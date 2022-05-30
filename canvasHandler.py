# Standard Libraries
from datetime import datetime
import time

# Libraries from Pip
from canvasapi import Canvas
from ics import Calendar, Event
import requests
import arrow



def futureDate(date):
    utc = datetime.strptime(date, "%Y-%m-%dT%H:%M:%fZ")  # Read date
    termEnd = (utc - datetime(1970, 1, 1)).total_seconds()  # Seconds since 1970 (;
    currentTime = int(time.time())
    if termEnd > currentTime:  # Course hasn't ended
        return True
    else:
        return False


def getCourses(canvasURL, apiKey):
    canvas = Canvas(canvasURL, apiKey)  # Initialize canvas api
    user = canvas.get_current_user() # Get connected user
    courses = user.get_courses(include=['term']) # Get courses as well as additional info
    visibleCourses = []

    for course in courses: # Keep only courses which end in the future (are currently being taken) 
        try: # If course is irregular somehow just keep going
            if course.term['end_at'] is None:
                continue
            elif futureDate(course.term['end_at']):
                visibleCourses.append(course)
        except:
            continue

    return visibleCourses

def sortAssignmentsByDate(assignmentList):  # Really inefficent spaghetti code to organize a list by date
    outputList = []
    if len(assignmentList) == 1:
        return assignmentList
    activeList = assignmentList
    for i in range(len(assignmentList)):
        low = activeList[0]
        lowIndex = 0
        for index, assignment in enumerate(activeList):
            if assignment.end < low.end:
                low = assignment
                lowIndex = index
        activeList.pop(lowIndex)
        outputList.append(low)
    return outputList

def retrieveAssignments(canvasURL, apiKey, inOrder=True, info={"name", "end"}, humanize=True, courseInTitle=False):
    visibleCourses = getCourses(canvasURL, apiKey) # Retrieve courses
    courseAssignments = {}
    for course in visibleCourses: # Loop over courses
        # Get corresponding cal for assignments
        cal = requests.get(course.calendar['ics']).text
        cal = Calendar(cal) # Process calander with ics from pypi
        courseAssignments[course.name] = [] # Start organizing assignments into dict
        for assignment in cal.events:
            if assignment.end > arrow.utcnow(): # Keep only assignments which aren't overdue
                courseAssignments[course.name].append(assignment) # Add to course's corresponding list in dict
    if inOrder:  # Order assignments if asked for
        for course in courseAssignments:
            courseAssignments[course] = sortAssignmentsByDate(courseAssignments[course])
    
    outputDict = {}
    for course in courseAssignments:
        outputDict[course] = []
        for assignment in courseAssignments[course]:
            outputAssignment = {}
            for item in info:
                value = getattr(assignment, item)
                if item == "end" or item == "start":
                    value = value.humanize()
                if not courseInTitle and item == "name":
                    # Thing will look like: assignment [P1-Teacher]
                    for i in range(len(value)-1, -1, -1): # Loop backwards (;
                        if value[i] == "[":
                            endIndex = i
                            break
                    value = value[:endIndex]

                outputAssignment[item] = value
            outputDict[course].append(outputAssignment)

    return visibleCourses, outputDict
