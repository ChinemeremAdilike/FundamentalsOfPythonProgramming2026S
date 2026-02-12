# Copyright (c) 2026 Chinemerem Adilike
# License: MIT
"""
Task E — Three Weeks of Electricity Consumption and Production (kWh) to a File

This program:
- reads hourly electricity data from week41.csv, week42.csv, week43.csv
- computes daily totals (Mon–Sun) by phase for consumption and production
- converts Wh → kWh
- formats using Finnish conventions (dd.mm.yyyy and comma decimal separator)
- writes a clear, user-friendly report into summary.txt

Your CSVs use semicolon ';' delimiter and headers:
  Time;Consumption phase 1 Wh;Consumption phase 2 Wh;Consumption phase 3 Wh;
       Production phase 1 Wh;Production phase 2 Wh;Production phase 3 Wh
"""

from __future__ import annotations

import csv
import os
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, date
from typing import Dict, List, Tuple


# --------------------- Data structures ---------------------

@dataclass
class HourRow:
    """One hourly measurement row (values in Wh)."""
    timestamp: datetime
    cons_wh: Tuple[float, float, float]
    prod_wh: Tuple[float, float, float]


@dataclass
class DaySummary:
    """Aggregated totals for one calendar day (values in kWh)."""
    day: date
    cons_kwh: Tuple[float, float, float]
    prod_kwh: Tuple[float, float, float]


# --------------------- Constants & helpers ---------------------

FINNISH_WEEKDAYS: Dict[int, str] = {
    0: "maanantai",
    1: "tiistai",
    2: "keskiviikko",
    3: "torstai",
    4: "perjantai",
    5: "lauantai",
    6: "sunnuntai",
}


def fi_number(value: float) -> str:
    """Format a float with two decimals using Finnish comma decimal separator."""
    return f"{value:.2f}".replace(".", ",")


def fi_date(d: date) -> str:
    """Format date as dd.mm.yyyy (Finnish convention)."""
    return f"{d.day:02d}.{d.month:02d}.{d.year}"


def parse_timestamp(s: str) -> datetime:
    """
    Parse timestamp preferring ISO-8601, with fallbacks for common variants.
    Accepts e.g. '2025-10-13T00:00:00', '2025-10-13 00:00', '2025-10-13'.
    """
    txt = s.strip()
    try:
        return datetime.fromisoformat(txt)
    except ValueError:
        pass
    for p in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(txt, p)
        except ValueError:
            continue
    raise ValueError(f"Unrecognized timestamp format: {s!r}")


def _normalize_header(h: str) -> str:
    """
    Normalize a CSV header for forgiving matching:
    - lowercase
    - remove spaces, dashes, brackets, parentheses, underscores
    - strip unit mentions like 'wh'
    """
    x = h.strip().lower()
    x = re.sub(r"[\s\-\[\]\(\)_]", "", x)
    x = x.replace("wh", "")  # ignore unit mentions
    return x


def _detect_columns(fieldnames: List[str]) -> Tuple[str, Dict[int, str], Dict[int, str]]:
    """
    Detect timestamp, consumption v1..v3, production v1..v3 columns.

    Returns:
        (timestamp_col, cons_cols, prod_cols)
        where cons_cols and prod_cols map phase 1..3 -> original header.
    """
    if not fieldnames:
        raise ValueError("CSV has no header row.")

    normalized = {fn: _normalize_header(fn) for fn in fieldnames}

    # Timestamp column
    ts_candidates = [
        fn for fn, nf in normalized.items()
        if "timestamp" in nf or "datetime" in nf or nf == "time" or nf == "date"
    ]
    if not ts_candidates:
        raise ValueError(
            "Could not detect timestamp column. Expected header like 'Time' or 'Timestamp'."
        )
    timestamp_col = ts_candidates[0]

    # Consumption/Production phase columns
    phase_re = re.compile(r".*([123]).*")
    cons_cols: Dict[int, str] = {}
    prod_cols: Dict[int, str] = {}

    for fn, nf in normalized.items():
        if "consumption" in nf or "cons" in nf or "kulutus" in nf:
            m = phase_re.match(nf)
            if m:
                p = int(m.group(1))
                if p in (1, 2, 3) and p not in cons_cols:
                    cons_cols[p] = fn
        if "production" in nf or "prod" in nf or "tuotanto" in nf:
            m = phase_re.match(nf)
            if m:
                p = int(m.group(1))
                if p in (1, 2, 3) and p not in prod_cols:
                    prod_cols[p] = fn

    missing_cons = [p for p in (1, 2, 3) if p not in cons_cols]
    missing_prod = [p for p in (1, 2, 3) if p not in prod_cols]
    if missing_cons or missing_prod:
        raise ValueError(
            "Could not detect all required phase columns.\n"
            f"Missing consumption phases: {missing_cons} | Missing production phases: {missing_prod}\n"
            "Expected headers like 'Consumption phase 1 Wh' and 'Production phase 1 Wh'."
        )

    return timestamp_col, cons_cols, prod_cols


