from flask import Flask, request, jsonify
from datetime import datetime as dt, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from uuid import uuid4
from smtplib import SMTP
from email.message import EmailMessage
from pymongo import MongoClient
from flask_cors import CORS
from random import randint
import json

########################################
# REMEMBER TO START THE MONGOD SERVICE #
########################################

app = Flask(__name__)
# to fix http and CORS
app.config['NODE_TLS_REJECT_UNAUTHORIZED'] = 0
CORS(app)

# connect to database
client = MongoClient("mongodb://localhost:27017/")
db = client["test-database0001"]

# list of all songs by user
song_list = db["song_list"]
# auth tokens that correspond to user
user_logins = db["user_logins"]
# verification codes for email
email_codes = db["email_codes"]

def get_time() -> str:
    timestamp = dt.now().timestamp()
    iso_time = dt.fromtimestamp(timestamp).isoformat()
    return iso_time

def str_to_date(iso_time_stamp) -> dt:
    return dt.fromisoformat(iso_time_stamp)

def is_valid_login_code(data):
    email_address = data["email_address"]
    login_code = data['login_code']
    codes = [c for c in email_codes.find({"email_address": email_address})]
    for code in codes:
        if code["login_code"] == login_code:
            return True
    return False

def is_athentic_user(data:dict):
    try:
        email_address = data["email_address"]
        auth_token = data["auth_token"]
        tokens = [c for c in user_logins.find({"email_address": email_address})]
        for tokens in tokens:
            if tokens["auth_token"] == auth_token:
                return True
    except:
        return False

def get_user_from_auth_token(auth_token) -> str:
    tokens = [c for c in email_codes.find({"email_address": email_address})]
    for tokens in tokens:
        if tokens["auth_token"] == auth_token:
            return True

@app.route('/save', methods=['POST'])
def save():
    # get json data sent in body of request
    data = request.get_json()
    # so mongodb doesn't cry
    data = json.loads(json.dumps(data))

    # invalid user
    if not is_athentic_user(data):
        return jsonify({})

    print(f"Saved '{data['title']}' for '{data['userId']}'")
    # insert/update song
    result = song_list.update_one(
        # find same song
        {
            "songId": data["songId"],
            "userId": data["userId"]
        },
        {"$set": data}, # rewrite existing song
        upsert=True # insert if not exists
    )
    # return id of new song
    new_id = data["songId"]
    if result.upserted_id is not None:
        new_id = result.upserted_id
    return jsonify({"_id": new_id})


@app.route('/load', methods=['POST'])
def load():
    # get json data sent in body of request
    data = request.get_json()

    # invalid user
    if not is_athentic_user(data):
        return jsonify([])

    # find all songs by user
    result = song_list.find(
        {
            "userId": data["email_address"]
        },
    )
    # put elements at cursor into list
    result = [r for r in result]
    # return list of songs
    return jsonify(result)

HOST_EMAIL = ""

def send_email(address: str, code: int):
    email = EmailMessage()
    email.set_content(f"Here is your code: {code}")
    email['Subject'] = "Lyric of Lyrics - Verification Code"
    email['From'] = HOST_EMAIL
    email['To'] = address
    with SMTP("localhost") as s:
        s.send_message(email)

@app.route('/send_verification_code', methods=['POST'])
def send_verification_code():
    # get json data sent in body of request
    data = request.get_json()
    email_address = data['email_address']
    login_code = randint(0,999999)

    # save code
    email_codes.insert_one({
        "login_code": login_code,
        "email_address": email_address,
        "time": get_time()
    })

    # email user
    print(f"Sent code {login_code} to '{email_address}'")
    # send_email(email_address, login_code)
    return jsonify({})


@app.route('/verify_login', methods=['POST'])
def verify_login():
    # get json data sent in body of request
    data = request.get_json()
    
    entry = {}
    if is_valid_login_code(data):
        auth_token = str(uuid4())
        entry = {
            "auth_token": auth_token,
            "email_address": data['email_address'],
            "time": get_time()
        }
        user_logins.insert_one(json.loads(json.dumps(entry)))
    return jsonify(entry)

LOGIN_CODE_EXPIRATION_MINUTES = 5

def remove_old_login_codes():
    window = dt.now() - timedelta(minutes=LOGIN_CODE_EXPIRATION_MINUTES)
    email_codes.delete_many({"time": {"$lt": window.isoformat()}})

AUTH_TOKEN_EXPIRATION_WEEKS = 8

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
