import os
import cv2
import time
import pytesseract
import easyocr
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import roboflow

# ======================= SETTINGS =======================
images_dir = "datasets/images"                # Folder with original images
annotations_dir = "datasets/annotations"      # Folder with XML files
cropped_dir = "cropped_plates"                # Output for cropped plates
os.makedirs(cropped_dir, exist_ok=True)

# 📍 Tesseract path (Windows only)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 🧠 Initialize EasyOCR
ocr = easyocr.Reader(['en'], gpu=False)

# =================== YOLOv11 LICENSE PLATE DETECTION =================

# Initialize Roboflow with API key
rf = roboflow.Roboflow(api_key="DDThNzGSx8rxGgPmk4Pn")

# Load YOLOv11 model version
project = rf.workspace().project("indian-number-plates-9oobq-jmyug")
model = project.version(2).model

def detect_license_plates_yolov11(image):
    # Run YOLOv11 model on the image
    predictions = model.predict(image).json()

    plates = []
    for prediction in predictions['predictions']:
        if prediction['class'] == 'license-plate':  # Only consider predictions for license plates
            xmin, ymin, xmax, ymax = prediction['bbox']
            plates.append((xmin, ymin, xmax, ymax))

    return plates

# ============== STEP 1: CROP PLATES + LABELS ==============
def crop_license_plates():
    count = 1
    labels = []

    for xml_file in os.listdir(annotations_dir):
        if not xml_file.endswith(".xml"):
            continue

        xml_path = os.path.join(annotations_dir, xml_file)
        tree = ET.parse(xml_path)
        root = tree.getroot()

        filename = root.find("filename").text
        image_path = os.path.join(images_dir, filename)

        if not os.path.exists(image_path):
            print(f"⚠️ Image {filename} not found.")
            continue

        image = cv2.imread(image_path)

        for obj in root.findall("object"):
            label = obj.find("name").text.lower()
            if label not in ["license", "plate", "license-plate"]:
                continue

            bbox = obj.find("bndbox")
            xmin = int(bbox.find("xmin").text)
            ymin = int(bbox.find("ymin").text)
            xmax = int(bbox.find("xmax").text)
            ymax = int(bbox.find("ymax").text)

            cropped = image[ymin:ymax, xmin:xmax]
            save_name = f"plate{count:03d}.jpg"
            save_path = os.path.join(cropped_dir, save_name)
            cv2.imwrite(save_path, cropped)

            # 👇 Extract license text from custom XML tag
            license_text_element = obj.find("license_text")
            license_text = license_text_element.text.strip().upper() if license_text_element is not None else "UNKNOWN"

            labels.append({"filename": save_name, "label": license_text})
            print(f"✅ Saved {save_name} with label: {license_text}")
            count += 1

    # 💾 Save labels to CSV
    df = pd.DataFrame(labels)
    df.to_csv("plate_labels.csv", index=False)
    print("🎯 All license plate crops completed and labels saved to plate_labels.csv.")

# ============= STEP 2: TESSERACT FALLBACK ================
def fallback_tesseract_ocr(image):
    print("📸 Running Tesseract OCR as fallback...")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    morph = cv2.morphologyEx(blur, cv2.MORPH_OPEN, kernel)
    morph = cv2.morphologyEx(morph, cv2.MORPH_CLOSE, kernel)

    thresh = cv2.adaptiveThreshold(morph, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 11, 2)

    config = '--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-'
    raw_text = pytesseract.image_to_string(thresh, config=config)
    cleaned_text = raw_text.strip().replace(" ", "").replace("\n", "").upper()

    print(f"🔍 Tesseract Raw Output: {cleaned_text}")
    return [cleaned_text] if cleaned_text else []

# ================= STEP 3: CAMERA SCAN ===================
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
        if len(cleaned) >= 5 and len(cleaned) <= 8 and confidence > 0.5:
            print(f"✅ Detected: {cleaned} (Confidence: {confidence:.2f})")
            detected_texts.append(cleaned)

    if detected_texts:
        return list(set(detected_texts))
    else:
        print("⚠️ EasyOCR failed. Falling back to Tesseract OCR...")
        return fallback_tesseract_ocr(frame)

# =================== MAIN FUNCTION ======================
def capture_and_scan_plate():
    return capture_plate()

# ==================== EXECUTION =========================
if __name__ == "__main__":
    print("📦 Step 1: Cropping license plate regions...")
    crop_license_plates()

    print("\n📸 Step 2: Capture plate via camera...")
    plates = capture_and_scan_plate()

    if plates:
        print("\n🔠 Final Detected Plates:")
        for plate in plates:
            print(f"➡️ {plate}")
    else:
        print("\n⚠️ No plates detected.")
