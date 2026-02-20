# Guide to the JSON data 

## Stops :

JSON data AllBusStops.json is an <u>array</u> of bus-stop data extracted from each file.<br>
jsonStopData[i] corresponds to all the bus-stop data in the 'i'th file.

jsonStopData[i] stores these rows of bus-stops data within file 'i' in an <u>array</u>.<br>
jsonStopData[i][j] corresponds to the 'j'th bus-stop data.

Each bus-stop data is a <u>JSON object</u> with attributes;
- Bus stop ATCO code 'StopPointRef'
- Common Name of the bus stop 'CommonName'
- Locality of the bus stop 'LocalityName'

### jsonStopData is structured as;

[<br>
&emsp;[<br>
&emsp;&emsp;{'StopPointRef': '3200YNA01361', 'CommonName': 'Crossroads', 'LocalityName': 'Aldborough'},<br>
&emsp;&emsp;{'StopPointRef': '3200YNA01362', 'CommonName': 'Crossroads', 'LocalityName': 'Aldborough'},<br>
&emsp;&emsp;{'StopPointRef': '3200YNA01360', 'CommonName': 'The Square', 'LocalityName': 'Aldborough'},<br>
&emsp;&emsp;{ ... }, <br>
&emsp;],<br><br>
&emsp;[<br>
&emsp;&emsp;{'StopPointRef': '3200YND20610', 'CommonName': 'Albany Road', 'LocalityName': 'Bilton'},<br>
&emsp;&emsp;{'StopPointRef': '3200YNA96952', 'CommonName': 'Bachelor Gardens', 'LocalityName': 'Bilton'},<br>
&emsp;&emsp;{'StopPointRef': '3200YND20470', 'CommonName': 'Bachelor Gardens', 'LocalityName': 'Bilton'},<br>
&emsp;&emsp;{ ... }, <br>
&emsp;],<br><br>
&emsp;[<br>
&emsp;&emsp;...<br>
&emsp;],<br>
]


## Routes :

JSON data AllRoutesData.json is an <u>array</u> of route data extracted from each file.<br>
jsonRouteData[i] corresponds to all the route data available in the 'i'th file.

jsonRouteData[i] stores these rows of route data within file 'i' in an <u>array</u>.<br>
jsonRouteData[i][j] corresponds to the 'j'th row of route data i.e. the route from bus-stop 'j' to bus-stop 'j+1'.

Each line of data is a <u>JSON object</u> with attributes;
- Starting bus-stop 'Start'
- Next bus-stop 'End'
- Distance between both bus-stops 'Distance'
- Certain location markers between both bus-stops 'Route Track'

### jsonRouteData is structured as;

[<br>
&emsp;[<br>
&emsp;&emsp;{'Start': '3200YND10825', 'End': '3200YND10830', 'Distance': '500', 'Route Track': { ... } },<br>
&emsp;&emsp;{'Start': '3200YND10830', 'End': '3200YND56000', 'Distance': '742' 'Route Track': { ... } },<br>
&emsp;&emsp;{'Start': '3200YND56000', 'End': '3200YNA97033', 'Distance': '354' 'Route Track': { ... } },<br>
&emsp;&emsp;{ ... },<br>
&emsp;],<br><br>
&emsp;[<br>
&emsp;&emsp;{'Start': '3200YND12960', 'End': '3200YND12970', 'Distance': '433' 'Route Track': { ... } },<br>
&emsp;&emsp;{'Start': '3200YND12970', 'End': '3200YND12980', 'Distance': '333' 'Route Track': { ... } },<br>
&emsp;&emsp;{'Start': '3200YND12980', 'End': '3200YND12990', 'Distance': '960' 'Route Track': { ... } },<br>
&emsp;&emsp;{ ... },<br>
&emsp;],<br><br>
&emsp;[<br>
&emsp;&emsp;...<br>
&emsp;],<br>
]

Where each Route Track attribute is of the form { 'LocationID': (Latitude, Longitude) }, as follows;<br>
{<br>
&ensp;'L1': ('54.007703587', '-1.465312652'),<br>
&ensp;'L2': ('54.007741798', '-1.465417486'),<br>
&ensp;'L3': ('54.007806598', '-1.465519586'),<br>
&ensp;...<br>
}
