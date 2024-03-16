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
#     "login_code": 133055
# }


url += "load"
body = {
    "authToken": "1de016b1-51ce-42e5-8ce2-934dec2105e4",
    "data": {
        "emailAddress": "blake.scampone@biola.edu",
    }
}

headers = {"Content-Type": "application/json"}
res = requests.post(url, json=body, headers=headers)
# print(res)
print(len(res.json()))
