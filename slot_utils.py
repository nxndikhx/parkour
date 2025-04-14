import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional
import pennylane as qml
import time
import math

SLOT_CSV = "updated_parking_slots_with_dimensions.csv"
USER_CSV = "user_authentication_dataset.csv"

# Vehicle type to dimensions (in meters)
CAR_DIMENSIONS = {
    "Compact": {"length": 3.6, "width": 1.6, "height": 1.4},
    "Sedan": {"length": 4.5, "width": 1.8, "height": 1.5},
    "SUV": {"length": 4.8, "width": 2.0, "height": 1.8},
    "Truck": {"length": 5.5, "width": 2.2, "height": 2.2}
}

def ensure_slot_csv():
    if not os.path.exists(SLOT_CSV):
        print("⚠️ Slot CSV not found. Please add the dataset.")
        return

def get_all_slot_ids():
    ensure_slot_csv()
    df = pd.read_csv(SLOT_CSV)
    return df['Slot_ID'].unique().tolist()

def get_available_slot_ids():
    ensure_slot_csv()
    df = pd.read_csv(SLOT_CSV)
    available_ids = df[df["Status"] == "Available"]["Slot_ID"].tolist()
    return available_ids

def show_available_slots():
    ensure_slot_csv()
    df = pd.read_csv(SLOT_CSV)
    available = df[df["Status"] == "Available"][["Slot_ID", "Level", "Type", "Max_Length", "Max_Width", "Max_Height"]]
    if available.empty:
        print("❌ No available slots right now.")
    else:
        print("🔓 Available Slots:\n")
        print(available.to_string(index=False))

def update_slot(slot_id: str, status: str, vehicle: str, user_id: str):
    df = pd.read_csv(SLOT_CSV)
    
    df["Status"] = df["Status"].astype(str)
    df["Vehicle"] = df["Vehicle"].astype(str)
    df["User_ID"] = df["User_ID"].astype(str)
    
    df.loc[df["Slot_ID"] == slot_id, ["Status", "Vehicle", "User_ID"]] = [status, vehicle, user_id]
    df.to_csv(SLOT_CSV, index=False)

def get_slot_level(slot_id: str) -> str:
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
        end_time_str = row.get("Booking_End")
        if pd.notna(end_time_str) and end_time_str:
            try:
                end = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")
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
            except Exception as e:
                print(f"⚠️ Error parsing date: {e}")
                continue

    if changed:
        df.to_csv(USER_CSV, index=False)

# Quantum RL setup
dev = qml.device("default.qubit", wires=3)

@qml.qnode(dev)
def qrl_circuit(params):
    qml.RY(params[0], wires=0)
    qml.RY(params[1], wires=1)
    qml.RY(params[2], wires=2)
    qml.CNOT(wires=[0, 1])
    qml.CNOT(wires=[1, 2])
    return qml.probs(wires=[0, 1, 2])

def choose_slot_quantum(slots, car_dims):
    scores = []
    for _, row in slots.iterrows():
        d_length = abs(row["Max_Length"] - car_dims["length"])
        d_width = abs(row["Max_Width"] - car_dims["width"])
        d_height = abs(row["Max_Height"] - car_dims["height"])
        params = [
            np.pi * d_length / 6,
            np.pi * d_width / 3,
            np.pi * d_height / 3
        ]
        probs = qrl_circuit(params)
        match_score = probs[0]  # Probability of |000⟩ = best match
        scores.append(match_score)

    slots["QRL_Score"] = scores
    best_slot = slots.sort_values(by="QRL_Score", ascending=False).iloc[0]
    return best_slot["Slot_ID"]

def assign_slot(vehicle_number: str, user_id: str, role: str = "General") -> Optional[str]:
    ensure_slot_csv()
    df = pd.read_csv(SLOT_CSV)
    available = df[df["Status"] == "Available"].copy()

    if available.empty:
        print("🚫 No slots available at the moment.")
        return None

    print("\n🚗 Choose your car type:")
    for idx, t in enumerate(CAR_DIMENSIONS.keys()):
        print(f"{idx+1}. {t}")
    choice = int(input("Enter choice (1–4): "))
    car_type = list(CAR_DIMENSIONS.keys())[choice - 1]
    car_dims = CAR_DIMENSIONS[car_type]

    suitable = available[
        (available["Max_Length"] >= car_dims["length"]) &
        (available["Max_Width"] >= car_dims["width"]) &
        (available["Max_Height"] >= car_dims["height"])
    ]

    if suitable.empty:
        print("❌ No slots can fit your vehicle’s dimensions.")
        return None

    selected_slot_id = choose_slot_quantum(suitable, car_dims)
    update_slot(selected_slot_id, "Occupied", vehicle_number, user_id)
    level = get_slot_level(selected_slot_id)
    print(f"✅ Slot assigned (via QRL): {selected_slot_id} (Level: {level})")
    return selected_slot_id

def release_slot(vehicle_number: str) -> Optional[str]:
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

def clear_all_slots():
    ensure_slot_csv()
    df = pd.read_csv(SLOT_CSV)
    df["Status"] = "Available"
    df["Vehicle"] = ""
    df["User_ID"] = ""
    df.to_csv(SLOT_CSV, index=False)
    print("🧹 All slots reset to Available.")

def compute_dim_diff(slot, dims):
    return math.sqrt(
        (slot["Max_Length"] - dims["length"]) ** 2 +
        (slot["Max_Width"] - dims["width"]) ** 2 +
        (slot["Max_Height"] - dims["height"]) ** 2
    )

def assign_slot_baseline(vehicle_number: str, user_id: str, role: str = "General") -> Optional[str]:
    ensure_slot_csv()
    df = pd.read_csv(SLOT_CSV)
    available = df[df["Status"] == "Available"].copy()

    if available.empty:
        print("🚫 No slots available at the moment (Baseline).")
        return None

    print("\n🚗 Choose your car type (Baseline):")
    for idx, t in enumerate(CAR_DIMENSIONS.keys()):
        print(f"{idx+1}. {t}")
    choice = int(input("Enter choice (1–4): "))
    car_type = list(CAR_DIMENSIONS.keys())[choice - 1]
    car_dims = CAR_DIMENSIONS[car_type]

    suitable = available[
        (available["Max_Length"] >= car_dims["length"]) &
        (available["Max_Width"] >= car_dims["width"]) &
        (available["Max_Height"] >= car_dims["height"])
    ]

    if suitable.empty:
        print("❌ No slots fit your vehicle dimensions (Baseline).")
        return None

    selected_slot = suitable.iloc[0]
    selected_slot_id = selected_slot["Slot_ID"]
    update_slot(selected_slot_id, "Occupied", vehicle_number, user_id)
    level = get_slot_level(selected_slot_id)
    print(f"✅ Slot assigned (Baseline): {selected_slot_id} (Level: {level})")
    return selected_slot_id
