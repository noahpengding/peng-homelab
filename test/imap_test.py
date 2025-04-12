import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

dotenv_path = '.env'
load_dotenv(dotenv_path)

from app.utils.imap_email_checker import ImapEmailChecker
from app.config.config import config

email_checker = ImapEmailChecker(
    email_address=config.imap_user,
    password=config.imap_password,
    imap_server=config.imap_server,
    imap_port=config.imap_port
)

email_list = email_checker.get_unread_emails()
for email in email_list:
    print(f"From: {email['from']}")
    print(f"Subject: {email['subject']}")
    print(f"Date: {email['date']}")
    print(f"Body: {email['body']}")
    print(f"Attachments: {email['attachments']}")
    print("-" * 50)