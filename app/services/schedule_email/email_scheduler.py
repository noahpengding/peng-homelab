import os
import datetime
from typing import Dict, List, Optional, Any
import time
import pickle
import re

from app.utils.imap_email_checker import ImapEmailChecker
from app.utils.smtp_email_sender import SmtpEmailSender
from app.utils.vaultwarden_client import BitwardenClient, BitwardenData
from app.utils.minio_connection import MinioStorage
from app.config.config import config
from app.utils.log import output_log

class ScheduledEmail:
    def __init__(self, from_address: str, to_address: str, subject: str, 
                body: str, time_to_send: datetime.datetime, attachments=None):
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
            'id': self.id,
            'from_address': self.from_address,
            'to_address': self.to_address,
            'subject': self.subject,
            'body': self.body,
            'time_to_send': self.time_to_send,
            'attachments': self.attachments
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScheduledEmail':
        """Create a ScheduledEmail from a dictionary.
        
        Args:
            data: Dictionary containing scheduled email data
            
        Returns:
            ScheduledEmail: A ScheduledEmail instance
        """
        email_obj = cls(
            from_address=data['from_address'],
            to_address=data['to_address'],
            subject=data['subject'],
            body=data['body'],
            time_to_send=data['time_to_send'],
            attachments=data.get('attachments', [])
        )
        email_obj.id = data.get('id', email_obj.id)
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
        subject = email_data.get('subject', '')
        body = email_data.get('body', '')
        
        # Split the body into lines
        lines = re.split(r'\r|\n', body)
        if len(lines) < 3:
            output_log("Scheduled email missing required header lines", "error")
            return None
        lines = list(filter(lambda x: x.strip() != '', lines))
        
        # Parse the first three lines
        from_line = lines[0].strip()
        to_line = lines[1].strip()
        time_line = lines[2].strip()
        
        # Extract values
        if not from_line.lower().startswith('from:'):
            output_log(f"Invalid From line in scheduled email: {from_line}", "error")
            from_address = email_data.get('from', '')
        else:
            from_address = re.search(r'\S+@\S+\.com', from_line[5:].strip()).group(0)
        
        if not to_line.lower().startswith('to:'):
            output_log(f"Invalid To line in scheduled email: {to_line}", "error")
            return None
        to_address = re.search(r'\S+@\S+\.com', to_line[3:].strip()).group(0)
        
        
        if not time_line.lower().startswith('time:'):
            output_log(f"Invalid Time line in scheduled email: {time_line}", "error")
            return None
        time_str = time_line[5:].strip()
        
        # Parse the time string (format: YYYY/MM/DD-HH:mm)
        try:
            time_to_send = datetime.datetime.strptime(time_str, '%Y/%m/%d-%H:%M')
        except ValueError:
            output_log(f"Invalid time format in scheduled email: {time_str}", "error")
            return None
        
        # Get the remaining body (excluding the first three lines)
        email_body = '\n'.join(lines[3:])
        
        # Parse any attachments if present
        attachments = email_data.get('attachments', [])
        # In a real implementation, you would extract attachments from the email_data here
        
        return ScheduledEmail(
            from_address=from_address,
            to_address=to_address,
            subject=subject,
            body=email_body,
            time_to_send=time_to_send,
            attachments=attachments
        )
    except Exception as e:
        output_log(f"Error parsing scheduled email: {str(e)}", "error")
        return None


def save_scheduled_emails(emails: List[ScheduledEmail]) -> bool:
    """Save scheduled emails to disk.
    
    Args:
        emails: List of ScheduledEmail objects
        
    Returns:
        bool: True if save successful, False otherwise
    """
    # Convert emails to dictionaries
    emails_data = [email.to_dict() for email in emails]
    
    # Save to file using pickle for datetime serialization
    with open("email.pickle", 'wb') as f:
        pickle.dump(emails_data, f)
    
    minio = MinioStorage()
    minio.file_upload("email.pickle", f"{config.email_path}/email.pickle", "application/octet-stream")
    return True

def load_scheduled_emails() -> List[ScheduledEmail]:
    """Load scheduled emails from disk.
    
    Returns:
        List[ScheduledEmail]: List of ScheduledEmail objects
    """
    minio = MinioStorage()
    if not minio.file_download(f"{config.email_path}/email.pickle", "email.pickle"):
        output_log("Failed to download scheduled emails from Minio", "error")
        return []
    with open("email.pickle", 'rb') as f:
        emails_data = pickle.load(f)
    emails = [ScheduledEmail.from_dict(data) for data in emails_data]
    output_log(f"Loaded {len(emails)} scheduled emails", "debug")
    return emails