# --------------------- Core functions ---------------------

def read_data(filename: str) -> List[HourRow]:
    """
    Reads a CSV file and returns rows as HourRow objects (Wh values preserved).
    Auto-detects delimiters ; , or tab, and tolerates flexible header names.
    """
    print(f"[read_data] Opening: {filename}", flush=True)

    with open(filename, "r", encoding="utf-8-sig", newline="") as f:
        # Detect delimiter from a small sample
        sample = f.read(2048)
        delim = ";" if sample.count(";") >= max(sample.count(","), sample.count("\t")) else ","
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=";,\t")
            delim = dialect.delimiter
        except csv.Error:
            pass

        print(f"[read_data] Detected delimiter: {repr(delim)}", flush=True)

        f.seek(0)
        reader = csv.DictReader(f, delimiter=delim)
        if reader.fieldnames is None:
            raise ValueError(f"CSV file {filename} is missing a header row.")

        print(f"[read_data] Headers: {reader.fieldnames}", flush=True)

        timestamp_col, cons_cols, prod_cols = _detect_columns(reader.fieldnames)
        print(f"[read_data] Timestamp column: {timestamp_col}", flush=True)
        print(f"[read_data] Consumption columns: {cons_cols}", flush=True)
        print(f"[read_data] Production columns: {prod_cols}", flush=True)

        rows: List[HourRow] = []
        for i, rec in enumerate(reader, start=2):  # header is line 1
            try:
                ts = parse_timestamp(rec[timestamp_col])

                def parse_wh(key: str) -> float:
                    txt = (rec.get(key, "") or "").strip().replace(",", ".")
                    return float(txt) if txt != "" else 0.0

                c1 = parse_wh(cons_cols[1]); c2 = parse_wh(cons_cols[2]); c3 = parse_wh(cons_cols[3])
                p1 = parse_wh(prod_cols[1]); p2 = parse_wh(prod_cols[2]); p3 = parse_wh(prod_cols[3])

                rows.append(HourRow(ts, (c1, c2, c3), (p1, p2, p3)))
            except Exception as e:
                raise ValueError(f"Error parsing {filename} at line {i}: {e}") from e

    print(f"[read_data] Parsed {len(rows)} hourly rows from {os.path.basename(filename)}", flush=True)
    return rows


def summarize_days(hour_rows: List[HourRow]) -> List[DaySummary]:
    """Aggregates hourly Wh measurements into daily kWh totals for each phase."""
    daily_wh: Dict[date, Dict[str, List[float]]] = defaultdict(lambda: {
        "cons": [0.0, 0.0, 0.0],
        "prod": [0.0, 0.0, 0.0],
    })

    for r in hour_rows:
        d = r.timestamp.date()
        for idx in range(3):
            daily_wh[d]["cons"][idx] += r.cons_wh[idx]
            daily_wh[d]["prod"][idx] += r.prod_wh[idx]

    summaries: List[DaySummary] = []
    for d in sorted(daily_wh.keys()):
        cons_kwh = tuple(v / 1000.0 for v in daily_wh[d]["cons"])
        prod_kwh = tuple(v / 1000.0 for v in daily_wh[d]["prod"])
        summaries.append(DaySummary(d, cons_kwh, prod_kwh))

    return summaries


def week_number_from_rows(hour_rows: List[HourRow]) -> int:
    """Determine ISO week number from the first row."""
    if not hour_rows:
        raise ValueError("Empty data when determining week number.")
    first_date = hour_rows[0].timestamp.date()
    return first_date.isocalendar()[1]


