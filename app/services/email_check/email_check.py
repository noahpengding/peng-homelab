from app.services.email_check.imap_email_checker import ImapEmailChecker
from app.config.config import config
from app.utils.log import output_log
from app.utils.rabbitmq_publisher import RabbitMQPublisher

def email_check():
    email_checker = ImapEmailChecker(
        config.imap_user,
        config.imap_password,
        config.imap_server,
        config.imap_port
    )
    
    for email in email_checker.get_unread_emails():
        r = RabbitMQPublisher()
        r.publish(f"## {email['subject']} \n {email['body']}")
        output_log(f"Email Received: {email['subject']}", "info")

    email_checker.disconnect()
    output_log("Email Check Done", "info")
