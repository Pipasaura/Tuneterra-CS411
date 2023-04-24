from flask import Flask, request, jsonify, render_template
import userdata

app = Flask(__name__)

user_cache = {}

# Status codes
SC100 = {"status": 100}  # Server acknowledges request
SC200 = {"status": 200}  # Server has completed the request

# Error codes
EC400 = {"status": 400}  # Bad client request


# set this up to pull from the database/cache later on
# Login page endpoints

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

    return render_template('Search Page.html', template_folder='Front_end')


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
#       Set up champion detection and playlist selection
#       Figure out how to properly return stuff to frontend

def champStatus():
    return
