import imaplib
import email
from email.header import decode_header
from typing import List, Dict, Any


class ImapEmailChecker:
    def __init__(self, email_address: str, password: str, imap_server: str, imap_port: int = 993):
        """
        Initialize the ImapEmailChecker with credentials and server information.
        
        Args:
            email_address: Your email address
            password: Your email password
            imap_server: IMAP server address (e.g., imap.gmail.com)
            imap_port: IMAP server port (default: 993 for SSL)
        """
        self.email_address = email_address
        self.password = password
        self.imap_server = imap_server
        self.imap_port = imap_port
        self.mail = None
    
    def connect(self) -> bool:
        """
        Connect to the IMAP server.
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            # Create an IMAP4 class with SSL
            self.mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            # Authenticate
            self.mail.login(self.email_address, self.password)
            self.mail.select("INBOX")
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def disconnect(self) -> None:
        """Close the connection to the IMAP server."""
        if self.mail:
            self.mail.close()
            self.mail.logout()
    
    def get_unread_emails(self, mailbox: str = "INBOX") -> List[Dict[str, Any]]:
        """
        Get unread emails from the specified mailbox.
        
        Args:
            mailbox: The mailbox to check (default: "INBOX")
            
        Returns:
            List[Dict[str, Any]]: List of dictionaries containing email data
        """
        if not self.mail:
            if not self.connect():
                return []
        
        try:
            # Select the mailbox
            status, messages = self.mail.select(mailbox)
            if status != "OK":
                print(f"Error selecting mailbox {mailbox}: {messages}")
                return []
            
            # Search for unread emails
            status, message_ids = self.mail.search(None, "UNSEEN")
            if status != "OK":
                print("No unread emails found")
                return []
            
            email_list = []
            # Process each unread email
            for message_id in message_ids[0].split():
                email_data = self._process_email(message_id)
                if email_data:
                    email_list.append(email_data)
                    # Mark as read
                    self.mail.store(message_id, '+FLAGS', '\\Seen')
            
            return email_list
        
        except Exception as e:
            print(f"Error retrieving emails: {e}")
            return []
    
    def _process_email(self, message_id: bytes) -> Dict[str, Any]:
        """
        Process a single email and extract its data.
        
        Args:
            message_id: The ID of the email message
            
        Returns:
            Dict[str, Any]: Dictionary containing email data
        """
        try:
            # Fetch the email data
            status, msg_data = self.mail.fetch(message_id, "(RFC822)")
            if status != "OK":
                print(f"Error fetching message {message_id}: {msg_data}")
                return None
            
            # Parse the raw email
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)
            
            # Get email subject
            subject = self._decode_email_header(msg["Subject"])
            # Get email from
            from_address = self._decode_email_header(msg["From"])
            # Get email date
            date = msg["Date"]
            
            # Get email body
            body = ""
            if msg.is_multipart():
                # If the email has multiple parts, find the text/plain part
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        body = self._get_email_body(part)
                        break
            else:
                # If the email is not multipart, just get the body
                body = self._get_email_body(msg)
            
            return {
                "id": message_id.decode(),
                "subject": subject,
                "from": from_address,
                "date": date,
                "body": body
            }
        
        except Exception as e:
            print(f"Error processing message {message_id}: {e}")
            return None
    
    def _decode_email_header(self, header: str) -> str:
        """
        Decode email header value.
        
        Args:
            header: The header to decode
            
        Returns:
            str: Decoded header value
        """
        if not header:
            return ""
            
        decoded_header = decode_header(header)
        header_parts = []
        
        for part, encoding in decoded_header:
            if isinstance(part, bytes):
                try:
                    if encoding:
                        part = part.decode(encoding)
                    else:
                        part = part.decode('utf-8', errors='replace')
                except Exception:
                    part = part.decode('utf-8', errors='replace')
            header_parts.append(str(part))
            
        return " ".join(header_parts)
    
    def _get_email_body(self, message_part) -> str:
        """
        Extract the body from an email message part.
        
        Args:
            message_part: The email message part
            
        Returns:
            str: Email body content
        """
        payload = message_part.get_payload(decode=True)
        if payload:
            charset = message_part.get_content_charset()
            if charset:
                try:
                    return payload.decode(charset)
                except Exception:
                    return payload.decode('utf-8', errors='replace')
            else:
                return payload.decode('utf-8', errors='replace')
        return ""
