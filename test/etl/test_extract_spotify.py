import pytest
import spotipy
from src.etl.extract_spotify import get_auth
from src.etl.config import *

class TestGetAuth:
    @pytest.mark.skipif(
        get_auth(USERNAME, CLIENT_ID[:-1], CLIENT_SECRET, REDIRECT_URI),
        reason='Will fail if a token is saved from a previous successful auth.'
    )
    def test_incorrect_arg(self):
        with pytest.raises(ValueError):
            get_auth(USERNAME, CLIENT_ID[:-1], CLIENT_SECRET, REDIRECT_URI)

    def test_successful_auth(self):
        assert isinstance(
            get_auth(USERNAME, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI), 
            spotipy.client.Spotify)\
        , 'does not return client'
    
    def test_missing_arg(self):
        with pytest.raises(TypeError):
            get_auth(None, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
        
        with pytest.raises(spotipy.SpotifyException):
            get_auth(USERNAME, None, CLIENT_SECRET, REDIRECT_URI)
            get_auth(USERNAME, CLIENT_ID, None, REDIRECT_URI)
            get_auth(USERNAME, CLIENT_ID, CLIENT_SECRET, None)
    
    
        