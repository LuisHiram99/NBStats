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