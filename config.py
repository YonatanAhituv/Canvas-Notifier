import os, json
from urllib.parse import urlparse, ParseResult, parse_qs, urlencode
def setScheme(url, scheme):
    params = parse_qs(url.scheme)
    params = scheme
    res = ParseResult(scheme=url.scheme, netloc=url.hostname, path=url.path,
                    params=url.params, query=urlencode(params), fragment=url.fragment)
    print(res.geturl())

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
    for key in ['url', 'apiKey']:
        if key in config.keys():
            if config[key] != "":
                continue
        return False
    return True  # File exists, is valid json, has the right keys, and the keys have stuff in them
def write(data):
    with open('config/api.json', 'w') as file:
        file.write(json.dumps(data))

def read():
    with open('config/api.json') as file:
        return json.loads(file.read())