def check_scheduled_emails() -> None:
    """Check for new scheduled emails in the configured IMAP account.
    
    This function:
    1. Connects to the IMAP server
    2. Checks for unread emails in the inbox
    3. Parses scheduled email instructions
    4. Saves new scheduled emails
    """
    try:
        if not config.schedule_check_email_address:
            output_log("Schedule check email address not configured, skipping check", "warning")
            return
        
        output_log("Checking for scheduled emails", "info")
        # Connect to IMAP server
        checker = ImapEmailChecker(
            email_address=config.schedule_check_email_address,
            password=config.schedule_check_email_password,
            imap_server=config.imap_server,
            imap_port=config.imap_port
        )
        
        # Get unread emails
        unread_emails = checker.get_unread_emails()
        checker.disconnect()
        if len(unread_emails) == 0:
            return
        
        # Load existing scheduled emails
        scheduled_emails = load_scheduled_emails()
        
        # Process each unread email
        for email_data in unread_emails:
            # Parse the scheduled email
            scheduled_email = parse_scheduled_email(email_data)
            if scheduled_email:
                scheduled_emails.append(scheduled_email)
        save_scheduled_emails(scheduled_emails)
    except Exception as e:
        output_log(f"Error checking scheduled emails: {str(e)}", "error")

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
            cipher for cipher in bw_data
            if cipher.username == email_address 
                and 
                re.match(f".*{config.smtp_server}.*", cipher.url, re.IGNORECASE)
        ),
        None
    )

def send_error_email(to_address: str, error_message: str, subject: str) -> None:
    sender = SmtpEmailSender(
        username=config.schedule_check_email_address,
        password=config.schedule_check_email_password
    )
    sender.send_email(
        to_address=to_address,
        subject=f"Error in scheduled email: {subject}",
        body=f"An error occurred while processing the scheduled email:\n\n{error_message}",
        attachments=[]
    )

def process_scheduled_emails() -> None:
    """Process scheduled emails that are due to be sent.
    
    This function:
    1. Loads scheduled emails
    2. Checks which emails are due
    3. Sends due emails
    4. Removes sent emails from the list
    5. Saves updated list
    """
    try:
        output_log("Processing scheduled emails", "debug")
        
        # Load scheduled emails
        scheduled_emails = load_scheduled_emails()
        if not scheduled_emails:
            return
        
        # Track which emails to keep (not sent yet)
        emails_to_keep = []
        
        # Process each scheduled email
        for email_obj in scheduled_emails:
            if email_obj.is_due():

                output_log(f"Processing scheduled email {email_obj.id} to {email_obj.to_address}", "info")
                # Get credentials from vaultwarden
                bw = BitwardenClient()
                credentials = get_email_credentials(email_obj.from_address, bw.get_ciphers("Email"))
                if not credentials:
                    output_log(f"No credentials found for {email_obj.from_address}", "error")
                    send_error_email(
                        email_obj.from_address,
                        f"No credentials found for {email_obj.from_address}",
                        email_obj.subject
                    )
                    # Add back to list to try later
                    emails_to_keep.append(email_obj)
                    continue
                # Send the email
                try:
                    print(f"{credentials.username} {credentials.password}")
                    sender = SmtpEmailSender(credentials.username, credentials.password)
                    success = sender.send_email(
                        email_obj.to_address,
                        email_obj.subject,
                        email_obj.body,
                        email_obj.attachments
                    )
                    
                    if success:
                        output_log(f"Scheduled email {email_obj.id} sent successfully", "debug")
                    else:
                        output_log(f"Failed to send scheduled email {email_obj.id}", "error")
                        # Send notification about failure
                        send_error_email(
                            email_obj.from_address,
                            f"Failed to send scheduled email {email_obj.id}",
                            email_obj.subject
                        )
                        # Keep in list to retry later if within 24 hours
                        emails_to_keep.append(email_obj)
                except Exception as e:
                    output_log(f"Error sending scheduled email {email_obj.id}: {str(e)}", "error")
                    # Send notification about error
                    send_error_email(
                        email_obj.from_address,
                        str(e),
                        email_obj.subject,
                        email_obj.to_address
                    )
                    emails_to_keep.append(email_obj)
            else:
                # Not due yet, keep in the list
                emails_to_keep.append(email_obj)
        
        # Save updated list of scheduled emails
        if len(emails_to_keep) != len(scheduled_emails):
            output_log(f"Removed {len(scheduled_emails) - len(emails_to_keep)} sent emails", "info")
            save_scheduled_emails(emails_to_keep)
    except Exception as e:
        output_log(f"Error processing scheduled emails: {str(e)}", "error")
