import pandas as pd

SLOT_CSV = "updated_parking_slots_dataset.csv"

def reset_all_slots():
    try:
        df = pd.read_csv(SLOT_CSV)
        df["Status"] = "Available"
        df["Vehicle"] = ""
        df["User_ID"] = ""
        df.to_csv(SLOT_CSV, index=False)
        print("✅ All parking slots have been reset and marked as available.")
    except FileNotFoundError:
        print("❌ Slot CSV file not found. Make sure the path is correct.")

if __name__ == "__main__":
    reset_all_slots()
