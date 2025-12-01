#!/usr/bin/env python3
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://byvkcpdtprodvhadpdix.supabase.co")
# Lấy từ Dashboard > Settings > API > service_role secret
SERVICE_ROLE_KEY = os.getenv("SERVICE_ROLE_KEY", "YOUR_SERVICE_ROLE_KEY_HERE")
TARGET_EMAIL = "tuantrungvuongk62@gmail.com"

def main():
    if not SERVICE_ROLE_KEY or "ey" not in SERVICE_ROLE_KEY:
        print("❌ Error: SERVICE_ROLE_KEY không hợp lệ")
        return

    supabase = create_client(SUPABASE_URL, SERVICE_ROLE_KEY)
    print(f"🔗 Connecting to: {SUPABASE_URL}")
    print(f"📧 Inviting Author: {TARGET_EMAIL}")

    try:
        # Invite với role 'author' để Trigger SQL tự bắt và set role_id=2
        response = supabase.auth.admin.invite_user_by_email(
            email=TARGET_EMAIL,
            options={
                "data": {
                    "role": "author", # Trigger sẽ map cái này thành role_id=2
                    "invited_by": "admin_script"
                }
            }
        )
        print(f"✅ Success! User ID: {response.user.id}")
        print("👉 User check mail > Click link > Profile tự động tạo với role Author.")

    except Exception as e:
        if "already registered" in str(e):
            print("⚠️ User đã tồn tại. Xóa user cũ trong Dashboard nếu muốn test lại.")
        else:
            print(f"❌ Failed: {str(e)}")

if __name__ == "__main__":
    main()
