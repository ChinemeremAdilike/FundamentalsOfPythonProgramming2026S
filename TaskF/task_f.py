# Copyright (c) 2025 Chinemerem Adilike
# License: MIT

from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Iterable, Optional

# Resolve paths relative to this script's folder so it works no matter where you run it from
BASE_DIR: Path = Path(__file__).resolve().parent
CSV_FILENAME: Path = BASE_DIR / "2025.csv"
REPORT_FILENAME: Path = BASE_DIR / "report.txt"


@dataclass
class Measurement:
    """Represents one hourly measurement from the CSV file.

    Attributes:
        dt: Timestamp (timezone-aware) of the measurement as a datetime.
        consumption: Net consumption in kWh.
        production: Net production in kWh.
        temperature: Hourly average temperature in °C.
    """
    dt: datetime
    consumption: float
    production: float
    temperature: float


# ------------------------------------------------------------
# Formatting helpers (Finnish formatting rules)
# ------------------------------------------------------------

def fmt_date(d: date) -> str:
    """Format date as dd.mm.yyyy without zero-padding, e.g. 1.11.2025."""
    return f"{d.day}.{d.month}.{d.year}"


def _fmt_decimal(value: float) -> str:
    """Format a decimal with 2 decimals and a comma as decimal separator."""
    return f"{value:.2f}".replace(".", ",")


def fmt_kwh(value: float) -> str:
    """Format a kWh value according to Finnish rules."""
    return _fmt_decimal(value)


def fmt_temp(value: float) -> str:
    """Format a temperature value according to Finnish rules."""
    return _fmt_decimal(value)


# ------------------------------------------------------------
# Parsing helpers
# ------------------------------------------------------------

def _parse_float(text: str) -> float:
    """Parse a float that may use a comma as decimal separator."""
    s = (text or "").strip().replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return 0.0


def _parse_timestamp(text: str) -> datetime:
    """Parse an ISO-8601 timestamp (with or without timezone offset)."""
    s = (text or "").strip()
    try:
        # Supports e.g. "2025-01-01T00:00:00.000+02:00"
        return datetime.fromisoformat(s)
    except Exception:
        # As a last resort, try date-only fallback
        try:
            d = datetime.strptime(s[:10], "%Y-%m-%d").date()
            return datetime(d.year, d.month, d.day)
        except Exception:
            return datetime(1970, 1, 1)


# ------------------------------------------------------------
# CSV reading
# ------------------------------------------------------------

def read_data(filename: Path) -> List[Measurement]:
    """Read a semicolon-separated CSV and return measurements.

    Handles:
      - semicolon delimiter
      - a space after each semicolon (skipinitialspace=True)
      - header normalization (strip + lower)
      - decimal commas
      - ISO timestamps with timezone
    """
    rows: List[Measurement] = []

    try:
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=";", skipinitialspace=True)

            for raw in reader:
                # Normalize headers -> keys: stripped + lowercased
                norm: Dict[str, str] = { (k or "").strip().lower(): (v or "") for k, v in raw.items() }

                ts   = norm.get("time", "")
                cons = norm.get("consumption (net) kwh", "0")
                prod = norm.get("production (net) kwh", "0")
                temp = norm.get("daily average temperature", "0")

                rows.append(
                    Measurement(
                        dt=_parse_timestamp(ts),
                        consumption=_parse_float(cons),
                        production=_parse_float(prod),
                        temperature=_parse_float(temp),
                    )
                )
    except FileNotFoundError:
        print(f"\n[ERROR] File '{filename}' not found.\n")

    return rows


# ------------------------------------------------------------
# Input helpers
# ------------------------------------------------------------

def _input_date(prompt: str) -> date:
    """Ask user for dd.mm.yyyy and return a date object."""
    while True:
        s = input(prompt).strip()
        try:
            return datetime.strptime(s, "%d.%m.%Y").date()
        except ValueError:
            print("Invalid format. Please use dd.mm.yyyy (e.g., 13.10.2025).")


def _input_month(prompt: str = "Enter month number (1–12): ") -> int:
    """Ask for a month number 1..12 and return it."""
    while True:
        s = input(prompt).strip()
        if s.isdigit():
            m = int(s)
            if 1 <= m <= 12:
                return m
        print("Invalid month. Enter 1–12.")


# ------------------------------------------------------------
# Report creation
# ------------------------------------------------------------

