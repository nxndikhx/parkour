import pandas as pd
import hashlib
import os

USER_CSV = "datasets/user_authentication_dataset.csv"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login_user():
    email = input("📧 Email: ").strip()
    password = input("🔐 Password: ").strip()
    if not os.path.exists(USER_CSV):
        print("⚠️ No users registered yet.")
        return None
    df = pd.read_csv(USER_CSV)
    user = df[df["Email"] == email]
    if not user.empty and user.iloc[0]["Password_Hash"] == hash_password(password):
        return user.iloc[0].to_dict()
    print("❌ Invalid email or password.")
    return None

def register_user():
    name = input("👤 Name: ").strip()
    phone = input("📱 Phone: ").strip()
    email = input("📧 Email: ").strip()
    password = input("🔐 Password: ").strip()
    role = input("🔧 Role (user/official/intern/worker): ").strip().lower()

    df = pd.read_csv(USER_CSV) if os.path.exists(USER_CSV) else pd.DataFrame(columns=[
        "User_ID", "Name", "Phone", "Email", "Password_Hash", "IsActive",
        "Slot", "VehicleNumber", "VehicleType", "IsElectric", "Role", "CheckIn", "CheckOut", "Notes"
    ])
    
    new_id = f"user_{len(df) + 1}"
    df.loc[len(df)] = [
        new_id, name, phone, email, hash_password(password), "Yes",
        "", "", "", "", role, "", "", ""
    ]
    df.to_csv(USER_CSV, index=False)
    print("✅ Registered successfully!")
    return df[df["User_ID"] == new_id].iloc[0].to_dict()
