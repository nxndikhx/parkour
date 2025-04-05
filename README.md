<h1 align="center">🚗 Parkour: AI-Powered Smart Parking System 🚗</h1>

<p align="center"><em>A modular parking solution that blends AI, Computer Vision, and optimization algorithms to revolutionize the way we park.</em></p>
<p align="center"><strong>Book. Verify. Park. All in one seamless experience.</strong></p>

---

## 🧠 Overview

**Parkour** is a Python-based smart parking system with a terminal UI and a range of intelligent features. Designed with modularity and scalability in mind, it leverages Artificial Intelligence, OCR, Computer Vision, and Quantum-inspired algorithms to offer an efficient and secure parking experience for users and admins alike.

---

## 🚀 Features

### 🔐 Authentication
- **QR Code-Based Login/Registration**: Fast and secure terminal-based QR authentication.
- **Role-Based Access**: Users, interns, officials/workers — each with customized slot policies and pricing.

### 🕐 Smart Prebooking
- Select **date**, **AM/PM**, **hour:minute**, and **duration**.
- System displays available slots dynamically.
- Includes **flexitime** and **auto-cancellation**.

### ♻️ Slot Management
- **Slot Change Requests**: Request change through attendants.
- **Dynamic Pricing**: Based on role (e.g., ₹60/hr for users, ₹30/hr for workers).
- **Fixed Time Slots**: For officials/workers (e.g., 9am–12pm, etc).

### 🎥 CCTV-Based Validation
- CCTV-only vehicle check — **no costly sensors**.
- Ensures parking integrity by comparing real-time footage with booking data.

### 🔍 License Plate Recognition
- Uses **YOLO-based ANPR** (Automatic Number Plate Recognition) and **EasyOCR** to extract vehicle numbers for validation.

### 🧠 AI & Quantum Optimization
- **Unauthorized Parking Detection**: Uses CNN for identifying illegal parking behavior.
- **Slot Optimization** using:
  - QRL (Quantum Reinforcement Learning)
  - QAOA (Quantum Approximate Optimization Algorithm)
  - Dijkstra's Algorithm
  - GA (Genetic Algorithm)
  - PSO (Particle Swarm Optimization)

---

## 🗂️ Project Structure
<pre>
├── authentication/
├── booking/
├── ocr_license_plate/
├── optimization/
├── qr_module/
├── slot_allocation/
├── vehicle_verification/
├── updated_parking_slots_dataset.csv
├── user_authentication_dataset.csv
├── vehicle_information_dataset.csv
</pre>


---

## 📦 Datasets Used

1. **updated_parking_slots_dataset.csv** – Real-time slot data.
2. **user_authentication_dataset.csv** – User login and QR code records.
3. **vehicle_information_dataset.csv** – License plate, vehicle type, and user details.

---

## 🛠️ Tech Stack

- **Python** (core logic)
- **YOLOv5 + EasyOCR** (for number plate recognition)
- **OpenCV** (for CCTV footage analysis)
- **Gupshup API** (for WhatsApp integration)
- **NetworkX** / **Graph Algorithms** (for navigation)
- **Quantum Optimization Libraries** (Qiskit, Pennylane, or equivalents)

---

## 📈 Demo Roles & Pricing Breakdown

| Role       | Booking System                     | Pricing (₹/hr) |
|------------|------------------------------------|----------------|
| User/Guest | Manual duration, alert post-expiry | 60             |
| Worker     | Fixed or custom time slots         | 30             |
| Intern     | Asked duration on input            | Varies         |

---

## ✅ TODOs

- [x] Implement prebooking flow
- [x] Add QR-based login and role-based pricing
- [x] Integrate WhatsApp reminders
- [x] License plate detection using YOLO + EasyOCR
- [x] Add CCTV verification module

---

## 🧾 License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).  
Feel free to use, modify, and distribute — just give credit where it’s due!

MIT License

Copyright (c) 2025 Nandikha

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

---

## 👩‍💻 Author

**Nandikha**  
🌐 GitHub: [nxndikhx]  
📬 Email: nandikhat@gmail.com  
🚀 Built as a final-year project with 💡 + ☕️

---

