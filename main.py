from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

OAuthTokens = {}


# set this up to pull from the database/cache later on

@app.get("/oauth_token")
def give_oauth_token():
    user = request.form["userid"]
    return OAuthTokens[user]


@app.post("/oauth_token")
def store_oauth_token():
    data = request.get_json()
    OAuthTokens[data["userid"]] = data["oauth_token"]
    return render_template('Search Page.html', template_folder='Front_end')


@app.patch("/oauth_token")
def update_token():
    OAuthTokens[request.form["userid"]] = request.get_json()["token"]


@app.delete("/oauth_token")
def remove_token():
    OAuthTokens[request.form["userid"]] = ""


def champStatus():
    return
