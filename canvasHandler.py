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
    canvas = Canvas(canvasURL, apiKey)
    user = canvas.get_current_user()
    courses = user.get_courses(include=['term', 'total_scores'])
    visibleCourses = []

    for course in courses:
        if course.term['end_at'] is None:
            continue
        elif futureDate(course.term['end_at']):
            visibleCourses.append(course)

    return visibleCourses

def sortAssignmentsByDate(assignmentList):
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
    visibleCourses = getCourses(canvasURL, apiKey)
    courseAssignments = {}
    for course in visibleCourses:
        # Get corresponding cal for assignments
        cal = requests.get(course.calendar['ics']).text
        cal = Calendar(cal)
        courseAssignments[course.name] = []
        for assignment in cal.events:
            if assignment.end > arrow.utcnow():
                courseAssignments[course.name].append(assignment)
    if inOrder:
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
