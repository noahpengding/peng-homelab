import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

dotenv_path = '.env'
load_dotenv(dotenv_path)

from app.utils.smtp_email_sender import SmtpEmailSender
from app.config.config import config

email = SmtpEmailSender(
    username=config.schedule_check_email_address,
    password=config.smtp_password
)
email.send_email(
    to_address="tw@tenawalcott.com", 
    subject="Test Email",
    body="This is a test email from Python.",
    attachments=None
)
