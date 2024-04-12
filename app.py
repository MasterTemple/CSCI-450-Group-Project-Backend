####################
# IMPORT LIBRARIES #
####################

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime as dt, timedelta
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask_cors import CORS
from flask import Flask, request, jsonify, Request, send_file
from pymongo import MongoClient
from random import randint
from uuid import uuid4
from slideshow import Slideshow

import json
import os
import smtplib
import re


def msg(data: str) -> dict[str, str]:
    return {"msg": data}

def reply(data):
    res = jsonify(data)
    res.headers.set("Content-Type", "application/json")
    res.headers.add('Access-Control-Allow-Origin', '*')
    return res

##############################
# LOAD ENVIRONMENT VARIABLES #
##############################

load_dotenv()

LOL_EMAIL = os.environ.get("EMAIL")
LOL_PASSWORD = os.environ.get("APP_PASSWORD")
DB_NAME = os.environ.get("DB_NAME")
DB_URI = os.environ.get("DB_URI")

if any(v is None for v in [LOL_EMAIL, LOL_PASSWORD, DB_NAME, DB_URI]):
    print("Follow the instructions in `README.md` to set up your `.env` file.")
    exit(1)

# to remove LSP errors
LOL_EMAIL = LOL_EMAIL or ""
LOL_PASSWORD = LOL_PASSWORD or ""
DB_NAME = DB_NAME or ""
DB_URI = DB_URI or ""

LOGIN_CODE_EXPIRATION_MINUTES = int(os.environ.get("LOGIN_CODE_EXPIRATION_MINUTES") or 5)
AUTH_TOKEN_EXPIRATION_WEEKS = int(os.environ.get("AUTH_TOKEN_EXPIRATION_WEEKS") or 8)

########################################
# REMEMBER TO START THE MONGOD SERVICE #
########################################

app = Flask(__name__)
# to fix http and CORS
app.config['NODE_TLS_REJECT_UNAUTHORIZED'] = 0
CORS(app)

# connect to database
client = MongoClient(DB_URI)
db = client[DB_NAME]

# list of all songs by user
song_list = db["song_list"]
# auth tokens that correspond to user
user_logins = db["user_logins"]
# verification codes for email
email_codes = db["email_codes"]

#############
# FUNCTIONS #
#############

def get_time() -> str:
    timestamp = dt.now().timestamp()
    iso_time = dt.fromtimestamp(timestamp).isoformat()
    return iso_time

def str_to_date(iso_time_stamp) -> dt:
    return dt.fromisoformat(iso_time_stamp)

def is_valid_login_code(data):
    email_address = data["emailAddress"]
    login_code = data['loginCode']
    codes = [c for c in email_codes.find({"emailAddress": email_address})]
    for code in codes:
        if int(code["loginCode"]) == int(login_code):
            return True
    return False

def is_athentic_user(data:dict) -> bool:
    print("is_athentic_user()")
    print(data)
    email_address = data["emailAddress"]
    auth_token = data["authToken"]
    tokens = [c for c in user_logins.find({"emailAddress": email_address})]
    print(tokens)
    print([c for c in user_logins.find()])
    for tokens in tokens:
        if tokens["authToken"] == auth_token:
            return True
    return False

def get_user_from_auth_token(auth_token) -> str | None:
    entry = user_logins.find_one({"authToken": auth_token})
    if entry is None:
        return None
    return entry["emailAddress"]

def send_verification_email(recipient: str, code: int) -> str:
    # code_str = f"{code:0>6}"
    SUBJECT = "Lyric of Lyrics - Verification Code"
    BODY = f"Enter the following 6-digit code to verify your identity and gain access to your Lyric of Lyrics account: <b>{code}</b>"
    s=smtplib.SMTP("smtp.gmail.com", 587)
    s.starttls()
    s.login(LOL_EMAIL, LOL_PASSWORD)
    message = MIMEMultipart()
    message['From'] = LOL_EMAIL
    message['To'] = recipient
    message['Subject'] = SUBJECT
    html_message = BODY
    message.attach(MIMEText(html_message, 'html'))
    try:
        s.sendmail(LOL_EMAIL, [recipient], message.as_string())
        s.quit()
        return "Code sent to email address if valid"
    except:
        return "Email address is invalid"


