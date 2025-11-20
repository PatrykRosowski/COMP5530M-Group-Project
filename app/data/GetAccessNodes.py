import naptan
import tabloo

AREA_CODE = "450"
BUS_STOP_TYPE = "BCT"
COLUMNS = ["ATCOCode", "CommonName", "Street", "Longitude", "Latitude", "StopType"]

df_west_york_stops = naptan.get_area_stops([AREA_CODE])
df_west_york_stops_simple = df_west_york_stops.filter(COLUMNS, axis=1)


## Gets all the access node data
def get_all_data():
    return df_west_york_stops_simple


## Gets all the bus stop access node data
def get_bus_stop_data():
    return df_west_york_stops_simple.loc[df_west_york_stops_simple["StopType"] == BUS_STOP_TYPE]


## GET SPECIFIC STREET DATA
def get_street_data(Streets):
    return df_west_york_stops_simple.loc[df_west_york_stops_simple["Street"].isin(Streets)]


## GET SPECIFIC STOP DATA
def get_specific_stop_data(ATCOCode):
    return df_west_york_stops_simple.loc[df_west_york_stops_simple["ATCOCode"] == ATCOCode]
