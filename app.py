import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask_login
from riotwatcher import LolWatcher

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'rperry'  # Change this!

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'PUT YOURS HERE'
app.config['MYSQL_DATABASE_DB'] = 'TuneTerra'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

conn = mysql.connect()

api_key = 'RGAPI-58a0e207-818e-4000-a22c-5bb4204bfe8a' # Must be changed daily until product is (hopefully) registered.

watcher = LolWatcher(api_key, default_status_v4=True)

region = 'na1' # Will need a way to dynamically change this value if we want support for other reigions.

def getLiveChampId(region, sum_name):
    # Returns the champion ID number for a player in a live game
    try:
        sum_info = watcher.summoner.by_name(region, sum_name)
    except:
        print("Not a valid summoner name/region combo.")
        return
    sum_id = sum_info["id"]
    try:
        match_info = watcher.spectator.by_summoner(region, sum_id)
    except:
        print("Player not currently in game.") # Can either call function for non-live playlists, or have a check before calling this function to ensure user is in game.
        return
    participants = match_info["participants"]
    for i in range(10):
        #Probably a cleaner way to do this
        if (participants[i]["summonerName"] == sum_name):
            return participants[i]["championId"]
    return

def getPlaylist(region, sum_name):
    champ_id = getLiveChampId(region, sum_name)
    cursor = conn.cursor()
    playlist = cursor.execute("SELECT playlist1, playlist2 FROM Champions WHERE champ_id = %s", (champ_id))
    return cursor.fetchall()


    
    

