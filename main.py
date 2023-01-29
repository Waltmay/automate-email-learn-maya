import os
from dotenv import load_dotenv
import smtplib
import ssl
from email.message import EmailMessage

# Load in email-related environmental variables
load_dotenv()
email_sender = os.environ.get('EMAIL_SENDER')
email_password = os.environ.get('EMAIL_PW')
email_receiver = os.environ.get('EMAIL_RECEIVER')

# Temp subject and body message
subject = 'Test Email'
body = 'This is a text email sent from a Python script.'

# Instantiate EmailMessage class with all necessary info for the email being sent
em = EmailMessage()
em['From'] = email_sender
em['To'] = email_receiver
em['Subject'] = subject
em.set_content(body)

# Add SSL security layer
context = ssl.create_default_context()

# Log in and send email
with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
    smtp.login(email_sender, email_password)
    smtp.sendmail(email_sender, email_receiver, em.as_string())
