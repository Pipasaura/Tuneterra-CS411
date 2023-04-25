import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask_login
from riotwatcher import LolWatcher

mysql = MySQL()
app = Flask(__name__)
app.secret_key = ''  # Change this!

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'TuneTerra'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

conn = mysql.connect()

api_key = ''

watcher = LolWatcher(api_key, default_status_v4=True)


def getLiveChampId(region, match_info, sum_id):
    # Returns the champion ID number for a player in a live game
    participants = match_info["participants"]
    for i in range(10):
        #Probably a cleaner way to do this
        if (participants[i]["summonerId"] == sum_id):
            return str(participants[i]["championId"])
    return

def getPlaylists(region, sum_name):
    champ_id = getLiveChampId(region, sum_name)
    cursor = conn.cursor()
    cursor.execute("SELECT playlist1, playlist2 FROM Champions WHERE champ_id = %s", (champ_id))
    return cursor.fetchall()

def getMatchHistory(region, puuid):
    history = watcher.match.matchlist_by_puuid(region, puuid, count=3) # Returns the three most recent match ids
    match1 = watcher.match.by_id(region, history[0])
    match2 = watcher.match.by_id(region, history[1])
    match3 = watcher.match.by_id(region, history[2])
    matches = [match1, match2, match3]
    matches_wins = [False, False, False]
    for i in range(3):
        parts = matches[i]['info']['participants']
        for x in parts:
            if (x['puuid'] == puuid):
                matches_wins[i] = x['win']

    return matches_wins


def getLP(region, sum_id):
    info = watcher.league.by_summoner(region, sum_id)
    return info[0]['leaguePoints']

def getMatchHistoryInfo(region, sum_id, puuid):
    LP = getLP(region, sum_id)
    winLoss = getMatchHistory(region, puuid)
    return [LP, winLoss]

def getMatchHistoryKeyword(xs):
    LP = xs[0]
    winLoss = xs[1]
    winStreak = [True, True, True]
    lossStreak = [False, False, False]
    if (winLoss == winStreak):
        if (LP < 25):
            return 'Triumphant'
        else:
            return 'Upbeat'
    elif (winLoss == lossStreak):
        if (LP > 75):
            return 'Tragic'
        else:
            return 'Sad'
    else:
        if ((LP == 0) or (LP > 85)):
            return 'Inspiring'
        else:
            return 'Default'
        
def getMatchHistoryPlaylist(region, sum_id, puuid):
    keyword = getMatchHistoryKeyword(getMatchHistoryInfo(region, sum_id, puuid))
    return keyword

def getPlaylistID(region, sum_name):
    try:
        sum_info = watcher.summoner.by_name(region, sum_name)
    except:
        print("Not a valid summoner name/region combo!")
        return
    
    sum_id = sum_info['id']
    puuid = sum_info['puuid']

    try:
        match_info = watcher.spectator.by_summoner(region, sum_id)
        return getLiveChampId(region, match_info, sum_id)
    except:
        return getMatchHistoryPlaylist(region, sum_id, puuid)

def getPlaylist(region, sum_name):
    keyword = getPlaylistID(region, sum_name)
    cursor = conn.cursor()
    cursor.execute("SELECT playlist1 FROM Playlists WHERE playlist_id = %s", (keyword))
    return cursor.fetchall()

def checkInGameStatus(region, sum_name):
    try:
        sum_info = watcher.summoner.by_name(region, sum_name)
    except:
        print("Not a valid summoner name/region combo!")
        return
    try:
        sum_id = sum_info['id']
        match_info = watcher.spectator.by_summoner(region, sum_id)
    except:
        return False
    return True


def insertUserID(UserID):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Users(user_id) VALUES (%s)", (UserID))
    conn.commit()
    return True

def insertSumName(SumName, UserID):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO SummonerNames(sum_name, user_id) VALUES (%s, %s), (SumName, UserID)")
    conn.commit()
    return True

def getUserIDFromSumName(SumName):
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM SummonerNames WHERE sum_name = %s", (SumName))
    return cursor.fetchone()[0]

def getSumNamesFromUserID(UserID):
    cursor = conn.cursor()
    cursor.execute("SELECT sum_name FROM SummonerNames WHERE user_id = %s", (UserID))
    return cursor.fetchall()