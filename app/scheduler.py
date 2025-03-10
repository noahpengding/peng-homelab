import schedule
import time
from app.services.ip_update.ip_test import ip_test_main, ip_test_schedule_report
from app.services.email_check.email_check import email_check
from app.config.config import config

def scheduler():
    schedule.every(config.test_interval).seconds.do(ip_test_main)
    schedule.every().day.at("09:00").do(ip_test_schedule_report)
    schedule.every().hour.at(":30").do(email_check)

    while True:
        schedule.run_pending()
        time.sleep(10)