# -------
# Imports
# -------
# Standard Libraries
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
# Connected Scripts
import canvasHandler
import config
# Pip Libraries
from flask import Flask, redirect, url_for, render_template, request, send_from_directory
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
                    courses, assignments = canvasHandler.retrieveAssignments(
                        apiInfo["url"], apiInfo["apiKey"])
                    print('what sexy assignments you got there', apiInfo["apiKey"])
                    config.write(apiInfo)
                except Exception as e:
                    print(e)
        
    return redirect(url_for('indexPage'))  # Index will redirect back to setup page if no config

@app.route("/setup")
def setupSite():
    if config.validConfig():
        return redirect(url_for('indexPage'))
    return render_template('setup.html')

@app.route("/", methods=["POST", "GET"])
def indexPage():
    if not config.validConfig():  # Check if config is valid before doing anything
        return redirect(url_for('setupSite'))
    
    # Now handle front page
    global assignments, courses
    if 'assignments' not in globals() or 'courses' not in globals() or request.method == "POST":
        apiInfo = config.read()
        courses, assignments = canvasHandler.retrieveAssignments(apiInfo["url"], apiInfo["apiKey"])
    print(assignments)
    return render_template('index.html', assignments=assignments)


app.run(debug=True)
