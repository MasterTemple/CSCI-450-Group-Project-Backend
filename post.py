############################
# this is used for testing #
############################

import requests
url = "http://127.0.0.1:5000/"

# url += "send_verification_code"
# data = {
#     "email_address": "blake.scampone@biola.edu",
# }

# url += "verify_login"
# data = {
#     "email_address": "blake.scampone@biola.edu",
#     "login_code": 641173
# }


url += "load"
data = {
    "email_address": "blake.scampone@biola.edu",
    "auth_token": "fce1fd30-da01-4f09-8709-331f514d6ad3"
}

headers = {"Content-Type": "application/json"}
res = requests.post(url, json=data, headers=headers)
# print(res)
print(res.json())
