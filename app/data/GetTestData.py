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
    test_streets = ['The Headrow',
                    'Woodhouse Lane', # disconnected
                    'Headingley Lane',
                    'Wellington Street', # disconnected
                    'Vicar Lane', # disconnected
                    'Boar Lane',
                    'Park Row',
                    'Infirmary Street',
                    'Burley Road', # disconnected
                    'Kirkstall Road']
    """
    test_streets = ["The Headrow"]

    return get_street_data(test_streets)
