import datetime
from typing import Dict, List, Optional, Any
import time
import pickle
import re
import pandas as pd
import os

from app.utils.imap_email_checker import ImapEmailChecker
from app.utils.smtp_email_sender import SmtpEmailSender
from app.utils.vaultwarden_client import BitwardenClient, BitwardenData
from app.utils.minio_connection import MinioStorage
from app.config.config import config
from app.utils.log import output_log


class ScheduledEmail:
    def __init__(
        self,
        from_address: str,
        to_address: str,
        subject: str,
        body: str,
        time_to_send: datetime.datetime,
        attachments=None,
    ):
        """Initialize a ScheduledEmail object to represent a scheduled email.

        Args:
            from_address: The sender's email address
            to_address: The recipient's email address
            subject: The email subject
            body: The email body
            time_to_send: The datetime to send the email
            attachments: Optional list of attachment dictionaries
        """
        self.from_address = from_address
        if "<" in from_address and ">" in from_address:
            self.from_address = re.search(r"<(.*?)>", from_address).group(1)
        self.to_address = to_address
        self.subject = subject
        self.body = body
        self.time_to_send = time_to_send
        self.attachments = attachments or []
        self.id = f"{from_address}-{to_address}-{int(time.time())}"

    def is_due(self) -> bool:
        """Check if the email is due to be sent.

        Returns:
            bool: True if the email should be sent now, False otherwise
        """
        now = datetime.datetime.now()
        return self.time_to_send <= now

    def to_dict(self) -> Dict[str, Any]:
        """Convert the ScheduledEmail to a dictionary for serialization.

        Returns:
            Dict[str, Any]: Dictionary representation of the scheduled email
        """
        return {
            "id": self.id,
            "from_address": self.from_address,
            "to_address": self.to_address,
            "subject": self.subject,
            "body": self.body,
            "time_to_send": self.time_to_send,
            "attachments": self.attachments,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScheduledEmail":
        """Create a ScheduledEmail from a dictionary.

        Args:
            data: Dictionary containing scheduled email data

        Returns:
            ScheduledEmail: A ScheduledEmail instance
        """
        email_obj = cls(
            from_address=data["from_address"],
            to_address=data["to_address"],
            subject=data["subject"],
            body=data["body"],
            time_to_send=data["time_to_send"],
            attachments=data.get("attachments", []),
        )
        email_obj.id = data.get("id", email_obj.id)
        return email_obj


def parse_scheduled_email(email_data: Dict[str, Any]) -> Optional[ScheduledEmail]:
    """Parse a scheduled email from an email message.

    Email should have the first three lines in the format:
    From: sender@example.com
    To: recipient@example.com
    Time: YYYY/MM/DD-HH:mm

    Args:
        email_data: Dictionary containing email data from IMAP

    Returns:
        Optional[ScheduledEmail]: A ScheduledEmail instance if parsing successful,
                                None otherwise
    """
    try:
        subject = email_data.get("subject", "")
        body = email_data.get("body", "")
        from_address = email_data.get("from", "")

        # Split the body into lines
        lines = re.split(r"\r|\n", body)
        if len(lines) < 3:
            output_log("Scheduled email missing required header lines", "error")
            return None
        lines = list(filter(lambda x: x.strip() != "", lines))

        to_line = lines[0].strip()
        time_line = lines[1].strip()

        if not to_line.lower().startswith("to:"):
            output_log(f"Invalid To line in scheduled email: {to_line}", "error")
            return None
        if not re.match(r"\S+@\S+\.\S+", to_line[3:].strip()):
            output_log(
                f"Invalid To email address in scheduled email: {to_line}", "error"
            )
            return None
        to_address = re.search(r"\S+@\S+\.\S+", to_line[3:].strip()).group(0)

        if not time_line.lower().startswith("time:"):
            output_log(f"Invalid Time line in scheduled email: {time_line}", "error")
            return None
        time_str = time_line[5:].strip()

        # Parse the time string (format: YYYY/MM/DD-HH:mm)
        try:
            time_to_send = datetime.datetime.strptime(time_str, "%Y/%m/%d-%H:%M")
        except ValueError:
            output_log(f"Invalid time format in scheduled email: {time_str}", "error")
            return None

        # Get the remaining body (excluding the first two lines)
        print(lines)
        email_body = "\n\n".join(lines[2:])

        # Parse any attachments if present
        attachments = email_data.get("attachments", [])
        # In a real implementation, you would extract attachments from the email_data here

        return ScheduledEmail(
            from_address=from_address,
            to_address=to_address,
            subject=subject,
            body=email_body,
            time_to_send=time_to_send,
            attachments=attachments,
        )
    except Exception as e:
        output_log(f"Error parsing scheduled email: {str(e)}", "error")
        return None


def save_scheduled_emails(emails: List[ScheduledEmail]):
    minio = MinioStorage()
    minio.file_download(
        f"{config.s3_base_path}/email/email_schedule.xlsx", "email_schedule.xlsx"
    )
    schedule_email_list = pd.read_excel("email_schedule.xlsx").to_dict(orient="records")
    for email in emails:
        current_time = datetime.datetime.now()
        with open(f"email-{current_time}.pickle", "wb") as f:
            pickle.dump(email, f)

        if minio.file_upload(
            f"email-{current_time}.pickle",
            f"{config.s3_base_path}/email/email-{current_time}.pickle",
            "application/octet-stream",
        ):
            schedule_email_list.append(
                {
                    "time": email.time_to_send,
                    "from": email.from_address,
                    "to": email.to_address,
                    "subject": email.subject,
                    "pickle_file": f"email-{current_time}.pickle",
                }
            )
        else:
            output_log(
                f"Failed to upload scheduled email {email.subject} to Minio", "error"
            )
    schedule_email_list_df = pd.DataFrame(schedule_email_list)
    schedule_email_list_df.to_excel("email_schedule.xlsx", index=False)
    minio.file_upload(
        "email_schedule.xlsx",
        f"{config.s3_base_path}/email/email_schedule.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    return True


def load_scheduled_emails_list() -> List[Dict[str, Any]]:
    minio = MinioStorage()
    if not minio.file_download(
        f"{config.s3_base_path}/email/email_schedule.xlsx", "email_schedule.xlsx"
    ):
        return []
    schedule_email_list = pd.read_excel("email_schedule.xlsx").to_dict(orient="records")
    return schedule_email_list


def check_scheduled_emails():
    """Check for new scheduled emails in the configured IMAP account.

    This function:
    1. Connects to the IMAP server
    2. Checks for unread emails in the inbox
    3. Parses scheduled email instructions
    4. Saves new scheduled emails
    """
    try:
        if not config.schedule_check_email_address:
            output_log(
                "Schedule check email address not configured, skipping check", "warning"
            )
            return

        output_log("Checking for scheduled emails", "info")
        # Connect to IMAP server
        checker = ImapEmailChecker(
            email_address=config.schedule_check_email_address,
            password=config.schedule_check_email_password,
            imap_server=config.imap_server,
            imap_port=config.imap_port,
        )

        # Get unread emails
        unread_emails = checker.get_unread_emails()
        checker.disconnect()
        if len(unread_emails) == 0:
            return 0

        for email_data in unread_emails:
            scheduled_email = parse_scheduled_email(email_data)
            if scheduled_email:
                output_log(
                    f"Scheduling email from {scheduled_email.from_address} to {scheduled_email.to_address} at {scheduled_email.time_to_send}",
                    "info",
                )
                save_scheduled_emails([scheduled_email])
            else:
                output_log(
                    f"Failed to parse scheduled email with subject: {email_data.get('subject', '')}",
                    "error",
                )
    except Exception as e:
        output_log(f"Error checking scheduled emails: {str(e)}", "error")
    return len(unread_emails)


def get_email_credentials(email_address: str, bw_data: BitwardenData) -> str:
    """Get email credentials from vaultwarden.

    Args:
        email_address: The email address to get credentials for
        bw_data: BitwardenData object containing credentials

    Returns:
        str: The email credentials
    """
    return next(
        (
            cipher
            for cipher in bw_data
            if cipher.username == email_address
            and re.match(f".*{config.smtp_server}.*", cipher.url, re.IGNORECASE)
        ),
        None,
    )


def send_error_email(to_address: str, error_message: str, subject: str) -> None:
    sender = SmtpEmailSender(
        username=config.schedule_check_email_address,
        password=config.schedule_check_email_password,
    )
    sender.send_email(
        to_address=to_address,
        subject=f"Error in scheduled email: {subject}",
        body=f"An error occurred while processing the scheduled email:\n\n{error_message}",
        attachments=[],
    )


def process_scheduled_emails():
    output_log("Processing scheduled emails", "debug")

    schedule_email_list = load_scheduled_emails_list()
    previous_length = len(schedule_email_list)
    if not schedule_email_list or len(schedule_email_list) == 0:
        return
    minio = MinioStorage()
    current_time = datetime.datetime.now()
    for item in schedule_email_list:
        item["time"] = pd.to_datetime(item["time"])
        if item["time"] <= current_time:
            from_address = item["from"]
            to_address = item["to"]
            subject = item["subject"]
            pickle_file = item["pickle_file"]

            if not minio.file_download(
                f"{config.s3_base_path}/email/{pickle_file}", pickle_file
            ):
                output_log(
                    f"Failed to download scheduled email file {pickle_file} from Minio",
                    "error",
                )
                continue

            bw = BitwardenClient()
            credentials = get_email_credentials(from_address, bw.get_ciphers("Share"))
            if not credentials:
                output_log(f"No credentials found for {from_address}", "error")
                send_error_email(
                    from_address,
                    f"No credentials found for {from_address}",
                    subject,
                )
                continue

            with open(pickle_file, "rb") as f:
                email_obj = pickle.load(f)
            os.remove(pickle_file)
            body = email_obj.body
            attachments = email_obj.attachments
            attempt = 0

            while attempt < 5:
                sender = SmtpEmailSender(
                    username=from_address,
                    password=credentials.password,
                )
                if sender.connect():
                    success = sender.send_email(
                        to_address=to_address,
                        subject=subject,
                        body=body,
                        attachments=attachments,
                    )
                    if success:
                        output_log(f"Scheduled email sent to {to_address}", "info")
                        minio.remove_file(f"{config.s3_base_path}/email/{pickle_file}")
                        schedule_email_list.remove(item)
                        break
                    else:
                        output_log(
                            f"Failed to send scheduled email to {to_address}, attempt {attempt + 1}",
                            "warning",
                        )
                else:
                    output_log(
                        f"Failed to connect to SMTP server for {from_address}, attempt {attempt + 1}",
                        "warning",
                    )
                attempt += 1
                time.sleep(2**attempt)

    schedule_email_list_df = pd.DataFrame(schedule_email_list)
    schedule_email_list_df.to_excel("email_schedule.xlsx", index=False)
    minio.file_upload(
        "email_schedule.xlsx",
        f"{config.s3_base_path}/email/email_schedule.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    return previous_length - len(schedule_email_list)
