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
#     "login_code": 197186
# }


url += "load"
data = {
    "email_address": "blake.scampone@biola.edu",
    "auth_token": "8294fb3a-e85c-4b44-8186-e2a0f2b6b422"
}

headers = {"Content-Type": "application/json"}
res = requests.post(url, json=data, headers=headers)
# print(res)
print(res.json())
