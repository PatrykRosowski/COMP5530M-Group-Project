# ----------------------------- #
# File to convert XML into JSON #
# ----------------------------- #


## Imports ##

from bs4 import BeautifulSoup
import json
import os


## File Handling ##

#Array of extracted XML data
rawData = []

#Extracting all xml files from working directory:
for file in os.listdir(r'./'):
    if file.endswith('xml'):

        #Append file data into data array:
        with open(file, 'r') as f:
            rawData.append(f.read())


## Formatting Data ##

jsonData = []

for file in rawData:
    
    BSData = BeautifulSoup(file, "xml")
    busStopData = BSData.find_all("AnnotatedStopPointRef")

    tempJsonData = []
    for i in range(len(busStopData)):
        tempJsonData.append( {
            "StopPointRef" : busStopData[i].find("StopPointRef").get_text(),
            "CommonName" : busStopData[i].find("CommonName").get_text(),
            "LocalityName" : busStopData[i].find("LocalityName").get_text()
            } )

    jsonData.append(tempJsonData)

with open("AllBusStopData.json", "w") as f:
    json.dump(jsonData, f)


## Main ##

tutorial = 1
if tutorial == 1:
    print("Data is stored in array 'jsonData'.\n\
    > jsonData[i] gives the data for the 'i'th file, and is an array.\n\
    > jsonData[i][j] gives the 'j'th bus stop in file 'i', and is a dictionary/JSON object.\n\
    > Data contains 1. Stop Point Reference (ATCO Code), 2. Common Name of bus stop, 3. Locality Name")
    print("Run commands on terminal to access data")
