# CSCI-450-Group-Project-Backend

Backend server for https://github.com/MasterTemple/CSCI-450-Group-Project

# Setup

## Install MongoDB on your system

Instructions found [here](https://www.mongodb.com/docs/manual/administration/install-community/).

## Install Python Packages

```sh
pip install flask apscheduler pymongo flask_cors python-dotenv
```

## Create `.env` file with the following contents

```
EMAIL="lyric.of.lyrics.app@gmail.com"
APP_PASSWORD="CONTACT_ME_FOR_THIS"
LOGIN_CODE_EXPIRATION_MINUTES=5
AUTH_TOKEN_EXPIRATION_WEEKS=8
```

# Usage

## Start Mongod

**Make sure that the MongoDB background process is running**

```sh
sudo systemctl start mongod
```

## Run Python Server

```sh
python app.py
```
