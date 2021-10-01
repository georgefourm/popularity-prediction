from dotenv import load_dotenv

from src.data.emails import download_emails
from src.data.documents import download_drafts

load_dotenv()

download_drafts("webtrans")
download_emails("webtransport")
