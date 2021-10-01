from ietfdata.mailarchive import MailArchive
import pandas as pd
import re

QUOTE_PATTERN = re.compile(rb'^>.*$', flags=re.MULTILINE)
QUOTE_START_PATTERN = re.compile(rb'On .+ wrote:')
WHITESPACE_PATTERN = re.compile(rb'\s+')


def download_emails(mail_list: str, archive=None, output_file="data/raw/emails.pkl"):
    if archive is None:
        archive = MailArchive()

    m_list = archive.mailing_list(mail_list)
    messages = m_list.messages()

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
    df.to_pickle(output_file)


def clean_content(content):
    # Remove quotes
    content = QUOTE_PATTERN.sub(b'', content)
    # Collapse newlines to single spaces
    content = WHITESPACE_PATTERN.sub(b' ', content).strip()
    # Remove start of quote
    content = QUOTE_START_PATTERN.sub(b'', content)
    return content
