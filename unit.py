from pptx.shapes.autoshape import autoshape_types
import requests
import os
from copy import deepcopy as cp
from pymongo import MongoClient
from dotenv import load_dotenv
import json

url = "http://127.0.0.1:5000"

load_dotenv()
# connect to database
DB_NAME="lyric-of-lyric-db-test-001"
DB_URI="mongodb://localhost:27017/"
client = MongoClient(DB_URI)
db = client[DB_NAME]

# list of all songs by user
song_list = db["song_list"]
# auth tokens that correspond to user
user_logins = db["user_logins"]
# verification codes for email
email_codes = db["email_codes"]

def reset_db():
    with open("song_list.json", "r") as f:
        song_list.delete_many({})
        song_list.insert_many(json.loads(f.read()))
    with open("user_logins.json", "r") as f:
        user_logins.delete_many({})
        user_logins.insert_many(json.loads(f.read()))
    with open("email_codes.json", "r") as f:
        email_codes.delete_many({})
        email_codes.insert_many(json.loads(f.read()))

# put necessary data in database for test
EXAMPLE_SONG = {
    "title": "Song Title",
    "author": "Song Author",
    "songId": "12345678",
    "emailAddress": "some.email@gmail.com",
    "lines": [
        { "text": "Slide 1 Line 1", "divider": False, },
        { "text": "Slide 1 Line 2", "divider": False, },
        { "text": "Slide 1 Line 3", "divider": False, },
        { "text": "Slide 1 Line 4", "divider": True,  },
        { "text": "Slide 2 Line 1", "divider": False, },
        { "text": "Slide 2 Line 2", "divider": False, },
        { "text": "Slide 2 Line 3", "divider": False, },
        { "text": "Slide 2 Line 4", "divider": True,  },
        { "text": "Slide 3 Line 1", "divider": False, },
        { "text": "Slide 3 Line 2", "divider": False, },
        { "text": "Slide 3 Line 3", "divider": False, },
        { "text": "Slide 3 Line 4", "divider": True,  },
    ],
    "slides": [
        [
            "Slide 1 Line 1",
            "Slide 1 Line 2",
            "Slide 1 Line 3",
            "Slide 1 Line 4",
        ],
        [
            "Slide 2 Line 1",
            "Slide 2 Line 2",
            "Slide 2 Line 3",
            "Slide 2 Line 4",
        ],
        [
            "Slide 3 Line 1",
            "Slide 3 Line 2",
            "Slide 3 Line 3",
            "Slide 3 Line 4",
        ],
    ],
    "settings": {
        "textColor": "#ffffff",
        "backgroundColor": "#000000",
        "numberOfColumns": 5,
        "fontSize": 36,
        "fontFamily": "Arial",
        "includeTitleSlide": "true"
    },
}

song = cp(EXAMPLE_SONG)

body = {
    "data": song,
    # "authToken": "top_secret_auth_token"
}

reset_db()
# print([s for s in song_list.find()])
print(len([s for s in song_list.find()]))
res = requests.post(url + "/save", json=body)
print(res.json())
print(len([s for s in song_list.find()]))
