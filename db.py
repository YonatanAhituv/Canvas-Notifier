configLocation = 'config/db.json'  # Default location
import os
import json
from secrets import token_urlsafe
import psycopg

# Break given path into file name and parent directory path
configDirs = configLocation.split('/')
configFile = configDirs[-1]
configDir = ""
for i in range(0,len(configDirs)-1): # Remove last entry in path
    configDir += configDirs[i] + '/'
configDir = configDir[:-1] # Remove last /


def validConfig(initConfig=False):  # Very messy sanity check
    fileExists = True
    if configDir not in os.listdir():
        fileExists = False
    elif configFile not in os.listdir(configDir):
        fileExists = False
    if not fileExists and not initConfig:
        return False
    elif fileExists and initConfig:
        with open(configLocation, 'w') as file:
            file.write('{}')
    # file exists
    with open(configLocation) as file:
        config = file.read()
    try: # Check for valid JSON
        config = json.loads(config)
    except ValueError:
        return False
    return True  # File exists, is valid json

def readConfig():
    with open(configLocation) as file:
        return json.loads(file.read())

def initDB():
    config = readConfig()
    with psycopg.connect("dbname=%s user=%s" % (config["databaseName"], config["user"])) as conn:
                         # Open a cursor to perform database operations
        with conn.cursor() as cur:
            cur.execute("""CREATE TABLE IF NOT EXISTS accounts (
    cookie VARCHAR(86) PRIMARY KEY,
    url text NOT NULL,
    apiKey text NOT NULL
);""")
            conn.commit()

def verifyUser(userToken):
    config = readConfig()
    with psycopg.connect("dbname=%s user=%s" % (config["databaseName"], config["user"])) as conn:
        # Open a cursor to perform database operations
        with conn.cursor() as cur:
            cur.execute(
                """SELECT cookie FROM accounts WHERE cookie = %s;""", [userToken])
            userToken = cur.fetchone()
            if userToken is None:
                return False
            else:
                return True

def getCookie(url, apiKey):
    config = readConfig()
    with psycopg.connect("dbname=%s user=%s" % (config["databaseName"], config["user"])) as conn:
        # Open a cursor to perform database operations
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM accounts WHERE url = %s AND apiKey = %s;", (url, apiKey))
            row = cur.fetchone()
            if row is None:
                return None
            else:
                return row[0]

def storeUser(url, apiKey):
    config = readConfig()
    userToken = getCookie(url, apiKey)
    if userToken is not None:
        return userToken # Return existing cookie
    userToken = token_urlsafe(64)
    while readUser(userToken) is not None:  # Ensure doesn't exist
        userToken = token_urlsafe(64)
    with psycopg.connect("dbname=%s user=%s" % (config["databaseName"], config["user"])) as conn:
        # Open a cursor to perform database operations
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO accounts (cookie, url, apiKey) VALUES (%s, %s, %s);",
                (userToken, url, apiKey))
            conn.commit()
    return userToken

def readUser(userToken):
    config = readConfig()
    with psycopg.connect("dbname=%s user=%s" % (config["databaseName"], config["user"])) as conn:  # Open a cursor to perform database operations
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM accounts WHERE cookie = %s;", [userToken])
            return cur.fetchone()

if validConfig():
    initDB()
else:
    print("Please check your database configuration!")