def parse_json(request: Request) -> tuple[str|None, dict]:
    """
    because MongoDB cries
    """
    body = {}
    # print(f"{request.is_json=}")
    # print(f"{request.json=}")
    # print(f"{request.data=}")
    if request.is_json:
        body = json.loads(json.dumps(request.get_json()))
    else:
        body = json.loads(request.get_data())
    token = body["authToken"] if "authToken" in body else None
    data = body["data"] if "data" in body else {}
    return token, data

#################
# SERVER ROUTES #
#################

@app.route('/save', methods=['POST'])
def save():
    # get json data sent in body of request
    auth_token, data = parse_json(request)

    if auth_token is None:
        return reply(msg("User not authenticated"))

    # invalid user
    emailAddress = get_user_from_auth_token(auth_token)

    if emailAddress is None:
        return reply(msg("Invalid user authentication"))

    if "songId" not in data:
        return reply(msg("No song id provided"))

    if "slides" not in data or "lines" not in data:
        return reply(msg("No song lyrics provided"))

    # insert/update song
    song_list.update_one(
        # find same song
        {
            "songId": data["songId"],
            "emailAddress": data["emailAddress"]
        },
        {"$set": data}, # rewrite existing song
        upsert=True # insert if not exists
    )
    # return reply(success=True,_id=result.upserted_id)
    return reply(msg("Valid save"))


@app.route('/load', methods=['POST'])
def load():
    # get json data sent in body of request
    auth_token, _ = parse_json(request)

    if auth_token is None:
        return reply(msg("User not authenticated"))

    # invalid user
    emailAddress = get_user_from_auth_token(auth_token)

    if emailAddress is None:
        return reply(msg("Invalid user authentication"))

    # find all songs by user
    result = song_list.find(
        {
            "emailAddress": emailAddress
        },
    )
    # put elements at cursor into list
    result = [r for r in result]
    # ObjectId() object doesn't reply and I don't need it
    for r in result:
        del r["_id"]
    # return list of songs
    return reply(result)

@app.route('/delete', methods=['POST'])
def delete_song():
    # get json data sent in body of request
    auth_token, data = parse_json(request)

    if auth_token is None:
        return reply(msg("User not authenticated"))

    # invalid user
    emailAddress = get_user_from_auth_token(auth_token)

    if emailAddress is None:
        return reply(msg("Invalid user authentication"))

    # print()
    # print(len([s for s in song_list.find({})]))
    # print([s["songId"] for s in song_list.find({})])
    # print(data['songId'])
    # print(emailAddress)
    result = song_list.delete_one(
        # find same song
        {
            "songId": str(data["songId"]),
            "emailAddress": emailAddress
        }
    )
    # print("DELETE")
    print(len([s for s in song_list.find({})]))
    print(result)
    if result.raw_result.get("n") == 0:
        return reply(msg("Song does not exist"))
    else:
        return reply(msg("Valid song delete successful"))

@app.route('/send_verification_code', methods=['POST'])
def send_verification_code():
    # get json data sent in body of request
    # data = request.get_json()
    _, data = parse_json(request)
    if "emailAddress" not in data:
        return reply(msg("No verification email address provided"))
    email_address = data['emailAddress']
    login_code = randint(100000,999999)

    # save code
    email_codes.insert_one({
        "loginCode": login_code,
        "emailAddress": email_address,
        "time": get_time()
    })

    # email user
    print(f"Sending code {login_code} to '{email_address}'")
    email_response =  send_verification_email(email_address, login_code)
    # email_response = "Code sent to email address if valid"
    return reply(msg(email_response))

