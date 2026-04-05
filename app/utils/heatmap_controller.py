# Imports
import csv
import pandas as pd
import gmplot
import random
import json
from pathlib import Path

# Constants
HEATMAP_DATA = "app/utils/HeatmapData/ManchesterPopulationDensity.csv"
LSOA_LOOKUP = "app/utils/HeatmapData/LSOA_Lookup.csv"
POINT_PAIRS_FILE = "app/utils/HeatmapData/PointPairs.json"


# Transforms heatmap data CSV to tabular data
def transform_heatmap_data():

    raw_heatmap_df = pd.DataFrame(columns=["Population Density", "LSOACode"])
    # Getting the csv data for the heatmap
    with open(HEATMAP_DATA, newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=",", quotechar="|")
        i = 0
        for row in reader:
            raw_heatmap_df.loc[i] = [row[0], row[2].replace('"', "")]
            i += 1

    raw_lookup_df = pd.DataFrame(columns=["LSOACode", "Latitude", "Longitude"])
    # Getting the csv data for the lookup
    with open(LSOA_LOOKUP, newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=",", quotechar="|")
        i = 0
        for row in reader:
            raw_lookup_df.loc[i] = [row[1], row[6], row[7]]
            i += 1

    # Inner merge both dataframes together to get coordinate data and heatmap data
    # Population Density, LSOACode, Latitude, Longitude
    heatmap_df = pd.merge(raw_heatmap_df, raw_lookup_df, on="LSOACode")

    return heatmap_df


# Return a k-random amount of pairs, with higher densities more likely to be produced
def get_heatmap_pairs(k):

    # If file exists, return those point pairs instead.
    if Path(POINT_PAIRS_FILE).exists():
        with open(POINT_PAIRS_FILE, "r") as file:
            data = json.load(file)
            if len(data) >= k:
                return data[:k]  # Return only k pieces of data

    pointPairs = []
    # Fetch the table with heatmap values
    heatmap_df = transform_heatmap_data()

    # Using pandas dataframe sample method to select random pairs, with a higher chance of high-density areas
    # being selected, dropping unneccesary columns
    choices = (heatmap_df.sample(k * 2, weights="Population Density", replace=True)).drop(
        columns=["Population Density", "LSOACode"]
    )
    # Turn into a list out of a dataframe
    choices = choices.values.tolist()

    # Iterate through list and append pairs to pointPairs list
    for i in range(0, len(choices), 2):
        ## CONVERT TO INTEGER
        initialPoint = list(map(float, choices[i]))
        targetPoint = list(map(float, choices[i + 1]))

        # Add a random variance to ensure not all at same point
        variance = random.randint(-20, 20)
        variance = variance / 10000
        initialPoint[0] += variance
        initialPoint[1] += variance
        targetPoint[0] += variance
        targetPoint[1] += variance

        pointPairs.append([initialPoint, targetPoint])

    return pointPairs


def mapped_example():

    gmap = gmplot.GoogleMapPlotter(53.9921, 1.5418, 13)

    pointPairs = get_heatmap_pairs(1000)

    with open(POINT_PAIRS_FILE, "w") as file:
        json.dump(pointPairs, file, indent=1)

    # Plotting points
    for pointPair in pointPairs:
        gmap.marker(pointPair[0][0], pointPair[0][1])
        gmap.marker(pointPair[1][0], pointPair[1][1])

    gmap.draw("exampleHeatmapPairs.html")


mapped_example()
