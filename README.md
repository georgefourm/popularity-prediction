# Micro-video popularity prediction
This repository is dedicated to the prediction of the popularity of micro-videos on the TikTok platform,
using the audio features extracted from non-original audio using Spotify's API. The task is modelled first 
as a regression task, then a multiclass and then a binary classification task.

## Project Structure
The project is structured into the following top-level directories, 
partially inspired by [Cookie Cutter Data Science](https://drivendata.github.io/cookiecutter-data-science/):
- `src`: Code for creating/updating the dataset and evaluation code for the models
- `bin`: The command-line interface for the code in `src`, explained in the "Usage" section below.
- `data`: The collected data. The `raw` folder contains the track data from TikTok, and the `interim` folder contains
the track data with the features fetched from the Spotify API. The `processed` folder contains the final dataset after
removing missing or invalid values.
- `notebooks`: This folder contains the exploration and modelling of the dataset using different approaches.

## Requirements
The only requirement for this package to work is Python >= 3.9. Using venv is suggested.

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

To run the view data collection, from the root directory run `python -m bin.download_views`. You can use the `-h` 
flag to display available options. The command will run until no new tracks are encountered.

To run the feature data collection, again from the root directory run `python -m bin.download_features`.

There is also a `bin.merge_views` command that can be used to merge view data files retrieved by the
`download_views` command. This can be useful, for example, in a distributed setting where multiple scraping agents
are launched, in order to merge results from all of them into a single file.