from pymongo import MongoClient
from datetime import datetime as dt, timedelta
client = MongoClient("mongodb://localhost:27017/")
db = client["test-database0001"]
song_list = db["song_list"]
user_logins = db["user_logins"]
# print(song_list)
logins = [i for i in user_logins.find()]
for l in logins:
    print(l)

window = dt.now() - timedelta(minutes=1)
print(window)
print(f"Before Logins: {len(logins)}")
user_logins.delete_many({"time": {"$lt": window.isoformat()}})
logins = [i for i in user_logins.find()]
print(f"After Logins: {len(logins)}")
