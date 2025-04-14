from datetime import datetime, timedelta

# 🧠 Core modules
from user_auth import register_user, login_user
from ocr import capture_and_scan_plate
from slot_utils import assign_slot, release_slot, show_available_slots, get_available_slot_ids, clear_all_slots
from qr_generator import generate_qr
from vehicle_utils import calculate_bill
from alerts import schedule_terminal_reminder

# 🔬 AI Optimization Module
from ai_optimization import qaoa_optimize, real_world_allocate

vehicle_types = ["Compact", "Sedan", "SUV", "Truck"]
role_options = {
    "1": "guest",
    "2": "user",
    "3": "official",
    "4": "worker",
    "5": "intern"
}

def choose_role():
    print("\n🧑 Choose your role:")
    for k, v in role_options.items():
        print(f"{k}. {v.capitalize()}")
    choice = input("Enter choice (1–5): ").strip()
    return role_options.get(choice, "guest")

def handle_role_based_booking(user_data, vehicle_number):
    role = user_data.get("Role", "user")
    now = datetime.now()

    if role in ["user", "guest"]:
        try:
            duration = int(input("⏳ Enter parking duration (in minutes): "))
            booking_end = now + timedelta(minutes=duration)
            schedule_terminal_reminder(vehicle_number, booking_end, delay_minutes=30)
            print(f"⏰ Reminder set for {booking_end.strftime('%H:%M:%S')}")
        except ValueError:
            print("⚠️ Invalid input for duration.")

    elif role in ["official", "worker"]:
        print("📅 Choose a predefined slot:")
        time_slots = {
            "1": ("09:00", "12:00"),
            "2": ("12:01", "15:00"),
            "3": ("15:01", "18:00"),
            "4": ("18:01", "21:00"),
            "5": ("21:01", "00:00"),
            "6": ("00:01", "03:00"),
            "7": ("03:01", "06:00"),
            "8": ("06:01", "09:00")
        }

        for key, (start, end) in time_slots.items():
            print(f"{key}. {start} - {end}")
        print("9. Custom Time")

        slot_choice = input("Select option (1–9): ")

        if slot_choice in time_slots:
            start_str, end_str = time_slots[slot_choice]
        else:
            start_str = input("Start time (HH:MM): ")
            end_str = input("End time (HH:MM): ")

        today = now.strftime('%Y-%m-%d')
        start = datetime.strptime(f"{today} {start_str}", "%Y-%m-%d %H:%M")
        end = datetime.strptime(f"{today} {end_str}", "%Y-%m-%d %H:%M")
        duration = int((end - start).total_seconds() // 60)
        print(f"⏰ Slot booked from {start_str} to {end_str} ({duration} minutes)")

    elif role == "intern":
        try:
            hours = int(input("⌛ How many hours? "))
            booking_end = now + timedelta(hours=hours)
            print(f"🕒 Slot booked for {hours} hour(s). Ends at {booking_end.strftime('%H:%M')}")
        except ValueError:
            print("⚠️ Invalid input.")

def main():
    print("🚗 Welcome to Parkour - Smart Parking System")

    while True:
        print("\n1. Register\n2. Login\n3. Guest Entry\n4. Exit")
        choice = input("Select an option: ")

        user_data = {}
        vehicle_number = ""

        if choice == "1":
            user_data = register_user()
            # No need to ask for role again after registration, it's set already
            print(f"✅ Registered successfully with Role: {user_data['Role']}")
            print("📸 Scanning your vehicle plate...")
            vehicle_number = capture_and_scan_plate()

        elif choice == "2":
            user_data = login_user()
            if not user_data:
                continue
            print("📸 Scanning your vehicle plate...")
            vehicle_number = capture_and_scan_plate()

        elif choice == "3":
            print("Guest Login Selected.")
            user_data = {
                "User_ID": f"guest_{datetime.now().strftime('%H%M%S')}",
                "Name": "Guest",
                "Phone": input("📞 Enter phone number: "),
                "Role": "guest"
            }
            print("📸 Scanning your vehicle plate...")
            vehicle_number = capture_and_scan_plate()

        elif choice == "4":
            print("👋 Thank you for using Parkour!")
            break

        else:
            print("❌ Invalid option.")
            continue

        print(f"\n👋 Welcome, {user_data['Name']}!")

        if not vehicle_number:
            vehicle_number = input("Enter vehicle number: ").upper()
        elif isinstance(vehicle_number, list):
            print("📋 Multiple plates detected:")
            for i, plate in enumerate(vehicle_number, 1):
                print(f"{i}. {plate}")
            choice = input("Select plate number (or press Enter for first): ")
            if choice.isdigit() and 1 <= int(choice) <= len(vehicle_number):
                vehicle_number = vehicle_number[int(choice) - 1].upper()
            else:
                vehicle_number = vehicle_number[0].upper()

        while True:
            print("\n1. Book Slot\n2. Release Slot\n3. Show Available Slots\n4. Rescan Plate\n5. Logout\n6. Clear All Slots")
            action = input("Choose action: ")

            if action == "1":
                role = user_data.get("Role", "user")
                print("⚙️ Optimizing slot using AI algorithms...")

                available_slot_ids = get_available_slot_ids()

                if not available_slot_ids:
                    print("❌ No slots available!")
                    continue

                if role in ["official", "worker"]:
                    selected_slot = real_world_allocate(available_slot_ids)
                else:
                    top_slots = qaoa_optimize(available_slot_ids)
                    selected_slot = top_slots[0] if top_slots else available_slot_ids[0]

                print(f"✅ AI Assigned Slot: {selected_slot}")

                assigned = assign_slot(selected_slot, vehicle_number, user_data.get("User_ID", "unknown"))
                if assigned:
                    generate_qr(vehicle_number)
                    if "L1" in selected_slot:
                        print("🅿️ Ground Floor (L1)")
                    elif "L2" in selected_slot:
                        print("🅿️ First Floor (L2)")
                    elif "L3" in selected_slot:
                        print("🅿️ Second Floor (L3)")
                    handle_role_based_booking(user_data, vehicle_number)
                else:
                    print("❌ Failed to assign slot.")

            elif action == "2":
                print(f"📤 Releasing slot for vehicle {vehicle_number}")
                start_time = input("Enter start time (HH:MM): ")
                end_time = input("Enter end time (HH:MM): ")
                try:
                    today = datetime.today().strftime('%Y-%m-%d')
                    start = datetime.strptime(f"{today} {start_time}", "%Y-%m-%d %H:%M")
                    end = datetime.strptime(f"{today} {end_time}", "%Y-%m-%d %H:%M")
                    bill = calculate_bill(start, end, role=user_data.get("Role", "user"))
                    print(f"💸 Total bill: ₹{bill}")
                    release_slot(vehicle_number)
                except Exception as e:
                    print(f"⚠️ Error: {e}")

            elif action == "3":
                show_available_slots()

            elif action == "4":
                print("🔁 Rescanning plate...")
                vehicle_number = capture_and_scan_plate()

            elif action == "5":
                print("👋 Logging out...")
                break

            elif action == "6":
                clear_all_slots()

            else:
                print("❌ Invalid action.")

if __name__ == "__main__":
    main()
