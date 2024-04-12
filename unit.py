from textwrap import indent
from pptx.shapes.autoshape import autoshape_types
import re
import requests
import os
from copy import deepcopy as cp
from pymongo import MongoClient
from dotenv import load_dotenv
import json
import pandas as pd

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
        "includeTitleSlide": True
    },
}

song = cp(EXAMPLE_SONG)

endpoint_counter = {}

test_results = []

def test(endpoint: str, json_data: dict, description: str=""):
    endpoint_name = re.sub("/", "", endpoint)
    if endpoint_name not in endpoint_counter:
        endpoint_counter[endpoint_name] = 0
    endpoint_counter[endpoint_name] += 1
    log_id = f"UT.{endpoint_name.upper()}.{endpoint_counter[endpoint_name]}"
    print(log_id, end=" - ")
    res = requests.post(url + endpoint, json=json_data)
    if res.headers['Content-Type'] == 'application/json':
        log_message = json.dumps(res.json())
    else:
    # elif res.headers['Content-Type'] == 'application/vnd.openxmlformats-officedocument.presentationml.presentation':
        # path = f"test_outputs/{log_id}.pptx"
        os.makedirs('test_outputs', exist_ok=True)
        path = os.path.join('test_outputs', f"{log_id}.pptx")
        log_message = f"File saved to '{path}'."
        # print(res.content)
        with open(path, "wb") as file:
            file.write(res.content)

    print(log_message)

    test_results.append([
        log_id,
        json.dumps(json_data),
        log_message,
        description
    ])
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

# UT.SAVE.1 - Valid save

body = {
    "data": song,
    "authToken": "top_secret_auth_token"
}
test("/save", body, "Valid save")

# UT.SAVE.2 - User not authenticated

body = {
    "data": song,
}
test("/save", body, "User not authenticated")

# UT.SAVE.3 - Invalid user authentication

body = {
    "data": song,
    "authToken": "some_invalid_auth_token"
}
test("/save", body, "Invalid user authentication")

# UT.SAVE.4 - No song id provided

del song["songId"]
body = {
    "data": song,
    "authToken": "top_secret_auth_token"
}
test("/save", body, "No song id provided")


# UT.SAVE.5 - No song lyrics provided

del song["slides"]
body = {
    "data": song,
    "authToken": "top_secret_auth_token"
}
test("/save", body, "No song lyrics provided")

# UT.SAVE.6 - Song doesn't already exist

# songId is already unique
body = {
    "data": song,
    "authToken": "top_secret_auth_token"
}
test("/save", body, "Song doesn't already exist")

# UT.SAVE.7 - Song already exists

# songId of song already in db
song["songId"] = "111"
body = {
    "data": song,
    "authToken": "top_secret_auth_token"
}
test("/save", body, "Song already exists")

###################
# Method: `/load` #
###################

# UT.LOAD.1 - User not authenticated

body = {
}
test("/load", body, "User not authenticated")

# UT.LOAD.2 - Invalid user authentication

body = {
    "authToken": "some_invalid_auth_token"
}
test("/load", body, "Invalid user authentication")

# UT.LOAD.3 - User has 0 songs

# delete all songs (which includes all songs for user)
song_list.delete_many({})
body = {
    "authToken": "top_secret_auth_token"
}
test("/load", body, "User has 0 songs")

# UT.LOAD.4 - User has 1 song

# delete all songs (which includes all songs for user)
song_list.delete_many({})
# create 1 song so that there is only 1 song
song_list.insert_one(song)
body = {
    "authToken": "top_secret_auth_token"
}
test("/load", body, "User has 1 song")

# UT.LOAD.5 - User has 1+ songs

# there are multiple songs already in the database
body = {
    "authToken": "top_secret_auth_token"
}
test("/load", body, "User has 1+ songs")

#####################
# Method: `/delete` #
#####################

# UT.DELETE.1 - User not authenticated

body = {
    "data": {
        "songId": 111
    },
}
test("/delete", body, "User not authenticated")

# UT.DELETE.2 - Song doesn't exist

# this song does not exist
body = {
    "data": {
        "songId": -1
    },
    "authToken": "top_secret_auth_token"
}
test("/delete", body, "Song doesn't exist")

# UT.DELETE.3 - Song doesn't belong to authenticated user

body = {
    "data": {
        "songId": 111
    },
    "authToken": "auth_token_for_other_user"
}
test("/delete", body, "Song doesn't belong to authenticated user")

# UT.DELETE.4 - Valid song delete successful

body = {
    "data": {
        "songId": 111
    },
    "authToken": "top_secret_auth_token"
}
test("/delete", body, "Valid song delete successful")

#####################################
# Method: `/send_verification_code` #
#####################################

# UT.SEND_VERIFICATION_CODE.1 - No verification email address provided

body = {
    "data": {
    },
}
test("/send_verification_code", body, "No verification email address provided")

# UT.SEND_VERIFICATION_CODE.2 - Email address is invalid

body = {
    "data": {
        # "emailAddress": "some.email.that.does.not.exist@idonotexistmail.com"
        "emailAddress": "some.email.that.does.not.exist@biola.edu"
    },
}
test("/send_verification_code", body, "Email address is invalid")

# UT.SEND_VERIFICATION_CODE.3 - Email address is valid

body = {
    "data": {
        "emailAddress": "blake.scampone@biola.edu"
    },
}
test("/send_verification_code", body, "Email address is valid")

###########################
# Method: `/verify_login` #
###########################

# UT.VERIFY_LOGIN.1 - No verification email address provided

body = {
    "data": {
        "loginCode": 777777,
    },
}
test("/verify_login", body, "No verification email address provided")

# UT.VERIFY_LOGIN.2 - No verification code provided

body = {
    "data": {
        "emailAddress": "some.email@gmail.com",
    },
}
test("/verify_login", body, "No verification code provided")

# UT.VERIFY_LOGIN.3 - Incorrect verification code provided

# correct code is 777777
body = {
    "data": {
        "emailAddress": "some.email@gmail.com",
        "loginCode": 111111,
    },
}
test("/verify_login", body, "Incorrect verification code provided")

# UT.VERIFY_LOGIN.4 - Valid verification

body = {
    "data": {
        "emailAddress": "some.email@gmail.com",
        "loginCode": 777777,
    },
}
test("/verify_login", body, "Valid verification")

#####################
# Method: `/export` #
#####################

# UT.EXPORT.1 - User Not Authenticated

body = {
    "data": song,
}
test("/export", body, "User Not Authenticated")

# UT.EXPORT.2 - Lyrics not provided

del song["slides"]
body = {
    "data": song,
    "authToken": "top_secret_auth_token"
}
test("/export", body, "Lyrics not provided")

# UT.EXPORT.3 - Settings not provided

del song["settings"]
body = {
    "data": song,
    "authToken": "top_secret_auth_token"
}
test("/export", body, "Settings not provided")


# UT.EXPORT.4 - No text color provided

del song["settings"]["textColor"]
body = {
    "data": song,
    "authToken": "top_secret_auth_token"
}
test("/export", body, "No text color provided")

# UT.EXPORT.5 - No background color provided

del song["settings"]["backgroundColor"]
body = {
    "data": song,
    "authToken": "top_secret_auth_token"
}
test("/export", body, "No background color provided")

# UT.EXPORT.6 - No font size provided

del song["settings"]["fontSize"]
body = {
    "data": song,
    "authToken": "top_secret_auth_token"
}
test("/export", body, "No font size provided")

# UT.EXPORT.7 - No font family provided

del song["settings"]["fontFamily"]
body = {
    "data": song,
    "authToken": "top_secret_auth_token"
}
test("/export", body, "No font family provided")

# UT.EXPORT.8 - No title slide boolean provided

del song["settings"]["includeTitleSlide"]
body = {
    "data": song,
    "authToken": "top_secret_auth_token"
}
test("/export", body, "No title slide boolean provided")

# UT.EXPORT.9 - Invalid text color provided

song["settings"]["textColor"] = "#a09v23"
body = {
    "data": song,
    "authToken": "top_secret_auth_token"
}
test("/export", body, "Invalid text color provided")

# UT.EXPORT.10 - Invalid background color provided

song["settings"]["backgroundColor"] = "#a09v23"
body = {
    "data": song,
    "authToken": "top_secret_auth_token"
}
test("/export", body, "Invalid background color provided")

# UT.EXPORT.11 - Invalid font size provided

song["settings"]["fontSize"] = -3
body = {
    "data": song,
    "authToken": "top_secret_auth_token"
}
test("/export", body, "Invalid font size provided")

# UT.EXPORT.12 - Title slide requested and title not provided

del song["title"]
song["settings"]["includeTitleSlide"] = True
body = {
    "data": song,
    "authToken": "top_secret_auth_token"
}
test("/export", body, "Title slide requested and title not provided")

# UT.EXPORT.13 - Title slide requested

song["settings"]["includeTitleSlide"] = True
body = {
    "data": song,
    "authToken": "top_secret_auth_token"
}
test("/export", body, "Title slide requested")

# UT.EXPORT.14 - Title slide not requested

song["settings"]["includeTitleSlide"] = False
body = {
    "data": song,
    "authToken": "top_secret_auth_token"
}
test("/export", body, "Title slide not requested")

# save

df = pd.DataFrame(test_results)
df.to_excel("unit_tests.xlsx")
