import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

dotenv_path = '.env'
load_dotenv(dotenv_path)

from app.utils.vaultwarden_client import BitwardenClient
from app.config.config import config
import re

bw = BitwardenClient()
bw_data = bw.get_ciphers("Test")
email_address = "dingyipeng@dingyipeng.com"
password = next(
    (
        cipher for cipher in bw_data
        if cipher.username == email_address 
            and 
            re.match(f".*{config.smtp_server}.*", cipher.url, re.IGNORECASE)
    ),
    None
)
print(bw_data)
print(password.password)