@app.route('/verify_login', methods=['POST'])
def verify_login():
    # get json data sent in body of request
    # data = request.get_json()
    _, data = parse_json(request)

    if "emailAddress" not in data:
        return reply(msg("No verification email address provided"))

    if "loginCode" not in data:
        return reply(msg("No verification code provided"))
    
    entry = {}
    print(f"{is_valid_login_code(data)=}")
    if is_valid_login_code(data):
        auth_token = str(uuid4())
        entry = {
            "authToken": auth_token,
            "emailAddress": data['emailAddress'],
            "time": get_time()
        }
        user_logins.insert_one(json.loads(json.dumps(entry)))
        return reply(entry)
    else:
        return reply(msg("Incorrect verification code provided"))

TEMP_PPTX_FILE = "temp.pptx"
@app.route('/export', methods=['POST'])
def export():
    auth_token, data = parse_json(request)

    if auth_token is None:
        return reply(msg("User not authenticated"))

    if "settings" not in data:
        return reply(msg("Settings not provided"))

    # validate all settings parameters
    settings = data["settings"]
    # defaults
    if "textColor" not in settings:
        settings["textColor"] = "#ffffff"
    if "backgroundColor" not in settings:
        settings["backgroundColor"] = "#000000"
    if "fontFamily" not in settings:
        settings["fontFamily"] = "Arial"
    if "fontSize" not in settings:
        settings["fontSize"] = 36
    else:
        settings["fontSize"] = float(settings["fontSize"])
    if "includeTitleSlide" not in settings:
        settings["includeTitleSlide"] = False


    if not re.match("#[0-9a-f]{6}", settings["textColor"]):
        return reply(msg("Invalid text color settings"))
    if not re.match("#[0-9a-f]{6}", settings["backgroundColor"]):
        return reply(msg("Invalid background color settings"))
    if settings["fontSize"] < 0:
        return reply(msg("Invalid font size settings"))

    if "title" not in data and settings["includeTitleSlide"]:
        return reply(msg("Title slide requested, but no title given"))

    if "slides" not in data:
        return reply(msg("Lyrics not provided"))

    # print(json.dumps(data))
    # if "author" not in data:
    #     data["author"] = ""

    # print(data.keys())
    slideshow = Slideshow(data["slides"], data["settings"], data["title"], data["author"])
    if len(data["title"]) > 0:
        title = data["title"]
    else:
        title = data["slides"][0][0]
    if len(data["author"]) > 0:
        title = f"{title} - {data['author']}"
    slideshow.save(TEMP_PPTX_FILE)
    res = send_file(TEMP_PPTX_FILE, as_attachment=True, download_name=f"{title}.pptx")
    # res.headers.set("Content-Type", "application/vnd.openxmlformats-officedocument.presentationml.presentation")
    res.headers.add('Access-Control-Allow-Origin', '*')
    return res

####################################
# CLEAN OLD LOGIN CODES AND TOKENS #
####################################

def remove_old_login_codes():
    window = dt.now() - timedelta(minutes=LOGIN_CODE_EXPIRATION_MINUTES)
    email_codes.delete_many({"time": {"$lt": window.isoformat()}})

def remove_old_auth_tokens():
    window = dt.now() - timedelta(weeks=AUTH_TOKEN_EXPIRATION_WEEKS)
    user_logins.delete_many({"time": {"$lt": window.isoformat()}})

if __name__ == '__main__':
    # cron jobs
    scheduler = BackgroundScheduler()
    scheduler.add_job(remove_old_login_codes, "interval", minutes=LOGIN_CODE_EXPIRATION_MINUTES)
    scheduler.add_job(remove_old_auth_tokens, "interval", weeks=AUTH_TOKEN_EXPIRATION_WEEKS)
    scheduler.start()
    
    # host server
    app.run(debug=True) # ssl_context='adhoc'
