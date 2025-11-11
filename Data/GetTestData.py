from GetAccessNodes import get_street_data

## Data Structure
##COLUMNS = ['ATCOCode',
##           'CommonName',
##           'Street',
##           'Longitude',
##           'Latitude',
##           'StopType']

def get_test_data():
    #test_streets = ['The Headrow',
    #                'Woodhouse Lane',
    #                'Headingley Lane',
    #                'Wellington Street',
    #                'Vicar Lane',
    #                'Boar Lane',
    #                'Park Row',
    #                'Burley Road',
    #                'Kirkstall Road']
    test_streets = ['The Headrow',
                    'Park Row',
                    'Boar Lane',
                    'Infirmary Street']
    
    return get_street_data(test_streets)