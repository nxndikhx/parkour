import threading
import time

def schedule_terminal_reminder(vehicle_number, booking_end_time, delay_minutes=30):
    delay_seconds = delay_minutes * 60

    def reminder():
        print(f"\n⏰ Reminder: Booking for {vehicle_number} ended {delay_minutes} mins ago. Please vacate your slot if not done already.\n")

    timer = threading.Timer(delay_seconds, reminder)
    timer.start()
