import csv
import json
import os
import pandas as pd
import smtplib
import ssl
from datetime import date
from dotenv import load_dotenv
from email.message import EmailMessage
from pathlib import Path


def main():
    load_dotenv()
    word, definition, word_id = determine_word_to_send()
    record_word_def_chosen(word, definition, word_id)
    email = create_email(word, definition)
    send_email(email)


def determine_word_to_send():
    # Load in with Windows-1252 encoding given the CSV's special characters
    all_words = pd.read_csv('yucatecan-maya-definitions.csv', encoding='cp1252').reset_index(drop=True)

    # Randomly select one word from all words that haven't been chosen before
    unchosen_words = subset_to_unchosen_words(all_words)
    word_definition_pair = unchosen_words.sample(n=1)

    # Grab the word and definition values from the randomly selected row
    word = word_definition_pair['words'].values[0].title()
    definition = word_definition_pair['definitions'].values[0]
    word_id = word_definition_pair['word_id'].values[0]
    return word, definition, word_id


def subset_to_unchosen_words(all_words):
    if Path('./past-words.csv').is_file():
        past_words_df = pd.read_csv('past-words.csv', encoding='cp1252')
        past_words_list = past_words_df['word_id'].tolist()
        unchosen_words = all_words[~all_words.word_id.isin(past_words_list)]
        return unchosen_words
    else:
        return all_words


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


def create_email(word, definition):
    subject, body = create_email_text(word, definition)

    email = structure_email(subject, body)
    return email


def create_email_text(word, definition):
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
    return subject, body


def structure_email(subject, body):
    email_sender = os.environ['EMAIL_SENDER']

    # Instantiate EmailMessage class with all necessary info for the email being sent
    email = EmailMessage()
    email['From'] = email_sender
    email['Subject'] = subject
    email.set_content(body, subtype='html')
    return email


def send_email(email):
    # Load in email-related environmental variables
    email_sender = os.environ.get('EMAIL_SENDER')
    email_password = os.environ.get('EMAIL_PW')
    email_list = json.loads(os.environ['EMAIL_LIST'])

    # Add SSL security layer
    context = ssl.create_default_context()

    # Log in and send email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        for email_receiver in email_list:
            smtp.sendmail(email_sender, email_receiver, email.as_string())


if __name__ == '__main__':
    main()