def format_week_section(week_no: int, day_summaries: List[DaySummary]) -> str:
    """Format one week's daily summaries into a readable section for the report."""
    title = f"Week {week_no} electricity consumption and production (kWh, by phase)\n"
    header1 = "Day         Date           Consumption [kWh]                 Production [kWh]\n"
    header2 = "                            v1       v2       v3              v1       v2       v3\n"
    sep = "---------------------------------------------------------------------------------\n"

    lines = [title, header1, header2, sep]
    for ds in day_summaries:
        wd = FINNISH_WEEKDAYS[ds.day.weekday()]
        date_str = fi_date(ds.day)
        c1, c2, c3 = (fi_number(v) for v in ds.cons_kwh)
        p1, p2, p3 = (fi_number(v) for v in ds.prod_kwh)
        line = (
            f"{wd:<12}{date_str:<14}"
            f"{c1:>8} {c2:>8} {c3:>8}      "
            f"{p1:>8} {p2:>8} {p3:>8}\n"
        )
        lines.append(line)
    lines.append("\n")
    return "".join(lines)


def write_report(
    path: str,
    week_sections: List[str],
    total_cons_kwh: Tuple[float, float, float],
    total_prod_kwh: Tuple[float, float, float],
) -> None:
    """Write the full report to a text file using UTF-8."""
    with open(path, "w", encoding="utf-8") as f:
        for section in week_sections:
            f.write(section)

        f.write("Overall totals for weeks 41–43 (kWh)\n")
        f.write("--------------------------------------\n")
        f.write("Consumption [kWh] by phase: ")
        f.write(f"v1={fi_number(total_cons_kwh[0])}  ")
        f.write(f"v2={fi_number(total_cons_kwh[1])}  ")
        f.write(f"v3={fi_number(total_cons_kwh[2])}\n")

        f.write("Production  [kWh] by phase: ")
        f.write(f"v1={fi_number(total_prod_kwh[0])}  ")
        f.write(f"v2={fi_number(total_prod_kwh[1])}  ")
        f.write(f"v3={fi_number(total_prod_kwh[2])}\n")

    print(f"[write_report] Report written to: {path}", flush=True)


def main() -> None:
    """
    Read week41/42/43 CSVs, compute daily summaries per week, and write summary.txt.
    """
    base = os.path.dirname(os.path.abspath(__file__))
    inputs = ["week41.csv", "week42.csv", "week43.csv"]
    input_paths = [os.path.join(base, x) for x in inputs]
    output_path = os.path.join(base, "summary.txt")

    print("[main] Starting Task E", flush=True)
    print(f"[main] Script folder: {base}", flush=True)

    all_week_sections: List[str] = []
    grand_cons = [0.0, 0.0, 0.0]
    grand_prod = [0.0, 0.0, 0.0]

    for csv_path in input_paths:
        print(f"[main] Processing file: {csv_path}", flush=True)
        if not os.path.exists(csv_path):
            raise FileNotFoundError(
                f"Input file not found: {csv_path}. "
                f"Ensure week41.csv, week42.csv, and week43.csv are in the same folder as task_e.py."
            )

        hour_rows = read_data(csv_path)
        print(f"[main] Rows loaded: {len(hour_rows)}", flush=True)
        week_no = week_number_from_rows(hour_rows)
        day_summaries = summarize_days(hour_rows)
        print(f"[main] Week {week_no}: {len(day_summaries)} days summarized", flush=True)

        for ds in day_summaries:
            for i in range(3):
                grand_cons[i] += ds.cons_kwh[i]
                grand_prod[i] += ds.prod_kwh[i]

        section = format_week_section(week_no, day_summaries)
        all_week_sections.append(section)

    write_report(
        output_path,
        all_week_sections,
        (grand_cons[0], grand_cons[1], grand_cons[2]),
        (grand_prod[0], grand_prod[1], grand_prod[2]),
    )

    print(f"[main] Done. Summary at: {output_path}", flush=True)


if __name__ == "__main__":
    # Show full traceback if anything goes wrong, so nothing is silent.
    try:
        main()
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise
