from pptx.shapes.autoshape import autoshape_types
import re
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

endpoint_counter = {}

def test(endpoint: str, json_data: dict):
    endpoint_name = re.sub("/", "", endpoint)
    if endpoint_name not in endpoint_counter:
        endpoint_counter[endpoint_name] = 0
    endpoint_counter[endpoint_name] += 1
    print(f"UT.{endpoint_name.upper()}.{endpoint_counter[endpoint_name]}", end=" - ")
    res = requests.post(url + endpoint, json=json_data)
    print(res.json())
    globals()["song"] = cp(EXAMPLE_SONG)
    reset_db()

# print([s for s in song_list.find()])
# print(len([s for s in song_list.find()]))


######################################################################
# Explanation: the song value and database get reset upon every test #
######################################################################

###################
# Method: `/save` #
###################

# UT.SAVE.1 - Valid save: "Valid Save"

body = {
    "data": song,
    "authToken": "top_secret_auth_token"
}
test("/save", body)

# UT.SAVE.2 - User not authenticated: "User not authenticated"

body = {
    "data": song,
}
test("/save", body)

# UT.SAVE.3 - Invalid user authentication: "Invalid user authentication"

body = {
    "data": song,
    "authToken": "some_invalid_auth_token"
}
test("/save", body)

# UT.SAVE.4 - No song id provided: "No song id provided"

del song["songId"]
body = {
    "data": song,
    "authToken": "top_secret_auth_token"
}
test("/save", body)


# UT.SAVE.5 - No song lyrics provided: "No song lyrics provided"

del song["slides"]
body = {
    "data": song,
    "authToken": "top_secret_auth_token"
}
test("/save", body)

# UT.SAVE.6 - Song doesn't already exist: "Valid Save"

# songId is already unique
body = {
    "data": song,
    "authToken": "top_secret_auth_token"
}
test("/save", body)

# UT.SAVE.7 - Song already exists: "Valid Save"

# songId of song already in db
song["songId"] = "111"
body = {
    "data": song,
    "authToken": "top_secret_auth_token"
}
test("/save", body)

###################
# Method: `/load` #
###################

# UT.LOAD.1 - User not authenticated: "User not authenticated"

body = {
}
test("/load", body)

# UT.LOAD.2 - Invalid user authentication: "Invalid user authentication"

body = {
    "authToken": "some_invalid_auth_token"
}
test("/load", body)

# UT.LOAD.3 - User has 0 songs: "[]"

# delete all songs (which includes all songs for user)
song_list.delete_many({})
body = {
    "authToken": "top_secret_auth_token"
}
test("/load", body)

# UT.LOAD.4 - User has 1 song: "[{...}]"

# delete all songs (which includes all songs for user)
song_list.delete_many({})
# create 1 song so that there is only 1 song
song_list.insert_one(song)
body = {
    "authToken": "top_secret_auth_token"
}
test("/load", body)

# UT.LOAD.5 - User has 1+ songs: "[{...},{...},...]"

# there are multiple songs already in the database
body = {
    "authToken": "top_secret_auth_token"
}
test("/load", body)

#####################
# Method: `/delete` #
#####################

# UT.DELETE.1 - User not authenticated: "User not authenticated"

body = {
    "data": {
        "songId": 111
    },
}
test("/delete", body)

# UT.DELETE.2 - Song doesn't exist: "Song doesn't exist"

# this song does not exist
body = {
    "data": {
        "songId": -1
    },
    "authToken": "top_secret_auth_token"
}
test("/delete", body)

# UT.DELETE.3 - Song doesn't belong to authenticated user: "Invalid user authentication"

body = {
    "data": {
        "songId": 111
    },
    "authToken": "auth_token_for_other_user"
}
test("/delete", body)

# UT.DELETE.4 - Valid song delete successful: "Valid song delete successful"

body = {
    "data": {
        "songId": 111
    },
    "authToken": "top_secret_auth_token"
}
test("/delete", body)

#####################################
# Method: `/send_verification_code` #
#####################################

# UT.SEND_VERIFICATION_CODE.1 - No verification email address provided: "No verification email address provided"

body = {
    "data": {
    },
}
test("/send_verification_code", body)

# UT.SEND_VERIFICATION_CODE.2 - Email address is invalid: "Email address is invalid"

# body = {
#     "data": {
#         # "emailAddress": "some.email.that.does.not.exist@idonotexistmail.com"
#         "emailAddress": "some.email.that.does.not.exist@biola.edu"
#     },
# }
# test("/send_verification_code", body)

# UT.SEND_VERIFICATION_CODE.3 - Email address is valid: "Email address is valid"

# body = {
#     "data": {
#         "emailAddress": "blake.scampone@biola.edu"
#     },
# }
# test("/send_verification_code", body)

###########################
# Method: `/verify_login` #
###########################

# UT.VERIFY_LOGIN.1 - No verification email address provided: "No verification email address provided"

body = {
    "data": {
        "loginCode": 777777,
    },
}
test("/verify_login", body)

# UT.VERIFY_LOGIN.2 - No verification code provided: "No verification code provided"

body = {
    "data": {
        "emailAddress": "some.email@gmail.com",
    },
}
test("/verify_login", body)

# UT.VERIFY_LOGIN.3 - Incorrect verification code provided: "Incorrect verification code provided"

# correct code is 777777
body = {
    "data": {
        "emailAddress": "some.email@gmail.com",
        "loginCode": 111111,
    },
}
test("/verify_login", body)

# UT.VERIFY_LOGIN.4 - Valid verification

body = {
    "data": {
        "emailAddress": "some.email@gmail.com",
        "loginCode": 777777,
    },
}
test("/verify_login", body)

#####################
# Method: `/export` #
#####################

# UT.EXPORT.1 - User Not Authenticated



# UT.EXPORT.2 - Lyrics not provided



# UT.EXPORT.3 - Title slide requested



# UT.EXPORT.4 - Title slide not requested



