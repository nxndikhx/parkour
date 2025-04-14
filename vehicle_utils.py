import pandas as pd
from datetime import datetime

USER_CSV = "user_authentication_dataset.csv"
SLOT_CSV = "updated_parking_slots_dataset.csv"

ROLE_PRIORITY = {
    "official": 1,
    "worker": 2,
    "intern": 3,
    "user": 4,
    "guest": 5
}

ROLE_RATE = {
    "official": 30,
    "worker": 40,
    "intern": 50,
    "user": 60,
    "guest": 70
}

def assign_slot(vehicle_number, user_id, role):
    df = pd.read_csv(SLOT_CSV)
    available = df[df["Status"].str.lower() == "available"]

    if available.empty:
        return "None"

    # Sort available slots based on custom logic (e.g., proximity, ID)
    available = available.sort_values(by="Slot_ID")

    # Choose slot based on role priority (officials get first available, guests last)
    selected_slot = available.iloc[0]["Slot_ID"] if not available.empty else "None"

    df.loc[df["Slot_ID"] == selected_slot, ["Status", "Vehicle", "User_ID"]] = ["Occupied", vehicle_number, user_id]
    df.to_csv(SLOT_CSV, index=False)
    return selected_slot

def calculate_bill(start_time_str, end_time_str, role):
    from datetime import datetime

    start = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
    end = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")
    total_minutes = (end - start).total_seconds() / 60

    hourly_rate = {
        "guest": 60,
        "user": 60,
        "official": 30,
        "worker": 30,
        "intern": 40
    }

    rate = hourly_rate.get(role, 60)
    total_bill = (total_minutes / 60) * rate
    return round(total_bill, 2)


def save_booking(user_id, slot, start, end, duration):
    df = pd.read_csv(USER_CSV)
    df.loc[df["User_ID"] == user_id, ["Prebooked", "Prebooked_Slot", "Booking_Start", "Booking_End", "Duration_Hrs"]] = [
        "Yes", slot, start, end, duration
    ]
    df.to_csv(USER_CSV, index=False)
