import schedule
import time
from app.services.ip_update.ip_test import ip_test_main, ip_test_schedule_report
from app.services.mattermost_email.email_check import email_check
from app.services.schedule_email.email_scheduler import (
    check_scheduled_emails,
    process_scheduled_emails,
)
from app.config.config import config


def scheduler():
    schedule.every(config.test_interval).seconds.do(ip_test_main)
    schedule.every().day.at("09:00").do(ip_test_schedule_report)
    schedule.every().hour.at(":30").do(email_check)

    # Email scheduling tasks
    schedule.every().hour.do(check_scheduled_emails)
    schedule.every(10).minutes.do(process_scheduled_emails)

    while True:
        schedule.run_pending()
        time.sleep(10)
