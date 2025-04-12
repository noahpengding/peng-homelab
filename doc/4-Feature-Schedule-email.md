Your goal is to add a feature to the current pyrhon homelab managment system that can send email schedulely using IMAP

Design:
- The user will send their scheduled email to a address with start three lines specify the from_address, to_address, time_to_send
- All email address username and password are stored in vaultwarden
- All email address username use the same imap host, port, SSL settings
- A user cannot send email as other address
- To get the vaultwarden collection use the python library [python-vaultwarden
](https://github.com/numberly/python-vaultwarden); Read the document and sample carefully
- The python script will first read the email from the specifial address, and get the from_address, to_address, and time_to_send from the first three lines. Use the "Bitwarden client" part
- Then, the script will find the username and password from vaultwarden for the from_address. 
- Notice that the script should find the entries with username=from_address and url/website eqauls to "mail."+ the part after @ in the from_address. eg: from_address=dingyipeng@dingyipeng.com, the script should search for items with username=dingyipeng@dingyipeng.com and URL=https://mail.dingyipeng.com/ and get the email of that.
- After that it will add event to schedule that will send the email using the from_address and the associated password to the to_address at the time_to_send time
- The top three line of the email body is removed while sending; the header and other things are keep same
- The email may have attachment

Requirements:
- Follow the [copilot-instructions.md](../.github/copilot-instructions.md)
- Follow the design workflow and requirements
- Always use python in this project
- Write the code in mainly in folder "app/services/email_schedule"
- Config field should be add into "app/config"; common used code should be add into "app/utils"
- The script should check the schedule email address hourly with SMTP
- The smtp/imap host, port, SSL (SSL True / False), username, password, the schedule email address should be included in configurations
- The time_to_send will be the format "YYYY/MM/DD-HH:mm"
- The email should send back to the from_address using the schedule email address if a failure is triggered while sending
- Use the same coding style as the project previously
- You can use the following settings to test vaultwarden library and understand the resturns: 
  - client_id: `user.521d1f79-d55f-4f7e-86c8-cfb17ded7fd9`
  - client_secret: `dFd14BmpmaInbZlXkmtfgiPEqAtH77`
  - scope: `api`
  - grant_type: `client_credentials`
- You should get a email address for "dingyipeng@dingyipeng.com" with password "NRtMjB8UMA93vl" in the testing vaultwarden