from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import load_dotenv
from pathlib import Path
import os
import logging
from jose import jwt
from datetime import datetime, timedelta, timezone
from secrets import token_hex

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent

# Load environment variables from config/.env
env_path = PROJECT_ROOT / 'config' / '.env'
load_dotenv(dotenv_path=env_path)

SECRET_KEY = os.getenv("SECRET_KEY", token_hex(32))
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 300000  # 300000 minutes = ~208 days

# Debug environment variables
logger.info(f"MAIL_USERNAME: {os.getenv('MAIL_USERNAME')}")
logger.info(f"MAIL_SERVER: {os.getenv('MAIL_SERVER')}")
logger.info(f"MAIL_PORT: {os.getenv('MAIL_PORT')}")

mail_config = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
    )

def create_verification_token(email: str, user_id: int):
    """Create a verification token that expires in 24 hours"""
    encode = {
        "sub": email, 
        "user_id": user_id, 
        "type": "email_verification"
    }
    expires = datetime.now(timezone.utc) + timedelta(hours=24)
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def send_verification_email(email_to: str, username: str, verification_link: str):
    """Send email verification link to the user."""
    try:
        logger.info(f"Attempting to send verification email to: {email_to}")
        
        subject = "NBStats Email Verification"
        body = f"""
        <p>Hi {username},</p>
        <p>Thank you for registering at NBStats! Please click the link below to verify your email address:</p>
        <p><a href="{verification_link}">Verify Email</a></p>
        <p>If you did not sign up for this account, please ignore this email.</p>
        <br>
        <p>Best regards,<br>NBStats Team</p>
        """
        
        message = MessageSchema(
            subject=subject,
            recipients=[email_to],
            body=body,
            subtype="html"
        )
        
        fm = FastMail(mail_config)
        await fm.send_message(message)
        logger.info(f"Email sent successfully to: {email_to}")
        
    except Exception as e:
        logger.error(f"Failed to send email to {email_to}: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        raise e

