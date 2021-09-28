from ietfdata.mailarchive import MailArchive
from dotenv import load_dotenv
import os

load_dotenv()

archive = MailArchive()
m_list = archive.mailing_list(os.getenv("IETF_MAIL_LIST"))
messages = m_list.messages()

