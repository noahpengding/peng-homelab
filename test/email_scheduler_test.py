import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

dotenv_path = '.env'
load_dotenv(dotenv_path)

from app.services.schedule_email.email_scheduler import check_scheduled_emails, process_scheduled_emails

check_scheduled_emails()
process_scheduled_emails()
