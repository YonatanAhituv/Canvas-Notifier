import os, json

def validConfig():  # Very messy sanity check
    if 'config' not in os.listdir():
        return False
    elif 'api.json' not in os.listdir('config'):
        return False
    # api.json exists
    with open('config/api.json') as file:
        config = file.read()
    try: # Check for valid JSON
        config = json.loads(config)
    except ValueError:
        return False
    return True  # File exists, is valid json, has the right keys, and the keys have stuff in them

def read(userToken=None):
    with open('config/api.json') as file:
        if userToken is None:
            return json.loads(file.read())
        else:
            return json.loads(file.read())[userToken]


def verifyUser(userToken):
    config = read()
    if userToken not in config.keys():
        return False
    for key in ['url', 'apiKey']:
        try:
            if key not in config[userToken].keys():
                return False
        except AttributeError:
            return False
    return True # Usertoken is in database and has the right keys

def write(data, userToken=None):
    if validConfig():
        writeMode = 'r+'
    else:
        writeMode = 'w+'
    with open('config/api.json', writeMode) as file:
        if userToken is None or writeMode == 'w+':
            fileData = data
        else:
            fileData = file.read() # Python has divinely intervened to ensure file.read() isnt with json.loads
            fileData = json.loads(fileData) # This code literally does not work if the two aren't seperate
            fileData[userToken] = data
        file.seek(0)
        output = json.dumps(fileData, indent=4)
        file.write(output)
        file.truncate() # Remove previous part of file because r+ is stupid

