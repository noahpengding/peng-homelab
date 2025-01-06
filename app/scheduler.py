import schedule
import time
from app.ip_test import ip_test_main, ip_test_schedule_report
from app.config import config

def scheduler():
    schedule.every(config.test_interval).seconds.do(ip_test_main)
    schedule.every().day.at("09:00").do(ip_test_schedule_report)

    while True:
        schedule.run_pending()
        time.sleep(10)