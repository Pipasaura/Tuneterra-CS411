from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
import time
import main

username = 'TuneTerra'
clientID = '4fe47df343244305b0c182bf3256a014'
clientSecret = '44d7366723e44e0b80661de489b0b521'
redirectURI = 'http://localhost:8888/callback'
scope = "user-read-playback-state"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
client_sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
authorization_base_url = "https://accounts.spotify.com/authorize"
token_url = "https://accounts.spotify.com/api/token"
spotify = OAuth2Session(clientID, scope=scope, redirect_uri=redirectURI)
authorization_url, state = spotify.authorization_url(authorization_base_url)
print('Please go here and authroize: ', authorization_url)
redirect_response = input('\n\nPaste the full redirect URL here: ')
code = redirect_response[len(redirectURI) + 5:]

for i in range(len(code)):
    if code[i] == '&':
        code = code[:i]
        break

auth = HTTPBasicAuth(clientID, clientSecret)
full_token = spotify.fetch_token(token_url, auth=auth, code=code)


def addSongtoQ(client: spotipy.Spotify, track_uri):
    track_info = client.audio_features(track_uri)
    song_duration = track_info['duration_ms']
    # gets the song's duration in ms
    client.add_to_queue(track_uri)
    # adds the song to the queue
    return song_duration


def extractPlaylist(playlist_url: str):
    playlist_url.replace("https://open.spotify.com/playlist/", "")
    results = client_sp.playlist(playlist_url)
    return results
    # figure out what sp.playlist returns and parse it into an array of song uris


def playbackController(client: spotipy.Spotify, playlist):
    current_champ = main.champStatus()
    timer = addSongtoQ(client, playlist[0])
    timer = timer - 5000
    time.sleep(timer / 1000)
    t_end = time.time() + 5
    while time.time() < t_end:
        if main.champStatus() != current_champ or len(playlist) <= 0:
            return
        else:
            playbackController(client, playlist[1:])

    if len(playlist) >= 2:
        addSongtoQ(client, playlist[1])
        return
    else:
        return
