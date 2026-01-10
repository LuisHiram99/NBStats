from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import load_dotenv
from pathlib import Path
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent

# Load environment variables from config/.env
env_path = PROJECT_ROOT / 'config' / '.env'
load_dotenv(dotenv_path=env_path)

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

