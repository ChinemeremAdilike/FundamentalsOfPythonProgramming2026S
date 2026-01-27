# Copyright (c) 2025 Ville Heikkiniemi
#
# This code is licensed under the MIT License.
# You are free to use, modify, and distribute this code,
# provided that the original copyright notice is retained.
#
# See LICENSE file in the project root for full license information.
#
# Modified by nnn according to given task

"""
A program that reads reservation data from a file
and prints them to the console using functions:

Reservation number: 123
Booker: Anna Virtanen
Date: 31.10.2025
Start time: 10.00
Number of hours: 2
Hourly rate: 19,95 €
Total price: 39,90 €
Paid: Yes
Venue: Meeting Room A
Phone: 0401234567
Email: anna.virtanen@example.com
"""

from datetime import datetime

# -------------------- FUNCTIONS --------------------

def print_reservation_number(reservation: list) -> None:
    number = int(reservation[0].strip())
    print(f"Reservation number: {number}")

def print_booker(reservation: list) -> None:
    print(f"Booker: {reservation[1].strip()}")

def print_date(reservation: list) -> None:
    date_obj = datetime.strptime(reservation[2].strip(), "%Y-%m-%d").date()
    print(f"Date: {date_obj.strftime('%d.%m.%Y')}")

def print_start_time(reservation: list) -> None:
    time_obj = datetime.strptime(reservation[3].strip(), "%H:%M").time()
    print(f"Start time: {time_obj.strftime('%H.%M')}")

def print_hours(reservation: list) -> None:
    hours = int(reservation[4].strip())
    print(f"Number of hours: {hours}")

def print_hourly_rate(reservation: list) -> None:
    rate = float(reservation[5].strip())
    price = f"{rate:.2f}".replace(".", ",")
    print(f"Hourly price: {price} €")

def print_total_price(reservation: list) -> None:
    hours = int(reservation[4].strip())
    rate = float(reservation[5].strip())
    total = hours * rate
    total_price = f"{total:.2f}".replace(".", ",")
    print(f"Total price: {total_price} €")

def print_paid(reservation: list) -> None:
    paid = reservation[6].strip() == "True"
    print(f"Paid: {'Yes' if paid else 'No'}")

def print_venue(reservation: list) -> None:
    print(f"Location: {reservation[7].strip()}")

def print_phone(reservation: list) -> None:
    print(f"Phone: {reservation[8].strip()}")

def print_email(reservation: list) -> None:
    print(f"Email: {reservation[9].strip()}")


# -------------------- MAIN --------------------

def main() -> None:
    # Absolute path to your reservations.txt file
    reservations_file = r"C:\Users\HP\GitRoot\FundamentalsOfPythonProgramming2026S\TaskB\reservations.txt"

    # Open file safely (removes BOM automatically)
    try:
        with open(reservations_file, "r", encoding="utf-8-sig") as f:
            content = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {reservations_file}")

    # -------------------- DEBUG --------------------
    print("DEBUG: file content read by Python:")
    print(repr(content))
    print("-" * 50)
    # -------------------- END DEBUG --------------------

    # Take the first non-empty line with '|' as reservation
    reservation = None
    for line in content.splitlines():
        line = line.strip()
        if line and "|" in line:
            reservation = [field.strip() for field in line.split("|")]
            break

    if reservation is None:
        raise ValueError("No reservation data found in reservations.txt")

    # -------------------- PRINT ALL FIELDS --------------------
    print_reservation_number(reservation)
    print_booker(reservation)
    print_date(reservation)
    print_start_time(reservation)
    print_hours(reservation)
    print_hourly_rate(reservation)
    print_total_price(reservation)
    print_paid(reservation)
    print_venue(reservation)
    print_phone(reservation)
    print_email(reservation)


if __name__ == "__main__":
    main()
