
# Copyright (c) 2025 Ville Heikkiniemi
#
# This code is licensed under the MIT License.
# You are free to use, modify, and distribute this code,
# provided that the original copyright notice is retained.
#
# See LICENSE file in the project root for full license information.

# Modified by nnn according to given task

"""
Program that reads reservation details from a file
and prints them to the console:

Reservation number: 123
Booker: Anna Virtanen
Date: 31.10.2025
Start time: 10.00
Number of hours: 2
Hourly price: 19,95 €
Total price: 39,90 €
Paid: Yes
Location: Meeting Room A
Phone: 0401234567
Email: anna.virtanen@example.com
"""

from datetime import datetime
import sys
from pathlib import Path


def main():
    # Define the file name directly in the code (must be in the same folder)
    reservations = "reservations.txt"
    file_path = Path(__file__).parent / reservations

    # Validate file existence (clear message helps grading/debugging)
    if not file_path.exists():
        print(f"Error: '{reservations}' not found next to this script.", file=sys.stderr)
        sys.exit(1)

    # Read all non-empty lines
    with file_path.open("r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    if not lines:
        print("No reservations found.")
        return

    # Process each reservation line
    for idx, reservation in enumerate(lines):
        # Split into columns
        parts = reservation.split("|")
        if len(parts) != 10:
            print(
                f"Error: Invalid column count ({len(parts)}) on line {idx + 1}. Expected 10.",
                file=sys.stderr,
            )
            sys.exit(1)

        # ---- Convert to correct data types ----
        try:
            reservation_number = int(parts[0].strip())
            booker = parts[1].strip()

            # Date and time (will raise if invalid -> good for data quality)
            day = datetime.strptime(parts[2].strip(), "%Y-%m-%d").date()
            finnish_day = day.strftime("%d.%m.%Y")

            start_time = datetime.strptime(parts[3].strip(), "%H:%M").time()
            finnish_time = start_time.strftime("%H.%M")

            hours = int(parts[4].strip())

            # Allow both 19.95 and 19,95 as input; standardize to float
            hourly_price = float(parts[5].replace(",", ".").strip())

            # Paid flag: accept True/False/true/false/1/0/yes/no
            paid_str = parts[6].strip().lower()
            if paid_str in ("true", "1", "yes", "y"):
                paid = True
            elif paid_str in ("false", "0", "no", "n"):
                paid = False
            else:
                raise ValueError(f"Invalid boolean value: {parts[6]!r}")

            resource = parts[7].strip()
            phone = parts[8].strip()
            email = parts[9].strip()

        except Exception as e:
            print(f"Error processing line {idx + 1}: {e}", file=sys.stderr)
            sys.exit(1)

        # ---- Compute totals and formatting ----
        total_price = hours * hourly_price

        def euro(x: float) -> str:
            # Format to two decimals and use comma as decimal separator
            return f"{x:.2f}".replace(".", ",")

        # ---- Print exactly as required ----
        print(f"Reservation number: {reservation_number}")
        print(f"Booker: {booker}")
        print(f"Date: {finnish_day}")
        print(f"Start time: {finnish_time}")
        print(f"Number of hours: {hours}")
        print(f"Hourly price: {euro(hourly_price)} €")
        print(f"Total price: {euro(total_price)} €")
        print(f"Paid: {'Yes' if paid else 'No'}")
        print(f"Location: {resource}")
        print(f"Phone: {phone}")
        print(f"Email: {email}")

        # Blank line between multiple reservations
        if idx < len(lines) - 1:
            print()


if __name__ == "__main__":
    main()
