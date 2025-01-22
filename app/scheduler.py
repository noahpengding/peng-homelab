import schedule
import time
from app.services.ip_update.ip_test import ip_test_main, ip_test_schedule_report
from app.services.updater.update_handler import update_all_handler
from app.services.upgrader.upgrade_handler import upgrade_handler
from app.handlers.schedule_message_check import schedule_message_check
from app.config.config import config

def scheduler():
    schedule.every(config.test_interval).seconds.do(ip_test_main)
    schedule.every().day.at("09:00").do(ip_test_schedule_report)
    schedule.every(4).hours.do(update_all_handler)
    schedule.every(30).seconds.do(schedule_message_check)

    while True:
        schedule.run_pending()
        time.sleep(10)