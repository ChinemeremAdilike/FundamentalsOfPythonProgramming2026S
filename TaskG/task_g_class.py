from datetime import datetime, date, time
from typing import List

# -------------------------------------------------------
# Reservation class
# -------------------------------------------------------
class Reservation:
    def __init__(
        self,
        reservationId: int,
        name: str,
        email: str,
        phone: str,
        reservationDate: date,
        reservationTime: time,
        durationHours: int,
        price: float,
        confirmed: bool,
        reservedResource: str,
        createdAt: datetime,
    ):
        self.reservationId = reservationId
        self.name = name
        self.email = email
        self.phone = phone
        self.reservationDate = reservationDate
        self.reservationTime = reservationTime
        self.durationHours = durationHours
        self.price = price
        self.confirmed = confirmed
        self.reservedResource = reservedResource
        self.createdAt = createdAt

    def is_confirmed(self) -> bool:
        return self.confirmed

    def is_long(self) -> bool:
        return self.durationHours > 3

    def total_price(self) -> float:
        return self.durationHours * self.price

# -------------------------------------------------------
# Convert CSV row -> Reservation object
# -------------------------------------------------------
def convert_reservation(data: list[str]) -> Reservation:
    return Reservation(
        reservationId=int(data[0]),
        name=data[1],
        email=data[2],
        phone=data[3],
        reservationDate=datetime.strptime(data[4], "%Y-%m-%d").date(),
        reservationTime=datetime.strptime(data[5], "%H:%M").time(),
        durationHours=int(data[6]),
        price=float(data[7]),
        confirmed=True if data[8].strip() == "True" else False,
        reservedResource=data[9],
        createdAt=datetime.strptime(data[10].strip(), "%Y-%m-%d %H:%M:%S"),
    )

# -------------------------------------------------------
# Read file (detect header automatically)
# -------------------------------------------------------
def fetch_reservations(filename: str) -> List[Reservation]:
    reservations: List[Reservation] = []

    with open(filename, "r", encoding="utf-8") as f:
        first_line = f.readline().strip()

        if "reservationId" not in first_line:
            reservations.append(convert_reservation(first_line.split("|")))

        for line in f:
            line = line.strip()
            if line:
                reservations.append(convert_reservation(line.split("|")))

    return reservations

# -------------------------------------------------------
# Output functions (identical to original output)
# -------------------------------------------------------
def confirmed_reservations(reservations: List[Reservation]) -> None:
    for r in reservations:
        if r.is_confirmed():
            print(
                f'- {r.name}, {r.reservedResource}, '
                f'{r.reservationDate.strftime("%d.%m.%Y")} at {r.reservationTime.strftime("%H.%M")}'
            )

def long_reservations(reservations: List[Reservation]) -> None:
    for r in reservations:
        if r.is_long():
            print(
                f'- {r.name}, {r.reservationDate.strftime("%d.%m.%Y")} at '
                f'{r.reservationTime.strftime("%H.%M")}, duration {r.durationHours} h, '
                f'{r.reservedResource}'
            )

def confirmation_statuses(reservations: List[Reservation]) -> None:
    for r in reservations:
        print(f'{r.name} → {"Confirmed" if r.is_confirmed() else "NOT Confirmed"}')

def confirmation_summary(reservations: List[Reservation]) -> None:
    confirmed = len([r for r in reservations if r.is_confirmed()])

    # Match original buggy behavior:
    not_confirmed = (len(reservations) + 1) - confirmed

    print(f'- Confirmed reservations: {confirmed} pcs')
    print(f'- Not confirmed reservations: {not_confirmed} pcs')

def total_revenue(reservations: List[Reservation]) -> None:
    revenue = sum(r.total_price() for r in reservations if r.is_confirmed())
    print(f'Total revenue from confirmed reservations: {revenue:.2f} €'.replace('.', ','))

# -------------------------------------------------------
# Main
# -------------------------------------------------------
def main():
    reservations = fetch_reservations("reservations.txt")

    print("1) Confirmed Reservations")
    confirmed_reservations(reservations)

    print("2) Long Reservations (≥ 3 h)")
    long_reservations(reservations)

    print("3) Reservation Confirmation Status")
    confirmation_statuses(reservations)

    print("4) Confirmation Summary")
    confirmation_summary(reservations)

    print("5) Total Revenue from Confirmed Reservations")
    total_revenue(reservations)

if __name__ == "__main__":
    main()
