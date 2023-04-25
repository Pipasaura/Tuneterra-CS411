import base64
import json
import os
import time
from urllib.parse import urlencode

import requests
from flask import Flask, request, jsonify, render_template, session, make_response, redirect, logging
from authlib.integrations.flask_client import OAuth
from numpy.random.mtrand import rand
from flaskext.mysql import MySQL

import spotify
import userdata
import string
import secrets

template_dir = os.path.abspath('Front_end')
SPOTIFY_URL_AUTH = 'https://accounts.spotify.com/authorize/?'
SPOTIFY_URL_TOKEN = 'https://accounts.spotify.com/api/token/'
RESPONSE_TYPE = 'code'
HEADER = 'application/x-www-form-urlencoded'
REFRESH_TOKEN = ''
app = Flask(__name__, template_folder=template_dir)
oauth = OAuth(app)
user_cache = {}
# Status codes
SC100 = {"status": 100}  # Server acknowledges request
SC200 = {"status": 200}  # Server has completed the request

# Error codes
EC400 = {"status": 400}  # Bad client request

# set this up to pull from the database/cache later on
# Login page endpoints
client_id = '4fe47df343244305b0c182bf3256a014'
clientSecret = '44d7366723e44e0b80661de489b0b521'
redirect_uri = 'http://localhost:8888/callback'
scope = "user-read-playback-state"


@app.route('/')
def home():
    return render_template('Login Page.html')


app.run()


def generate_state_key(size):
    return secrets.token_urlsafe(size)


@app.route('/authorize', methods=['GET'])
def authorize():
    state_key = generate_state_key(15)
    session['state_key'] = state_key

    authorize_url = 'https://accounts.spotify.com/en/authorize?'
    params = {'response_type': 'code', 'client_id': client_id,
              'redirect_uri': redirect_uri, 'scope': scope,
              'state': state_key}
    query_params = urlencode(params)
    response = make_response(redirect(authorize_url + query_params))
    return response


def get_token(code):
    token_url = 'https://accounts.spotify.com/api/token'
    authorization = "Bearer " + clientSecret
    headers = {'Authorization': authorization, 'Accept': 'application/json',
               'Content-Type': 'application/x-www-form-urlencoded'}
    body = {'code': code, 'redirect_uri': redirect_uri, 'grant_type': 'authorization_code'}
    post_response = requests.post(token_url, headers=headers, data=body)
    if post_response.status_code == 200:
        pr = post_response.json()

        return pr['access_token'], pr['refresh_token'], pr['expires_in']
    return None


def handle_token(response):
    auth_head = {"Authorization": "Bearer {}".format(response["access_token"])}
    global REFRESH_TOKEN
    REFRESH_TOKEN = response["refresh_token"]
    return [response["access_token"], auth_head, response["scope"], response["expires_in"]]


@app.route('/callback')
def callback():
    # make sure the response came from Spotify
    if request.args.get('state') != session['state_key']:
        return render_template('Login Page.html', error='State failed.')
    if request.args.get('error'):
        return render_template('Login Page.html', error='Spotify error.')
    else:
        code = request.args.get('code')
        session.pop('state_key', None)

        # get access token to make requests on behalf of the user
        payload = get_token(code)
        if payload is not None:
            session['token'] = payload[0]
            session['refresh_token'] = payload[1]
            session['token_expiration'] = time.time() + payload[2]
        else:
            return render_template('Login Page.html', error='Failed to access token.')

    current_user = session['user_id']
    session['user_id'] = current_user['id']

    return redirect(session['previous_url'])


# check API endpoints.txt for descriptions of what these do
@app.get("/oauth_token")
def give_oauth_token():
    user = request.form["userid"]
    return user_cache[user]


@app.post("/oauth_token")
def store_oauth_token():
    data = request.get_json()
    user_id = data["userid"]
    if data is not None:
        current_user = userdata.User(user_id)
        current_user.token = data["token"]
        user_cache[user_id] = current_user
    else:
        return jsonify(EC400)

    return render_template('Search Page.html')


@app.patch("/oauth_token")
def update_token():
    if request.form is not None:
        user_cache[request.form["userid"]].token = request.get_json()["token"]

    else:
        return jsonify(EC400)


@app.delete("/oauth_token")
def remove_token():
    if request.form is not None:
        user_cache[request.form["userid"]].token = None

    else:
        return jsonify(EC400)


# Search page endpoints
summoner_lookup = {}


# temporary dict that links a summoner name to a user id for quick lookup
# store dict in database after use - only pull entries relevant to current userid
# I'll implement this after we ge the main api working -Nathan


@app.post("/summoner")
def link_summoner():
    if request.form is not None:
        user = request.form["userid"]
        summoner_name = request.form["summoner_name"]
        user_cache[user].summoner.append(summoner_name)

    else:
        return jsonify(EC400)


@app.get("/summoner")
def retrieve_summoner_data():
    if request.form is not None:
        summoner_name = request.form["summoner"]
        user = summoner_lookup[summoner_name]
        return user_cache[user].jsonify()

    else:
        return jsonify(EC400)


# todo: Verification of summoner name
#       Figure out status codes

def champStatus():
    return
