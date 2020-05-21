import spotipy
from .config import *
from .consts import *

def get_auth(username, client_id, client_secret, redirect_uri):
    """
    Attempts to get a Spotify API authentication token.

    Returns
    -------
    A spotify.Spotify client object if a token is retrieved. Else, gives a
    failure message.
    """
    token = spotipy.util.prompt_for_user_token(
        username = username,
        client_id = client_id,
        client_secret = client_secret,
        redirect_uri = redirect_uri
    )

    if token:
        print(token)
        sp = spotipy.Spotify(auth=token)
        return sp

    else:
        raise ValueError("Can't get token for {}. Check auth.".format(username))

if __name__ == '__main__':
    # print(get_auth(USERNAME, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI))
    print(get_auth(USERNAME, CLIENT_ID[:-1], CLIENT_SECRET, REDIRECT_URI))