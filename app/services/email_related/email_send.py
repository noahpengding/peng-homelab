from app.services.vaultwarden_password.get_password import get_password_by_name_and_username
from app.utils.smtp_email_sender import SmtpEmailSender

def email_send(from_address, to_address, subject, body, attachments) -> bool:
    password = get_password_by_name_and_username(name="mail.tenawalcott.com", username=from_address)
    if not password:
        return False
    email_sender = SmtpEmailSender(username=from_address, password=password.password)
    if not email_sender.connect():
        return False
    success = email_sender.send_email(
        to_address=to_address,
        subject=subject,
        body=body,
        attachments=attachments,
    )
    return success
