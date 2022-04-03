# -------
# Imports
# -------
# Standard Libraries
import os
from secrets import token_urlsafe
import token
# Connected Scripts
import canvasHandler
import config
# Pip Libraries
from flask import Flask, make_response, redirect, url_for, render_template, request, send_from_directory
import validators

#  ----------------------------

# Handle Web Sever

global courses, assignments

app = Flask(__name__)
def getFiles(directory):
    files = {}
    for file in os.listdir(directory):
        with open(directory + "/" + file) as fileData:
            files[file] = str(fileData.read())
    return files

def initGlobals():
    global assignments, courses
    if 'assignments' not in globals() or 'courses' not in globals():
        assignments = {}
        courses = {}

def loadToCache(token, url, apiKey):
    global assignments, courses
    initGlobals()
    loadedCourses, loadedAssignments = canvasHandler.retrieveAssignments(
        url, apiKey)
    courses[token] = loadedCourses
    assignments[token] = loadedAssignments

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/submitAPI', methods=['POST', 'GET'])
def handleAPI():
    if request.method == 'POST':
        global courses, assignments
        apiInfo = dict(request.form)
        # Validation step goes here buddy
        if list(apiInfo.keys()) == ["url", "apiKey"]: # Check url
            print("i like the keys you got there")
            if validators.url(apiInfo["url"]):
                print("oh and I love your url")
                try:
                    userToken = token_urlsafe(64)
                    while userToken in config.read().keys():  # Make sure token doesnt already exist
                        userToken = token_urlsafe(64)  # The chances of this running are like actually zero
                    loadToCache(token, apiInfo["url"], apiInfo["apiKey"])
                    print('what sexy assignments you got there')
                    response = make_response(redirect(url_for('indexPage')))
                    response.set_cookie('userID', userToken)
                    config.write(apiInfo, userToken=userToken)
                    return response
                except Exception as e:
                    print(e)
        
    return redirect(url_for('indexPage'))  # Index will redirect back to setup page if no config

@app.route("/setup")
def setupSite():
    if config.verifyUser(request.cookies.get('userID')):
        return redirect(url_for('indexPage'))

    return render_template('setup.html')

@app.route("/", methods=["POST", "GET"])
def indexPage():
    token = request.cookies.get('userID')
    # Check if cookie is visible first
    if not config.verifyUser(token):
        return redirect(url_for('setupSite'))

    # Now handle front page
    global assignments, courses
    initGlobals()
    if request.method == "POST" or token not in assignments.keys() or token not in courses.keys(): # Data is reloaded or user token is not in thingies
        userConfig = config.read(userToken=token)
        loadToCache(token, userConfig["url"], userConfig["apiKey"])
        
    return render_template('index.html', assignments=assignments[token])


if config.validConfig(initConfig=True):  # Check if config is valid before doing anything
    app.run(debug=True)
else:
    print("ERROR: There is an issue with config/api.json. Please check the file for problems!")

