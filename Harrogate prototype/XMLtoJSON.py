# ----------------------------- #
# File to convert XML into JSON #
# ----------------------------- #

## Imports ##

from bs4 import BeautifulSoup
import json
import os

## File Handling ##

# Array of extracted XML data
rawData = []

# Extracting all xml files from working directory:
for file in os.listdir(r"./"):
    if file.endswith("xml"):

        # Append file data into data array:
        with open(file, "r") as f:
            rawData.append(f.read())

## Formatting Data ##

jsonStopData = []
jsonRouteData = []

for file in rawData:

    BSData = BeautifulSoup(file, "xml")

    busStopData = BSData.find_all("AnnotatedStopPointRef")
    tempStopData = []

    for i in range(len(busStopData)):
        tempStopData.append(
            {
                "StopPointRef": busStopData[i].find("StopPointRef").get_text(),
                "CommonName": busStopData[i].find("CommonName").get_text(),
                "LocalityName": busStopData[i].find("LocalityName").get_text(),
            }
        )
    jsonStopData.append(tempStopData)

    routeData = BSData.find_all("RouteLink")
    tempRouteData = []

    for i in range(len(routeData)):

        midrouteDirections = {}
        for j in routeData[i].find_all("Location"):
            # Fetch all coordinates from RouteSection, and link them with their respective 'id'
            midrouteDirections[j.get("id")] = (
                j.find("Latitude").get_text(),
                j.find("Longitude").get_text(),
            )

        tempRouteData.append(
            {
                "Start": routeData[i]
                .find("From")
                .get_text()[1:-1],  # removes '\n' from start and end
                "End": routeData[i].find("To").get_text()[1:-1],
                "Distance": routeData[i].find("Distance").get_text(),
                "Route Track": midrouteDirections,
            }
        )
    jsonRouteData.append(tempRouteData)

## Exporting Formatted Data ##

with open("AllBusStopData.json", "w") as f:
    json.dump(jsonStopData, f)

with open("AllRoutesData.json", "w") as g:
    json.dump(jsonRouteData, g)

## Main ##

# Convenience functions:

def printStops(StopsJSON, n = None, s = 0):
    try:
        if n == None:
            n = len(StopsJSON)
        for i in StopsJSON[s:n]:
            print(i)
    except:
        print("Error in JSON or filter_number(s)")

def printOnlyRoutes(RoutesJSON, n = None, s = 0):
    try:
        if n == None:
            n = len(RoutesJSON)
        for j in RoutesJSON[s:n]:
            print( {k:v for k,v in j.items() if k not in  "Route Track"} )
    except:
        print("Error in JSON or filter_number(s)")

def printExtraRoutes(RoutesJSON, n = None, s = 0):
    try:
        if n == None:
            n = len(StopsJSON)
        for k in RoutesJSON[s:n]:
            print(k, end='\n\n')
    except:
        print("Error in JSON or filter_number(s)")

def printExcessRoutes(RoutesJSON, n = None, s = 0):
    try:
        if n == None:
            n = len(StopsJSON)
        for l in RoutesJSON[s:n]:
            for r in l["Route Track"]:
                print(f"'{r}' : {l['Route Track'][r]}")
            print()
    except:
        print("Error in JSON or filter_number(s)")
        
tutorial = 0
if tutorial == 1:
    print(
        "Data is stored in array 'jsonStopData' for bus stops and 'jsonRouteData' for bus routes.\n\
    > jsonData[i] gives the data for the 'i'th file, and is an array.\n\
    > jsonData[i][j] gives the 'j'th bus stop in file 'i', and is a dictionary/JSON object.\n\
    > Data contains 1. Stop Point Reference (ATCO Code), 2. Common Name of bus stop, 3. Locality Name"
    )
    print("Run commands on terminal to access data")
