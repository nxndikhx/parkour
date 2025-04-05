# qr_generator.py

import qrcode
import os

def generate_qr(vehicle_number):
    # Create the directory if it doesn't exist
    qr_folder = "static\qr_codes"
    os.makedirs(qr_folder, exist_ok=True)

    # Generate and save the QR code
    img = qrcode.make(vehicle_number)
    img.save(f"{qr_folder}/{vehicle_number}.png")
