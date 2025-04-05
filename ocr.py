import cv2
import easyocr
import time
import re
import pytesseract
import numpy as np
import os

# ✅ Set path if Tesseract is not in PATH
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# ✅ Initialize EasyOCR
reader = easyocr.Reader(['en'], gpu=False)

# ✅ Indian license plate format
def is_valid_plate(text):
    pattern = r'^[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}$'
    return re.match(pattern, text.upper())

# ✅ Tesseract fallback
def fallback_tesseract_ocr(image):
    print("📸 Running Tesseract OCR as fallback...")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    config = '--psm 6'
    tesseract_text = pytesseract.image_to_string(thresh, config=config)

    cleaned_text = tesseract_text.strip().replace(" ", "").replace("\n", "").upper()
    print(f"🔍 Tesseract Output: {cleaned_text}")
    return [cleaned_text] if is_valid_plate(cleaned_text) else []

# ✅ Capture and scan license plate
def capture_plate(cam_id=1, retries=3):
    print("🎥 Accessing camera...")

    cap = None
    attempt = 0
    while attempt < retries:
        cap = cv2.VideoCapture(cam_id)
        if cap.isOpened():
            print(f"✅ Camera 1 opened (attempt {attempt + 1})")
            break
        else:
            print(f"⚠️ Attempt {attempt + 1}: Failed to open camera.")
            attempt += 1
            time.sleep(1)

    if not cap or not cap.isOpened():
        print("❌ All attempts failed. Is Camo running and set to Camera 1?")
        return []

    print("⏳ Capturing frame in 5 seconds. Please position vehicle plate in view.")
    time.sleep(5)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("❌ Failed to capture frame.")
        return []

    print("🔍 Running EasyOCR...")
    results = reader.readtext(frame)

    detected_plates = []
    for (bbox, text, prob) in results:
        clean_text = text.strip().upper().replace(" ", "")
        if len(clean_text) >= 6 and prob > 0.5 and is_valid_plate(clean_text):
            print(f"✅ Detected: {clean_text} with confidence {prob:.2f}")
            detected_plates.append(clean_text)

    if detected_plates:
        return list(set(detected_plates))
    else:
        print("⚠️ EasyOCR failed. Falling back to Tesseract OCR...")
        return fallback_tesseract_ocr(frame)
