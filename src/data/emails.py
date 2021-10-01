import os
import re

import pandas as pd
from ietfdata.mailarchive import MailArchive

QUOTE_PATTERN = re.compile(rb'^>.*$', flags=re.MULTILINE)
QUOTE_START_PATTERN = re.compile(rb'On .+ wrote:')
WHITESPACE_PATTERN = re.compile(rb'\s+')


def download_emails(mail_list: str, archive=None, output_dir="data/raw"):
    if archive is None:
        archive = MailArchive()

    print("Downloading emails...")
    m_list = archive.mailing_list(mail_list)
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
