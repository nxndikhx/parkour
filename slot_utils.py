import pandas as pd
from datetime import datetime, timedelta
import os

SLOT_CSV = "updated_parking_slots_dataset.csv"
USER_CSV = "user_authentication_dataset.csv"

def ensure_slot_csv():
    if not os.path.exists(SLOT_CSV):
        df = pd.DataFrame(columns=["Slot_ID", "Level", "Type", "Status", "Vehicle", "User_ID"])
        for i in range(1, 21):
            level = "L1" if i <= 10 else "L2"
            vehicle_type = "Electric" if i % 5 == 0 else "Normal"
            df.loc[i-1] = [f"SLOT{i}", level, vehicle_type, "Available", "", ""]
        df.to_csv(SLOT_CSV, index=False)

def get_all_slot_ids():
    if not os.path.exists(SLOT_CSV):
        ensure_slot_csv()
    df = pd.read_csv(SLOT_CSV)
    return df['Slot_ID'].unique().tolist()

def show_available_slots():
    if not os.path.exists(SLOT_CSV):
        ensure_slot_csv()
    df = pd.read_csv(SLOT_CSV)
    available = df[df["Status"] == "Available"][["Slot_ID", "Level", "Type"]]
    if available.empty:
        print("❌ No available slots right now.")
    else:
        print("🔓 Available Slots:\n")
        print(available.to_string(index=False))

def update_slot(slot_id, status, vehicle, user_id):
    df = pd.read_csv(SLOT_CSV)
    df.loc[df["Slot_ID"] == slot_id, ["Status", "Vehicle", "User_ID"]] = [status, vehicle, user_id]
    df.to_csv(SLOT_CSV, index=False)

def get_slot_level(slot_id):
    df = pd.read_csv(SLOT_CSV)
    level = df.loc[df["Slot_ID"] == slot_id, "Level"].values
    return level[0] if len(level) else "Unknown"

def release_expired_slots():
    if not os.path.exists(USER_CSV):
        return
    df = pd.read_csv(USER_CSV)
    now = datetime.now()
    changed = False
    for index, row in df.iterrows():
        if pd.notna(row.get("Booking_End")) and row["Booking_End"]:
            try:
                end = datetime.strptime(row["Booking_End"], "%Y-%m-%d %H:%M:%S")
                if now > end + timedelta(minutes=30):
                    slot = row.get("Prebooked_Slot")
                    if pd.notna(slot) and slot:
                        print(f"⌛ Booking expired. Releasing slot {slot}.")
                        update_slot(slot, "Available", "", "")
                        df.at[index, "Prebooked"] = "No"
                        df.at[index, "Prebooked_Slot"] = ""
                        df.at[index, "Booking_Start"] = ""
                        df.at[index, "Booking_End"] = ""
                        df.at[index, "Duration_Hrs"] = ""
                        changed = True
            except ValueError:
                continue
    if changed:
        df.to_csv(USER_CSV, index=False)

def assign_slot(vehicle_number, user_id, role="General"):
    if not os.path.exists(SLOT_CSV):
        ensure_slot_csv()
    df = pd.read_csv(SLOT_CSV)
    available = df[df["Status"] == "Available"]

    if available.empty:
        print("🚫 No slots available at the moment.")
        return None

    if role == "VIP":
        preferred = available[available["Level"] == "L1"]
        slot_id = preferred.iloc[0]["Slot_ID"] if not preferred.empty else available.iloc[0]["Slot_ID"]
    else:
        slot_id = available.iloc[0]["Slot_ID"]

    update_slot(slot_id, "Occupied", vehicle_number, user_id)
    level = get_slot_level(slot_id)
    print(f"✅ Slot {slot_id} assigned to vehicle {vehicle_number} on {level}.")
    return slot_id

def release_slot(vehicle_number):
    if not os.path.exists(SLOT_CSV):
        ensure_slot_csv()

    df = pd.read_csv(SLOT_CSV)
    index = df[df["Vehicle"] == vehicle_number].index

    if index.empty:
        print("⚠️ Vehicle not found in any occupied slot.")
        return None

    slot_id = df.loc[index[0], "Slot_ID"]
    update_slot(slot_id, "Available", "", "")
    print(f"🔓 Slot {slot_id} is now available.")
    return slot_id