def create_daily_report(data: List[Measurement]) -> List[str]:
    """Create a daily summary for a selected date range (inclusive)."""
    start = _input_date("Enter start date (dd.mm.yyyy): ")
    end = _input_date("Enter end date (dd.mm.yyyy): ")

    if end < start:
        print("End date is before start date. Swapping.")
        start, end = end, start

    selected = [m for m in data if start <= m.dt.date() <= end]

    total_cons = sum(m.consumption for m in selected)
    total_prod = sum(m.production for m in selected)
    temps = [m.temperature for m in selected]
    avg_temp: Optional[float] = (sum(temps) / len(temps)) if temps else None

    lines: List[str] = []
    lines.append("-" * 55)
    lines.append(f"Report for the period {fmt_date(start)}–{fmt_date(end)}")
    lines.append(f"- Total consumption: {fmt_kwh(total_cons)} kWh")
    lines.append(f"- Total production: {fmt_kwh(total_prod)} kWh")
    lines.append(
        f"- Average temperature: {fmt_temp(avg_temp)} °C"
        if avg_temp is not None else "- Average temperature: n/a"
    )

    return lines


def _group_by_day(rows: Iterable[Measurement]) -> Dict[date, List[Measurement]]:
    """Group measurements by calendar date."""
    groups: Dict[date, List[Measurement]] = defaultdict(list)
    for r in rows:
        groups[r.dt.date()].append(r)
    return groups


def create_monthly_report(data: List[Measurement]) -> List[str]:
    """Create a monthly summary for a selected month (2025 only).

    Average temperature is the average of **daily averages** (equal weight per day).
    """
    month = _input_month()

    month_rows = [m for m in data if m.dt.year == 2025 and m.dt.month == month]

    total_cons = sum(m.consumption for m in month_rows)
    total_prod = sum(m.production for m in month_rows)

    by_day = _group_by_day(month_rows)
    daily_avgs: List[float] = []
    for rows in by_day.values():
        daily_avgs.append(sum(r.temperature for r in rows) / len(rows))
    avg_temp: Optional[float] = (sum(daily_avgs) / len(daily_avgs)) if daily_avgs else None

    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    name = month_names[month - 1]

    lines: List[str] = []
    lines.append("-" * 55)
    lines.append(f"Report for the month: {name}")
    lines.append(f"- Total consumption: {fmt_kwh(total_cons)} kWh")
    lines.append(f"- Total production: {fmt_kwh(total_prod)} kWh")
    lines.append(
        f"- Average temperature: {fmt_temp(avg_temp)} °C"
        if avg_temp is not None else "- Average temperature: n/a"
    )

    return lines


def create_yearly_report(data: List[Measurement]) -> List[str]:
    """Create a full-year summary for 2025."""
    year_rows = [m for m in data if m.dt.year == 2025]

    total_cons = sum(m.consumption for m in year_rows)
    total_prod = sum(m.production for m in year_rows)
    temps = [m.temperature for m in year_rows]
    avg_temp: Optional[float] = (sum(temps) / len(temps)) if temps else None

    lines: List[str] = []
    lines.append("-" * 55)
    lines.append("Report for the year: 2025")
    lines.append(f"- Total consumption: {fmt_kwh(total_cons)} kWh")
    lines.append(f"- Total production: {fmt_kwh(total_prod)} kWh")
    lines.append(
        f"- Average temperature: {fmt_temp(avg_temp)} °C"
        if avg_temp is not None else "- Average temperature: n/a"
    )

    return lines


# ------------------------------------------------------------
# Output (console/file)
# ------------------------------------------------------------

def print_report_to_console(lines: List[str]) -> None:
    """Print the report lines to the console."""
    print()
    for ln in lines:
        print(ln)


def write_report_to_file(lines: List[str]) -> None:
    """Write (overwrite) report.txt with the given report lines."""
    with open(REPORT_FILENAME, "w", encoding="utf-8") as f:
        for ln in lines:
            f.write(ln + "\n")


# ------------------------------------------------------------
# Menus and main loop
# ------------------------------------------------------------

def show_main_menu() -> str:
    """Show the main menu and return the user's selection."""
    print("\nChoose a report type:")
    print("1) Daily summary for a date range")
    print("2) Monthly summary for one month")
    print("3) Full year 2025 summary")
    print("4) Exit")
    return input("Enter choice (1–4): ").strip()


def show_post_menu() -> str:
    """Show post-report actions and return the user's selection."""
    print("\nWhat next?")
    print("1) Write this report to report.txt")
    print("2) Create a new report")
    print("3) Exit")
    return input("Enter choice (1–3): ").strip()


def main() -> None:
    """Main controller: reads data, shows menus, generates and saves reports."""
    data = read_data(CSV_FILENAME)

    while True:
        choice = show_main_menu()

        if choice == "1":
            report = create_daily_report(data)
        elif choice == "2":
            report = create_monthly_report(data)
        elif choice == "3":
            report = create_yearly_report(data)
        elif choice == "4":
            print("Goodbye!")
            return
        else:
            print("Invalid choice.")
            continue

        print_report_to_console(report)

        while True:
            post = show_post_menu()
            if post == "1":
                write_report_to_file(report)
                print(f"Saved to {REPORT_FILENAME}.")
            elif post == "2":
                break  # back to main menu
            elif post == "3":
                print("Goodbye!")
                return
            else:
                print("Invalid choice.")


if __name__ == "__main__":
    main()