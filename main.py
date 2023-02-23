import os
from dotenv import load_dotenv
import smtplib
import ssl
from email.message import EmailMessage
import pandas as pd
from datetime import date

# Load in email-related environmental variables
load_dotenv()
email_sender = os.environ.get('EMAIL_SENDER')
email_password = os.environ.get('EMAIL_PW')
email_receiver = os.environ.get('EMAIL_RECEIVER')


def det_word_to_send():
    # Load in with Windows-1252 encoding given the CSV's special characters
    all_words = pd.read_csv('yucatecan-maya-definitions.csv', encoding='cp1252')
    word_definition_pair = all_words.sample(n=1)
    word = word_definition_pair['words'].values[0].title()
    definition = word_definition_pair['definitions'].values[0]
    return word, definition


word, definition = det_word_to_send()

# Subject line of email
subject = f"Maya Word of the Day: {date.today()}"

body = f'''
<html>
    <span style = "font-family: Verdana">
        <body>
            The Spanish-Maya word of the day is:
            <br> 
            <br> <b>Spanish Word/Phrase:</b> {word} 
            <br> <b>Mayan Translation:</b> {definition}
            <br>
            <br> Notice any typos or mistranslations? Reply to this email to notify the owner!
            <br>
            <br> <b> Parts of speech guide </b>
                <li> <em>sus</em>: sustantivo / noun</li>
                <li> <em>adj</em>: adjetivo / adjective</li>
                <li> <em>adv.</em>: adverbio / adverb </li>
                <li> <em>v.i</em>: verbo intransitvo / intransitive verb</li> 
                <li> <em>v.t</em>: verbo transitvo / transitive verb</li> 
                <li> <em>prep</em>: preposici&oacute;n / preposition</li>
                <li> <em>pron</em>: pronombre / pronoun</li>
                <li> <em>conj</em>: conjunci&oacute;n / conjunction</li>
        </body>
    </span>
</html>
'''

# Instantiate EmailMessage class with all necessary info for the email being sent
em = EmailMessage()
em['From'] = email_sender
em['To'] = email_receiver
em['Subject'] = subject
em.set_content(body, subtype = 'html')

# Add SSL security layer
context = ssl.create_default_context()

# Log in and send email
with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
    smtp.login(email_sender, email_password)
    smtp.sendmail(email_sender, email_receiver, em.as_string())
