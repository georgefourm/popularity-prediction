# Micro-video popularity prediction
This repository is dedicated to popularity prediction of micro-videos on the TikTok platform,
using the audio features extracted from non-original audio using Spotify's API.

## Requirements
The only requirement for this package to work is Python >= 3.9

## Setup
Run `pip install -r requirements.txt` to install dependencies, then create a `.env` file as a copy of the `.env-example` file, and fill
out the values. To properly scrape TikTok data, 3 different values are needed, which you can get by opening
your browser to the front page of TikTok (no need to be logged in), and examining the outgoing requests:

- `TT_COOKIE` : The cookie value sent with all requests. You can find this in any request header.
- `TT_DEVICE_ID` : The device id assigned to the requesting browser. It is available on the query parameters any request.
- `TT_TOKEN`: It is not entirely clear if this value is needed, but it is contained in another cookie stored in the browser
named `s_v_web_id`. Copy the entire cookie value, it should be in the form `verify_*`.

Note that because this code is using the internal, undocumented TikTok API, the parameters and end endpoints are subject
to change, and so there is no guarantee that it will continue to work.

For the `SPOTIFY_* values`, an app must be created from 
Spotify's [dashboard for developers](https://developer.spotify.com/dashboard/). The client ID and secret of this app
is used here to access the API.

## Usage
The data collection is a two-step process. First, the view data along with the tracks and album names are 
downloaded from the TikTok API, and then the audio features of each track are retrieved from the Spotify API.

To run the view data collection, from the root directory run `python bin/view_scrape.py`. You can use the `-h` 
flag to display available options.

To run the feature data collection, again from the root directory run `python bin/audio_scrape.py`.