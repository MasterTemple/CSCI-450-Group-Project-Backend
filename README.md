# CSCI-450-Group-Project-Backend

Back-end server for https://github.com/MasterTemple/CSCI-450-Group-Project

# Setup

## Install Python

Download found [here](https://www.python.org/downloads/).

## Install MongoDB on your system

Instructions found [here](https://www.mongodb.com/docs/manual/administration/install-community/).

## Install Python Packages

```sh
pip install -r requirements.txt
```

## Create `.env` file with the following contents

```sh
EMAIL="lyric.of.lyrics.app@gmail.com"
APP_PASSWORD="CONTACT_ME_FOR_THIS"
LOGIN_CODE_EXPIRATION_MINUTES=5
AUTH_TOKEN_EXPIRATION_WEEKS=8
DB_NAME="lyric-of-lyric-db-001"
DB_URI="mongodb://localhost:27017/"
```

You can rename the `.env.template` file to `.env` and then fill in the `APP_PASSWORD` field.

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
