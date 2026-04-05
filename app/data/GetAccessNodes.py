import naptan

# Harrogate :
# AREA_CODES = ["320" , "450"]    # North Yorkshire (320) West Yorkshire (450) post code

# Manchester :
AREA_CODES = ["180", "069", "450", "060", "100", "280"]  # Manchester post code


BUS_STOP_TYPE = "BCT"
COLUMNS = ["ATCOCode", "CommonName", "Street", "Longitude", "Latitude", "StopType"]

df_west_york_stops = naptan.get_area_stops(AREA_CODES)
df_west_york_stops_simple = df_west_york_stops.filter(COLUMNS, axis=1)


# Gets all the access node data
def get_all_data():
    return df_west_york_stops_simple


# Gets all the bus stop access node data
def get_bus_stop_data():
    return df_west_york_stops_simple.loc[df_west_york_stops_simple["StopType"] == BUS_STOP_TYPE]


# GET SPECIFIC STREET DATA
def get_street_data(Streets):
    return df_west_york_stops_simple.loc[df_west_york_stops_simple["Street"].isin(Streets)]


# GET SPECIFIC STOP DATA
def get_specific_stop_data(ATCOCode):
    return df_west_york_stops_simple.loc[df_west_york_stops_simple["ATCOCode"].isin(ATCOCode)]
