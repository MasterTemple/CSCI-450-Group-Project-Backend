from pymongo import MongoClient
from datetime import datetime as dt, timedelta
client = MongoClient("mongodb://localhost:27017/")
db = client["test-database0001"]
song_list = db["song_list"]
user_logins = db["user_logins"]
# print(song_list)
# logins = [i for i in user_logins.find()]
# for l in logins:
#     print(l)

# window = dt.now() - timedelta(minutes=1)
# print(window)
# print(f"Before Logins: {len(logins)}")
# user_logins.delete_many({"time": {"$lt": window.isoformat()}})
# logins = [i for i in user_logins.find()]
# print(f"After Logins: {len(logins)}")

# songs = [i for i in song_list.find()]
# print(songs)

# print([e for e in user_logins.find()])
# print([e for e in song_list.find()])

# user_logins.delete_many({})

# data = {
#     "emailAddress": "blake.scampone@biola.edu",
#     'authToken': '1de016b1-51ce-42e5-8ce2-934dec2105e4',
#     'time': '2024-03-15T09:01:14.209632'
# }
#
# result = user_logins.update_one(
#     # find same song
#     {
#         "email_address": data["emailAddress"]
#     },
#     {"$set": data}, # rewrite existing song
#     upsert=True # insert if not exists
# )
# print([e for e in user_logins.find()])
print([e for e in song_list.find()])
# song_list.delete_many({})
# print([e for e in song_list.find()])
