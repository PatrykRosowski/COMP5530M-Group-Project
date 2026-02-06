from GetAccessNodes import get_street_data

# Data Structure
# COLUMNS = ['ATCOCode',
#           'CommonName',
#           'Street',
#           'Longitude',
#           'Latitude',
#           'StopType']


def get_test_data():
    """
    test_streets = ['Parliament Street']
    """
    test_streets = [
        "Parliament Street",
        "Cheltenham Parade",
        "Station Parade",
        "W Park",
        "Montpellier Hill",
    ]

    return get_street_data(test_streets)
