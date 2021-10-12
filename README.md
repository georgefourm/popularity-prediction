# Micro-video popularity prediction
This repository is dedicated to popularity prediction of micro-videos on the TikTok platform,
using the audio features extracted from non-original audio using Spotify's API.

## Installation
Run `pip install` to install dependencies, then create a `.env` file as a copy of the `.env-example` file, and fill
out the values. To get the TT_* values, open the front page of TikTok, examine the XHR requests, and retrieve
the cookie value and device id. The token is not necessary.