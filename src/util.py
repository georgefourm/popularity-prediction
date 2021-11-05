import os

import requests
from progress.bar import Bar


def scrape_views(total_count: int):
    url = "https://m.tiktok.com/api/recommend/item_list/"
    batch_limit = 35

    cookie = os.getenv("TT_COOKIE")
    token = os.getenv('TT_TOKEN', None)
    device_id = os.getenv('TT_DEVICE_ID', None)

    params = {
        "aid": 1988,
        "count": batch_limit,
        "verifyFp": token,
        "device_id": device_id
    }

    bar = Bar("Downloading batch...", max=total_count)
    downloaded = []

    while len(downloaded) < total_count:
        requests.head(url, params=params)

        headers = {
            "cookie": cookie
        }

        response = requests.get(url, params=params, headers=headers)

        content = response.json()
        items = content['itemList']

        if len(items) == 0:
            break

        bar.next(len(items))
        downloaded += items

    bar.finish()

    return downloaded
