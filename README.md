# Micro-video popularity prediction
This repository is dedicated to popularity prediction of micro-videos on the TikTok platform,
using the audio features extracted from non-original audio using Spotify's API.

## Installation
Run `pip install -r requirements.txt` to install dependencies, then create a `.env` file as a copy of the `.env-example` file, and fill
out the values. To get the TT_* values, open the front page of TikTok, examine the XHR requests, and retrieve
the cookie value and device id. The token is not necessary.

## Usage
The data collection is a two-step process. First, the view data along with the tracks and album names are 
downloaded from the TikTok API, and then the audio features of each track are retrieved from the Spotify API.

To run the view data collection, from the root directory run `python bin/view_scrape.py`. You can use the `-h` 
flag to display available options.

To run the feature data collection, again from the root directory run `python bin/audio_scrape.py`.