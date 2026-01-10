import asyncio
from src.auth.email_verification import send_verification_email

async def test_email():
    try:
        await send_verification_email(
            "hernandez.luis.hiram@hotmail.com", 
            "TestUser", 
            "http://localhost:8000/test-link"
        )
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Email failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_email())


import asyncio
from src.auth.email_verification import send_verification_email
from src.auth.auth import create_verification_token

async def test_email_true_user():
    try:
        # Create a real verification token (like your signup process does)
        test_email = "hernandez.luis.hiram@hotmail.com"
        test_user_id = 1  # Use a test user ID
        
        verification_token = create_verification_token(test_email, test_user_id)
        verification_link = f"http://localhost:8000/api/v1/auth/verify-email?token={verification_token}"
        
        await send_verification_email(
            test_email, 
            "TestUser", 
            verification_link
        )
        print("✅ Email sent successfully!")
        print(f"🔗 Verification link: {verification_link}")
        
    except Exception as e:
        print(f"❌ Email failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_email())