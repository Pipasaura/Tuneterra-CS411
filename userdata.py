from flask import jsonify


# Class declarations and methods for user data manipulation
class User:
    def __init__(self, userid):
        self.userid = userid
        self.token = None
        self.summoner = []

    def jsonify(self):
        # returns a json of the user object's fields
        entry = {"userid": self.userid, "token": self.token, "summoner": self.summoner}
        return jsonify(entry)
