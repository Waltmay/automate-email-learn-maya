import os
from dotenv import load_dotenv
load_dotenv()
email_sender = os.environ.get('EMAIL_SENDER')
email_password = os.environ.get('EMAIL_PW')
email_receiver = os.environ.get('EMAIL_RECEIVER')

