#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Task D - Weekly Electricity Consumption and Production (kWh) in the Console.

Reads hourly data from week42.csv (Wh), groups by day (Mon–Sun), converts to kWh,
and prints a clear table with Finnish weekday names and Finnish number formatting.

Expected folder:
TaskD/
├─ task_d.py
└─ week42.csv
"""

from __future__ import annotations

import csv
from collections import defaultdict, OrderedDict
from dataclasses import dataclass
from datetime import datetime, date
from typing import Dict, List, Tuple


# ===================== Data structures =====================

@dataclass(frozen=True)
class Row:
    """
    One CSV row of hourly values.

    timestamp: datetime of measurement.
    consumption_wh: (v1, v2, v3) in Wh.
    production_wh: (v1, v2, v3) in Wh.
    """
    timestamp: datetime
    consumption_wh: Tuple[int, int, int]
    production_wh: Tuple[int, int, int]


# ===================== Utilities =====================

def parse_timestamp(text: str) -> datetime:
    """Parse a timestamp string into a datetime."""
    s = text.strip().replace("Z", "")
    try:
        return datetime.fromisoformat(s)  # e.g. 2025-10-13T00:00:00
    except ValueError:
        pass

    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M", "%d.%m.%Y %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue

    raise ValueError(f"Unrecognized timestamp format: {text!r}")


def finnish_weekday_name(d: date) -> str:
    """Return Finnish weekday name (capitalized) for a given date."""
    names = ["Maanantai", "Tiistai", "Keskiviikko",
             "Torstai", "Perjantai", "Lauantai", "Sunnuntai"]
    return names[d.weekday()]


def format_date_fi(d: date) -> str:
    """Format a date as dd.mm.yyyy (Finnish style)."""
    return d.strftime("%d.%m.%Y")


def kwh_str_from_wh(total_wh: float) -> str:
    """Convert Wh to kWh string with two decimals and comma decimal separator."""
    kwh = total_wh / 1000.0
    return f"{kwh:.2f}".replace(".", ",")


# ===================== Core logic =====================

def read_data(filename: str) -> List[Row]:
    """
    Read the CSV file and return parsed rows.

    Expected columns by position:
        0: timestamp
        1..3: consumption (Wh) v1, v2, v3
        4..6: production (Wh) v1, v2, v3
    """
    rows: List[Row] = []

    # Use utf-8-sig to tolerate BOM; sniff delimiter (; or , or tab)
    with open(filename, "r", encoding="utf-8-sig", newline="") as f:
        sample = f.read(4096)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=[",", ";", "\t"])
            delimiter = dialect.delimiter
        except csv.Error:
            delimiter = ";" if ";" in sample else ","

        reader = csv.reader(f, delimiter=delimiter)

        for raw in reader:
            if not raw or all(not c.strip() for c in raw):
                continue

            # Skip header if first cell isn't a timestamp
            try:
                ts = parse_timestamp(raw[0])
            except ValueError:
                continue

            if len(raw) < 7:
                raise ValueError(
                    f"Expected at least 7 columns, got {len(raw)} in row: {raw}"
                )

            def to_wh(s: str) -> int:
                # Accept '', ints, floats, decimal commas; normalize to int Wh
                s = s.strip().replace("\u00A0", " ")  # non‑breaking space
                if s == "":
                    return 0
                return int(round(float(s.replace(",", "."))))

            cons = tuple(to_wh(x) for x in raw[1:4])  # v1..v3
            prod = tuple(to_wh(x) for x in raw[4:7])  # v1..v3

            rows.append(Row(ts, (cons[0], cons[1], cons[2]),
                                (prod[0], prod[1], prod[2])))

    return rows


def daily_totals_wh(
    rows: List[Row],
) -> "OrderedDict[date, Dict[str, Tuple[float, float, float]]]":
    """Group rows by date and sum Wh per day and per phase."""
    acc: Dict[date, Dict[str, List[float]]] = defaultdict(
        lambda: {"cons": [0.0, 0.0, 0.0], "prod": [0.0, 0.0, 0.0]}
    )

    for r in rows:
        d = r.timestamp.date()
        for i in range(3):
            acc[d]["cons"][i] += float(r.consumption_wh[i])
            acc[d]["prod"][i] += float(r.production_wh[i])

    ordered: "OrderedDict[date, Dict[str, Tuple[float, float, float]]]" = OrderedDict()
    for d in sorted(acc.keys()):
        ordered[d] = {
            "cons": (acc[d]["cons"][0], acc[d]["cons"][1], acc[d]["cons"][2]),
            "prod": (acc[d]["prod"][0], acc[d]["prod"][1], acc[d]["prod"][2]),
        }
    return ordered


def print_report(
    daily: "OrderedDict[date, Dict[str, Tuple[float, float, float]]]"
) -> None:
    """Print the weekly report to the console."""
    if not daily:
        print("No data found.")
        return

    first_day = next(iter(daily.keys()))
    iso_week = first_day.isocalendar().week

    print(f"Week {iso_week} electricity consumption and production (kWh, by phase)")
    print()
    print("Day           Date         Consumption [kWh]                 Production [kWh]")
    print("             (dd.mm.yyyy)  v1        v2        v3             v1       v2       v3")
    print("-" * 75)

    for d, vals in daily.items():
        day_name = finnish_weekday_name(d)
        date_str = format_date_fi(d)

        cons = vals["cons"]
        prod = vals["prod"]

        cons_v = [kwh_str_from_wh(x) for x in cons]
        prod_v = [kwh_str_from_wh(x) for x in prod]

        print(
            f"{day_name:<13} {date_str:<12} "
            f"{cons_v[0]:>8}  {cons_v[1]:>8}  {cons_v[2]:>8}       "
            f"{prod_v[0]:>8} {prod_v[1]:>8} {prod_v[2]:>8}"
        )


def main() -> None:
    """Read week42.csv, compute daily totals (Wh) and print kWh report (FI formatting)."""
    filename = "week42.csv"
    rows = read_data(filename)

    # (Optional) quick sanity print; comment out before submission
    # print(f"Rows read: {len(rows)}")  # Expect 168

    daily = daily_totals_wh(rows)
    print_report(daily)


if __name__ == "__main__":
    main()