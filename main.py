import os
from dotenv import load_dotenv
import smtplib
import ssl
from email.message import EmailMessage
import pandas as pd
from datetime import date
from pathlib import Path
import csv
import json

# Load in email-related environmental variables
load_dotenv()
email_sender = os.environ.get('EMAIL_SENDER')
email_password = os.environ.get('EMAIL_PW')
email_receiver = os.environ.get('EMAIL_RECEIVER')


def subset_to_unchosen_words(all_words):
    if Path('./past-words.csv').is_file():
        past_words_df = pd.read_csv('past-words.csv', encoding='cp1252')
        past_words_list = past_words_df['word_id'].tolist()
        unchosen_words = all_words[~all_words.word_id.isin(past_words_list)]
        return unchosen_words
    else:
        return all_words


def det_word_to_send():
    # Load in with Windows-1252 encoding given the CSV's special characters
    all_words = pd.read_csv('yucatecan-maya-definitions.csv', encoding='cp1252').reset_index(drop=True)
    unchosen_words = subset_to_unchosen_words(all_words)
    word_definition_pair = unchosen_words.sample(n=1)
    word = word_definition_pair['words'].values[0].title()
    definition = word_definition_pair['definitions'].values[0]
    word_id = word_definition_pair['word_id'].values[0]
    return word, definition, word_id


word, definition, word_id = det_word_to_send()


def record_word_def_chosen(word, definition, word_id):
    fieldnames = ['word_id', 'word', 'definition', 'date']
    if Path('./past-words.csv').is_file():
        with open('past-words.csv', 'a', encoding='cp1252', newline='') as past_words_csv:
            writer = csv.DictWriter(past_words_csv, fieldnames=fieldnames)
            writer.writerow({'word_id': word_id, 'word': word, 'definition': definition, 'date': date.today()})
    else:
        with open('past-words.csv', 'a', encoding='cp1252', newline='') as past_words_csv:
            writer = csv.DictWriter(past_words_csv, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({'word_id': word_id, 'word': word, 'definition': definition, 'date': date.today()})



record_word_def_chosen(word, definition, word_id)

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
em.set_content(body, subtype='html')

# Add SSL security layer
context = ssl.create_default_context()

# Log in and send email
with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
    smtp.login(email_sender, email_password)
    email_list = json.loads(os.environ['EMAIL_RECEIVER'])
    for email_receiver in email_list:
        smtp.sendmail(email_sender, email_receiver, em.as_string())
