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
"""
1. Start with artist names to get Spotify artist IDs
"""
# Manually pick artists whose music we'll explore. 4 Salsa, 4 Bachata.
artists = {
    'salsa':["Oscar D'León", "Frankie Ruiz","Tito Nieves", "La Maxima 79"],
    'bachata':["Aventura", "Monchy & Alexandra", "Prince Royce", "Romeo Santos"]
}
# Container to store their ids
artist_ids = {
    'salsa':{},
    'bachata':{}
}
# Iterate through each genre and then through each artist name
for genre in ['salsa', 'bachata']:
    for artist in artists[genre]:

        # Set search params.
        params = {
              'q':f'{artist}',   # Search Query: [str] spaces must be separated by %20 or +
              'type':'artist',   # Type of response: [str | comma sep optional] album, artist, playlist, and track
              'limit':None,      # No. of responses: [int] default is 20. Can be (1, 50)
              'offset':None      # Index of where to start in the search results. Can be (1, 100,000)
        }

        # Make API call and then parse to append id to artist_ids
        search_results = api_call('search', token, params)
        artist_ids[genre][artist] = parse_search(search_results)

"""
2. Using artist IDs, get up to 50 album IDs per artist
"""

# Empty dict to store results
artist_album_ids = {
    'salsa':{},
    'bachata':{}
}

for genre in ['salsa', 'bachata']:
    for artist in artist_ids[genre]:

        # Capture up to 50 albums by current artist in the loop
        params={'limit':20}

        # Make API call using artist ID of the current artist in the loop
        albums = api_call('albums', token, params=params, id_=artist_ids[genre][artist])

        # Generate list of the album ids for the current artist in the loop. Filter out albums
        # That are not entirely their own by restricting the album artist name to be only the name
        # of the current artist in the loop
        album_ids = [album['id']
                        for album in albums['items']
                        if album['artists'][0]['name'] == artist]

        # Add this list to a dict
        artist_album_ids[genre][artist] = album_ids

        # Wait a little bit to not get kicked off API
        time.sleep(0.25)


# """
# 3. Pass Album IDs into album_tracks call to get each individual track's info
# """
#
# # Partition artist list into salseros and bachateros so that
# # we can easily label genres later
# salseros = artists[:4]
# bachateros = artists[4:]
#
# # Set up track ID containers
# salsa_track_ids = []
# bachata_track_ids = []
#
# # Iterate through dict to get an individual artist
# for artist in artists_album_ids:
#
#     # Iterate through each artist's album ids
#     for album_id in artists_album_ids[artist]:
#
#         # Call API for album track info
#         tracks = api_call('album_tracks', token, id_=album_id)
#
#         # Iterate through each album's track's info
#         for track in tracks['items']:
#
#             # Extract song ids and sort into appropriate container
#             if artist in salseros:
#                 salsa_track_ids.append(track['id'])
#             else:
#                 bachata_track_ids.append(track['id'])
#
#         # Wait a moment
#         time.sleep(0.1)
#
# """
# 4. Pass track ids into analysis, features, and track info calls
# """
# def collect_data(track_ids,genre):
#     """
#     Returns a list of song data for each id passed into the function.
#     Param track_ids: [list of strings] must be valid Spotify song IDs.
#     Param genre: [str] must be either 'salsa' or 'bachata'
#     """
#     assert type(track_ids) == list, 'The argument passed as track_ids is not a list'
#     assert genre in ['salsa','bachata'], 'Pick a valid genre'
#
#     # Container for song data
#     result = []
#
#     # Iterate through track id list
#     for track_id in track_ids:
#
# #         print('start of the loop')
# #         print(f'track id is {track_id}')
#
#         # Call API for section data. See documentation for meanings
#         analysis_sections = {'sections':api_call('analysis', token, id_=track_id)['sections']}
#
#         # Call API for audio features and parse for relevant information
#         parsed_features = parse_features(api_call('features', token, id_=track_id))
#
#         # Call API for track info and parse for relevant information
#         parsed_track_info = parse_tracks(api_call('tracks', token, id_=track_id))
#
#
#         # Combine all these calls into a single dict, adding in genre
#         row = {**parsed_features, **parsed_track_info, **analysis_sections,'genre':genre}
#
#         # Append to container
#         result.append(row)
#
#         time.sleep(0.1)
#
#     return result
#
# salsa_track_data = collect_data(salsa_track_ids,'salsa')
# bachata_track_data = collect_data(bachata_track_ids,'bachata')
# all_track_data = salsa_track_data + bachata_track_data
