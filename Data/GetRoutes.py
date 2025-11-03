import requests
import zipfile
import io
API_KEY = 'ca19a3e46de3564c0669e6bb7c6c510ef9817484'
FIRSTBUS_HUNSLET_DATASET_ID = '18326'

## https://data.bus-data.dft.gov.uk/guidance/requirements/?section=databyoperator

## Create account and go to account settings to get API KEY. 
data =requests.get(f'https://data.bus-data.dft.gov.uk/api/v1/dataset/{FIRSTBUS_HUNSLET_DATASET_ID}/?api_key={API_KEY}')

## Get URL of dataset
dataset_url = data.json()['url']

## Extracting ZIP file for dataset
dataset_zip_file_request = requests.get(dataset_url)
dataset_zip_file = zipfile.ZipFile(io.BytesIO(dataset_zip_file_request.content))

## Printing names of all files in the zip folder
with dataset_zip_file as dataset:
    print(dataset.infolist())
