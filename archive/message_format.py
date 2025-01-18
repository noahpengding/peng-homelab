import re
from app.utils.log import output_log

def format_message(message):
    modified_message = re.sub(r"\*\*", "*", message)
    modified_message = re.sub(r"#+(.*)\n", r"*\1*\n", modified_message)
    return modified_message
