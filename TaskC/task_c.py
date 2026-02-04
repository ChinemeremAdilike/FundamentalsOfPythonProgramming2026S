# Copyright (c) 2026 Ville Heikkiniemi, Luka Hietala, Luukas Kola
#
# This code is licensed under the MIT License.
# You are free to use, modify, and distribute this code,
# provided that the original copyright notice is retained.
#
# See LICENSE file in the project root for full license information.

# Modified by nnn according to given task

"""
A program that prints reservation information according to task requirements

The data structure and example data record:

reservationId | name | email | phone | reservationDate | reservationTime | durationHours | price | confirmed | reservedResource | createdAt
------------------------------------------------------------------------
201 | Moomin Valley | moomin@whitevalley.org | 0509876543 | 2025-11-12 | 09:00:00 | 2 | 18.50 | True | Forest Area 1 | 2025-08-12 14:33:20
int | str | str | str | date | time | int | float | bool | str | datetime

"""

from datetime import datetime, date, time

HEADERS = [
    "reservationId",
    "name",
    "email",
    "phone",
    "reservationDate",
    "reservationTime",
    "durationHours",
    "price",
    "confirmed",
    "reservedResource",
    "createdAt",
]


def convert_reservation_data(reservation: list) -> list:
    """
    Convert data types to meet program requirements

    Parameters:
     reservation (list): Unconverted reservation -> 11 columns

    Returns:
     converted (list): Converted data types in the order:
       int | str | str | str | date | time | int | float | bool | str | datetime
    """
    # Strip whitespace/newlines from each field
    fields = [x.strip() for x in reservation]

    # 1) reservationId: str -> int
    reservation_id = int(fields[0])

    # 2-4) name, email, phone: str
    name = fields[1]
    email = fields[2]
    phone = fields[3]

    # 5) reservationDate: "YYYY-MM-DD" -> datetime.date
    reservation_date = datetime.strptime(fields[4], "%Y-%m-%d").date()

    # 6) reservationTime: "HH:MM" or "HH:MM:SS" -> datetime.time
    try:
        reservation_time = datetime.strptime(fields[5], "%H:%M").time()
    except ValueError:
        reservation_time = datetime.strptime(fields[5], "%H:%M:%S").time()

    # 7) durationHours: str -> int
    duration_hours = int(fields[6])

    # 8) price: str -> float
    price = float(fields[7])

    # 9) confirmed: "True"/"False" -> bool
    confirmed = fields[8] == "True"

    # 10) reservedResource: str
    reserved_resource = fields[9]

    # 11) createdAt: "YYYY-MM-DD HH:MM:SS" -> datetime.datetime
    created_at = datetime.strptime(fields[10], "%Y-%m-%d %H:%M:%S")

    converted = [
        reservation_id,
        name,
        email,
        phone,
        reservation_date,
        reservation_time,
        duration_hours,
        price,
        confirmed,
        reserved_resource,
        created_at,
    ]
    return converted


def fetch_reservations(reservation_file: str) -> list:
    """
    Reads reservations from a file and returns the reservations converted
    You don't need to modify this function!

    Parameters:
     reservation_file (str): Name of the file containing the reservations

    Returns:
     reservations (list): Read and converted reservations
    """
    reservations = []
    with open(reservation_file, "r", encoding="utf-8") as f:
        for line in f:
            fields = line.split("|")
            reservations.append(convert_reservation_data(fields))
    return reservations


def confirmed_reservations(reservations: list[list]) -> None:
    """
    Print confirmed reservations:
    - Name, Reserved Resource, dd.mm.yyyy at hh.mm
    """
    for r in reservations:
        if r[8]:  # confirmed
            date_str = r[4].strftime("%d.%m.%Y")
            time_str = r[5].strftime("%H.%M")
            print(f"- {r[1]}, {r[9]}, {date_str} at {time_str}")


def long_reservations(reservations: list[list]) -> None:
    """
    Print long reservations (duration >= 3 h):
    - Name, dd.mm.yyyy at hh.mm, duration X h, Reserved Resource
    """
    for r in reservations:
        if r[6] >= 3:  # durationHours
            date_str = r[4].strftime("%d.%m.%Y")
            time_str = r[5].strftime("%H.%M")
            print(
                f"- {r[1]}, {date_str} at {time_str}, duration {r[6]} h, {r[9]}"
            )


def confirmation_statuses(reservations: list[list]) -> None:
    """
    Print confirmation statuses:
    Name → Confirmed / NOT Confirmed
    """
    for r in reservations:
        status = "Confirmed" if r[8] else "NOT Confirmed"
        print(f"{r[1]} \u2192 {status}")


def confirmation_summary(reservations: list[list]) -> None:
    """
    Print confirmation summary:
    - Confirmed reservations: X pcs
    - Not confirmed reservations: Y pcs
    """
    confirmed_count = sum(1 for r in reservations if r[8])
    not_confirmed_count = len(reservations) - confirmed_count
    print(f"- Confirmed reservations: {confirmed_count} pcs")
    print(f"- Not confirmed reservations: {not_confirmed_count} pcs")


def total_revenue(reservations: list[list]) -> None:
    """
    Print total revenue from confirmed reservations:
    Total revenue from confirmed reservations: xxx,yy €
    (price is hourly; revenue = durationHours * price)
    """
    total = sum(r[6] * r[7] for r in reservations if r[8])
    amount_str = f"{total:.2f}".replace(".", ",")
    print(f"Total revenue from confirmed reservations: {amount_str} €")


def main():
    """
    Prints reservation information according to requirements (PART B)
    """
    reservations = fetch_reservations("reservations.txt")

    # PART B outputs (1–5) in order
    print("1) Confirmed Reservations")
    confirmed_reservations(reservations)
    print()

    print("2) Long Reservations (≥ 3 h)")
    long_reservations(reservations)
    print()

    print("3) Reservation Confirmation Status")
    confirmation_statuses(reservations)
    print()

    print("4) Confirmation Summary")
    confirmation_summary(reservations)
    print()

    print("5) Total Revenue from Confirmed Reservations")
    total_revenue(reservations)


if __name__ == "__main__":
    main()