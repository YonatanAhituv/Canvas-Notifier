# -------
# Imports
# -------
# Standard Libraries
import os
import token
# Connected Scripts
import canvasHandler
import db
# Pip Libraries
from flask import Flask, make_response, redirect, url_for, render_template, request, send_from_directory
import validators

#  ----------------------------

# Handle Web Sever

global courses, assignments

app = Flask(__name__)
def initGlobals():
    global assignments, courses
    if 'assignments' not in globals() or 'courses' not in globals():
        assignments = {}
        courses = {}

def loadToCache(token, url, apiKey):  # Loads user info into a dictonary variable for caching
    global assignments, courses
    initGlobals()  # Initalizes globals as blank dictonaries if they don't exist
    loadedCourses, loadedAssignments = canvasHandler.retrieveAssignments(
        url, apiKey)  # Retrieve assignments from canvasHandler
    courses[token] = loadedCourses  # Assign courses to user token in cache
    assignments[token] = loadedAssignments  # Assign assignments to user token in cache 

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
                    loadToCache(token, apiInfo["url"], apiInfo["apiKey"])
                    print('what sexy assignments you got there')
                    userToken = db.storeUser(apiInfo["url"], apiInfo["apiKey"])
                    response = make_response(redirect(url_for('indexPage')))
                    response.set_cookie('userID', userToken)
                    return response
                except Exception as e:
                    print(e)
        
    return redirect(url_for('indexPage'))  # Index will redirect back to setup page if no config

@app.route("/setup")
def setupSite():
    if db.verifyUser(request.cookies.get('userID')):
        return redirect(url_for('indexPage'))
    else:
        return render_template('setup.html')

@app.route("/", methods=["POST", "GET"])
def indexPage():
    token = request.cookies.get('userID')
    # Check if cookie is visible first
    if not db.verifyUser(token):
        return redirect(url_for('setupSite'))

    # Now handle front page
    global assignments, courses
    initGlobals()
    if request.method == "POST" or token not in assignments.keys() or token not in courses.keys(): # Page is reloaded or user token is not in cache
        userConfig = db.readUser(token)
        loadToCache(token, userConfig[1], userConfig[2])
        
    return render_template('index.html', assignments=assignments[token])


app.run(debug=True)
