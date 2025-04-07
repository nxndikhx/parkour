import cv2
import time
import pytesseract
import easyocr
import numpy as np

# ✅ Set path if Tesseract is not in PATH
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# ✅ Initialize EasyOCR instead of PaddleOCR
ocr = easyocr.Reader(['en'], gpu=False)

# ✅ Tesseract fallback
def fallback_tesseract_ocr(image):
    print("📸 Running Tesseract OCR as fallback...")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # ➕ Morphological Opening to remove noise
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    morph = cv2.morphologyEx(blur, cv2.MORPH_OPEN, kernel)

    # ➕ Morphological Closing to connect broken characters
    morph = cv2.morphologyEx(morph, cv2.MORPH_CLOSE, kernel)

    # ➕ Adaptive Thresholding for better contrast
    thresh = cv2.adaptiveThreshold(morph, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                    cv2.THRESH_BINARY, 11, 2)

    config = '--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    raw_text = pytesseract.image_to_string(thresh, config=config)
    cleaned_text = raw_text.strip().replace(" ", "").replace("\n", "").upper()

    print(f"🔍 Tesseract Raw Output: {cleaned_text}")
    return [cleaned_text] if cleaned_text else []

# ✅ Capture and scan license plate
def capture_plate(cam_id=1, retries=3):
    print("🎥 Accessing camera...")

    cap = None
    attempt = 0
    while attempt < retries:
        cap = cv2.VideoCapture(cam_id)
        if cap.isOpened():
            print(f"✅ Camera {cam_id} opened (attempt {attempt + 1})")
            break
        else:
            print(f"⚠️ Attempt {attempt + 1}: Failed to open camera.")
            attempt += 1
            time.sleep(1)

    if not cap or not cap.isOpened():
        print("❌ All attempts failed. Is the camera connected and working?")
        return []

    print("⏳ Capturing frame in 5 seconds. Please position the plate in view.")
    time.sleep(5)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("❌ Failed to capture frame.")
        return []

    print("🔍 Running EasyOCR...")
    results = ocr.readtext(frame)

    detected_texts = []
    for (bbox, text, confidence) in results:
        cleaned = text.strip().upper().replace(" ", "")
        if len(cleaned) >= 4 and confidence > 0.5:
            print(f"✅ Detected: {cleaned} (Confidence: {confidence:.2f})")
            detected_texts.append(cleaned)

    if detected_texts:
        return list(set(detected_texts))
    else:
        print("⚠️ EasyOCR failed. Falling back to Tesseract OCR...")
        return fallback_tesseract_ocr(frame)

# ✅ External function to use the scanner
def capture_and_scan_plate():
    return capture_plate()
