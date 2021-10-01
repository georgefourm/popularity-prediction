from ietfdata.datatracker import DataTracker
import pandas as pd
from progress.spinner import Spinner
import os

DRAFT_SLUG = "draft"


def download_drafts(group_acronym: str, datatracker=None, output_dir="data/raw"):
    if datatracker is None:
        datatracker = DataTracker()

    group = datatracker.group_from_acronym(group_acronym)
    docs = datatracker.documents(group=group)

    doc_dict = []
    event_dict = []

    bar = Spinner("Downloading Documents...", suffix='%(index)d%')
    output_path = os.path.join(output_dir, group_acronym)

    if not os.path.exists(output_path):
        os.mkdir(output_path)

    for doc in docs:
        doctype = datatracker.document_type(doc.type)
        if doctype.slug != DRAFT_SLUG:
            continue
        doc_dict.append({
            "id": doc.id,
            "name": doc.name,
            "title": doc.title,
            "timestamp": doc.time,
            "rfc_number": doc.rfc,
            "expires": doc.expires,
            "revision": doc.rev,
        })
        events = datatracker.document_events(doc=doc)

        for event in events:
            event_dict.append({
                "id": event.id,
                "doc_id": doc.id,
                "type": event.type,
                "timestamp": event.time,
                "description": event.desc,
            })
            bar.next()
        bar.next()

    doc_df = pd.DataFrame(doc_dict)
    event_df = pd.DataFrame(event_dict)

    doc_df.to_pickle(os.path.join(output_path, "documents.pkl"))
    event_df.to_pickle(os.path.join(output_path, "events.pkl"))
