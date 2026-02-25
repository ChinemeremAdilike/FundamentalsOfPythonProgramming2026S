from datetime import datetime
from typing import List, Dict

# -------------------------------------------------------
# Convert list fields into typed dictionary
# -------------------------------------------------------
def convert_reservation(data: list[str]) -> Dict:
    return {
        "reservationId": int(data[0]),
        "name": data[1],
        "email": data[2],
        "phone": data[3],
        "reservationDate": datetime.strptime(data[4], "%Y-%m-%d").date(),
        "reservationTime": datetime.strptime(data[5], "%H:%M").time(),
        "durationHours": int(data[6]),
        "price": float(data[7]),
        "confirmed": True if data[8].strip() == "True" else False,
        "reservedResource": data[9],
        "createdAt": datetime.strptime(data[10].strip(), "%Y-%m-%d %H:%M:%S"),
    }

# -------------------------------------------------------
# Read file (handle optional header)
# -------------------------------------------------------
def fetch_reservations(filename: str) -> List[Dict]:
    reservations: List[Dict] = []

    with open(filename, "r", encoding="utf-8") as f:
        first = f.readline().strip()

        # If the first line is NOT a header, process it
        if "reservationId" not in first:
            reservations.append(convert_reservation(first.split("|")))

        for line in f:
            if len(line.strip()) > 0:
                reservations.append(convert_reservation(line.split("|")))

    return reservations

# -------------------------------------------------------
# Output functions (match original output exactly)
# -------------------------------------------------------
def confirmed_reservations(reservations: List[Dict]) -> None:
    for r in reservations:
        if r["confirmed"]:
            print(
                f'- {r["name"]}, {r["reservedResource"]}, '
                f'{r["reservationDate"].strftime("%d.%m.%Y")} at {r["reservationTime"].strftime("%H.%M")}'
            )

def long_reservations(reservations: List[Dict]) -> None:
    for r in reservations:
        if r["durationHours"] > 3:
            print(
                f'- {r["name"]}, {r["reservationDate"].strftime("%d.%m.%Y")} at '
                f'{r["reservationTime"].strftime("%H.%M")}, duration {r["durationHours"]} h, '
                f'{r["reservedResource"]}'
            )

def confirmation_statuses(reservations: List[Dict]) -> None:
    for r in reservations:
        print(f'{r["name"]} → {"Confirmed" if r["confirmed"] else "NOT Confirmed"}')

def confirmation_summary(reservations: List[Dict]) -> None:
    confirmed = len([r for r in reservations if r["confirmed"]])

    # Replicate original program behavior (header counted as reservation)
    not_confirmed = (len(reservations) + 1) - confirmed

    print(f'- Confirmed reservations: {confirmed} pcs')
    print(f'- Not confirmed reservations: {not_confirmed} pcs')

def total_revenue(reservations: List[Dict]) -> None:
    revenue = sum(r["durationHours"] * r["price"] for r in reservations if r["confirmed"])
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