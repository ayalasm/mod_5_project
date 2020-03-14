import requests
import time
import config
import json

"""
REQUEST OAUTH TOKEN
------------------
"""
# Set parameters for the POST request. Based on Spotify OAuth documentation.
auth_url = 'https://accounts.spotify.com/api/token'
auth_params = {'grant_type':'client_credentials'}
auth_header = {'Authorization':'Basic MGY3MTFjMjM1OGI0NDIzNGEyNWJiMDc1MWJkNTdjYTY6OTg4NjRlYjc0ODYyNGE3OTg4MDRhMjlhOWNiODRmNDg='}

# Make request and retrieve a token
auth_response = requests.post(url = auth_url, data = auth_params,headers=auth_header)
token = auth_response.json()['access_token']

"""
HELPERS FOR API CALL AND PARSING
--------------------------------
"""

def api_call(kind, token, params = None, id_ = None):
    """
    RETURNS
    -------
    JSON object with API call results.

    PARAMETERS
    -----------
    kind: [str] must be in `allowed kinds` below.

    params: [dict] optional search parameters. Depends on the type of search. Consult
        Spotify API documentation referenced at the top of the notebook for proper input.
        Will be None if id_ is NOT None.

    id_: [str] optional id used for any search requiring an id input. Will be None
        if params is NOT None.

    token: [str] the active OAuth token.
    """
    # Set the allowed kinds of api calls
    allowed_kinds = ['search', 'artist', 'features', 'tracks', 'albums',
                     'album_tracks', 'multiple_albums', 'analysis']

    # Assert that user requested an allowed kind of api call
    assert kind in allowed_kinds, f'Please use from the api call types {allowed_kinds}'

    # Set the appropriate url based on the specified `kind`
    urls = {'search':'https://api.spotify.com/v1/search',
            'artists':'https://api.spotify.com/v1/artists/',
            'albums':f'https://api.spotify.com/v1/artists/{id_}/albums',
            'album_tracks':f'https://api.spotify.com/v1/albums/{id_}/tracks',
            'analysis':f'https://api.spotify.com/v1/audio-analysis/{id_}',
            'features':f'https://api.spotify.com/v1/audio-features/{id_}',
            'tracks':f'https://api.spotify.com/v1/tracks/{id_}'}
    url = urls[kind]

    # Set call authorization
    auth = {'Authorization':f'Bearer {token}'}

    return requests.get(url, params = params, headers = auth).json()

def parse_search(search_results):
    """
    RETURNS
    -------
    A string of the id associated with the search result.

    PARAMETERS
    ----------
    search_results: [JSON] the output of the api_call function with 'search'
        used as the first argument.
    """
    return search_results['artists']['items'][0]['id']

def parse_features(features_results):
    """
    RETURNS
    -------
    A dictionary from the analysis_results with only relevant key:value pairs.

    PARAMETERS
    ----------
    features_results: [JSON] the output of the api_call function with 'features'
        used as the first argument.
    """

    # List keys to ignore from features_results
    irrelevant_keys = ['uri','track_href','analysis_url','type']

    # Keep only the key:value pairs we care about
    return {key:features_results[key]
            for key in features_results
            if key not in irrelevant_keys}

def parse_tracks(tracks_results):
    """
    RETURNS
    -------
    A dictionary from the tracks_results with only relevant key:value pairs.
    Param features_results: [JSON] the output of the api_call function with 'tracks'
        used as the first argument.
    """
    # Empty container for parsed track info
    result = {}

    # Store only the following key:pair info in result
    result['track_name'] = tracks_results['name']
    result['album_name'] = tracks_results['album']['name']
    result['artists'] = [dict_['name']
                         for dict_ in tracks_results['album']['artists']]
    result['release_date'] = tracks_results['album']['release_date']

    return result

"""
API CALLS AND PARSING
---------------------------

1. Start with artist names to get Spotify artist IDs
2. Using artist IDs, get up to 50 album IDs per artist
3. Pass Album IDs into album_tracks call to get each individual track's info
4. Pass track ids into analysis, features, and track info calls
5. Maybe MySQL tables? Then can combine necessary things when you want?
"""

# Manually pick artists whose music we'll explore. 4 Salsa, 4 Bachata.
artists = ["Oscar D'León", "Frankie Ruiz", "Tito Nieves", "La Maxima 79",
               "Aventura", "Monchy & Alexandra", "Prince Royce", "Romeo Santos"]

# Container to store their ids
artist_ids = {}

# Iterate through artist names
for artist in artists:

    # Set search params.
    params = {
          'q':f'{artist}',   # Search Query: [str] spaces must be separated by %20 or +
          'type':'artist',   # Type of response: [str | comma sep optional] album, artist, playlist, and track
          'limit':None,      # No. of responses: [int] default is 20. Can be (1, 50)
          'offset':None      # Index of where to start in the search results. Can be (1, 100,000)
    }

    # Append entry to our dict with {artist_name : artist_id}
    search_results = api_call('search', token, params)
    artist_ids[artist] = parse_search(search_results)
