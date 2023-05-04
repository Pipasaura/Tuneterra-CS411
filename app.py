import flask
import spotipy
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask_login
from riot import getPlaylist
from spotify import linkDresser, playlistID, devicePicker
import requests

from secrets import databasePassword, secretAppKey, clientSecret

mysql = MySQL()
app = Flask(__name__)
app.secret_key = secretAppKey()

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = databasePassword()
app.config['MYSQL_DATABASE_DB'] = 'TuneTerra'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users")
users = cursor.fetchall()

def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from Users")
	return cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['password'] == pwd
	return user

authorization_base_url = "https://accounts.spotify.com/authorize"
token_url = "https://accounts.spotify.com/api/token"
username = 'TuneTerra'
clientID = '8f58798abaf548f0a1a92980022659db'
clientSecret = clientSecret()
redirectURI = 'https://google.com'
scope = ["user-modify-playback-state", "user-read-playback-state", "user-read-currently-playing"]
auth_token = None


from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth
spotify = OAuth2Session(clientID, scope=scope, redirect_uri=redirectURI)
authorization_url, state = spotify.authorization_url(authorization_base_url)

@app.route('/auth', methods=['GET'])
def auth():
    return render_template('auth.html', auth=authorization_url)

@app.route('/auth', methods=['POST'])
def auth_success():
    url = request.form.get('url')
    code = url[(len(redirectURI) + 11):]

    for i in range(len(code)):
        if code[i] == '&':
            code = code[:i]
            break

    auth = HTTPBasicAuth(clientID, clientSecret)
    global auth_token
    auth_token = spotify.fetch_token(token_url, auth=auth, code=code)

    return render_template('auth_success.html')

@app.route('/search', methods=['GET'])
def search():
    return render_template('search.html')

@app.route('/search', methods=['POST'])
def result():
    global auth_token
    sum_name = request.form.get('sum_name')
    region = request.form.get('region')
    playlist = getPlaylist(region, sum_name)
    src = linkDresser(playlist)
    sp = spotipy.Spotify(auth=auth_token['access_token'])
    devices = sp.devices()
    device = devicePicker(devices)
    songs = sp.playlist_items(playlist_id=playlistID(playlist), fields="items(track(id))", limit=20, offset=0)
    songs_ids = []
    for i in songs['items']:
        songs_ids += [i['track']['id']]
    for i in songs_ids:
        sp.add_to_queue(i, device_id=device)
    return render_template('playlist.html', playlist=playlist, src=src)


@app.route('/', methods=['GET'])
def home_page():
    return render_template('home.html')

if __name__ == "__main__":
    app.run(port=5000, debug=True)