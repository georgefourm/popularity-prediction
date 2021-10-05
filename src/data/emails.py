import os
import re

import pandas as pd
from ietfdata.mailarchive import MailArchive

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from nltk import tokenize

QUOTE_PATTERN = re.compile(rb'^>.*$', flags=re.MULTILINE)
QUOTE_START_PATTERN = re.compile(rb'On .+ wrote:')
WHITESPACE_PATTERN = re.compile(rb'\s+')


def download_emails(mail_list: str, archive=None, output_dir="data/raw", update=False):
    if archive is None:
        archive = MailArchive()

    print("Downloading emails...")
    m_list = archive.mailing_list(mail_list)
    if update:
        m_list.update()

    messages = m_list.messages()

    output_path = os.path.join(output_dir, mail_list)

    if not os.path.exists(output_path):
        os.mkdir(output_path)

    messages_dict = []
    for message in messages:
        rfc_obj = message.rfc822_message()
        body = rfc_obj.get_body(preferencelist=('plain', 'html'))
        messages_dict.append({
            "timestamp": message.date,
            "from": message.from_addr,
            "subject": message.subject,
            "content": body.get_payload(decode=True),
            "charset": body.get_content_charset()
        })

    df = pd.DataFrame(messages_dict)
    df.to_pickle(os.path.join(output_path, "emails.pkl"))


def clean_content(content):
    # Remove quotes
    content = QUOTE_PATTERN.sub(b'', content)
    # Collapse newlines to single spaces
    content = WHITESPACE_PATTERN.sub(b' ', content).strip()
    # Remove start of quote
    content = QUOTE_START_PATTERN.sub(b'', content)
    return content


def compute_sentiment(row):
    analyzer = SentimentIntensityAnalyzer()

    charset = 'utf-8' if row['charset'] is None else row['charset']
    try:
        decoded_text = row['content'].decode(charset)
    except UnicodeDecodeError:
        return None

    sentences = tokenize.sent_tokenize(decoded_text)
    overall_polarity = 0
    if len(sentences) == 0:
        return 0.0

    for sentence in sentences:
        scores = analyzer.polarity_scores(sentence)
        overall_polarity += scores['compound']
    return overall_polarity / len(sentences)
