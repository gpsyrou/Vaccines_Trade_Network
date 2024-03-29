"""
-------------------------------------------------------------------
-- Title:
-- File:    dataRetrieval.py
-- Purpose: Gather monthly data for multiple years for the imports/exports of Vaccines products around the world, from  https://comtrade.un.org/Data/
-- Author:  Georgios Spyrou
-- Date:    28/03/2020
-------------------------------------------------------------------
"""

# Import dependencies
from typing import List
import requests
import csv
import json
import time
import os
import argparse

parser = argparse.ArgumentParser(description='Provided list of years to retrieve data for')

# Provide as input a list of years
parser.add_argument('-years', '--arg', nargs='+', type=int, dest='years')
args = parser.parse_args()
print('List of years provided {}\n\n Initiating data retrieval process...\n\n'.format(args.years))

# Get the data as separate csv files, each for every year of interest
outputFilesFolder = f'CSVFiles\\'

# Setting up the parameters for the API calls to receive the data
# Reference: https://comtrade.un.org/data/doc/api/#DataAvailabilityRequests

max_rec = 100000
output_fmt = 'csv'
trade_type = 'C'            # Commodities
frequency = 'M'             # Monthly
px = 'HS'                   # Classification for products
cc = 300220                 # Subcategory --> 300220 code for Vaccines
reporter = 'all'
partner = 'all'                 # world
rg ='all'

# Connection string to comtrade.un.org based on the parameters above
api_call_string = f'http://comtrade.un.org/api/get?max={max_rec}&type={trade_type}&freq={frequency}&px={px}&ps=year&r=reporter&p={partner}&rg={rg}&cc={cc}&fmt={output_fmt}'


def collect_data(api_string: str, reporterid: str, reportername: str, year: int, out_folder: str) -> None:
    """
    Create a CSV file that contains the monthly data as received from  https://comtrade.un.org/Data/, for a specified year.

    Args:
    ----
        api_string: String that contains the URL for the API call. The string already contains all the paremeters required for the call.
        reporterid, reportername: Id and Name of the country of interest.
        year: Specify year of interest.
    Returns:
    -------
        None: The output is a .csv file that contains the data for a specified country/year.
    """
    csv_by_year_out_loc = os.path.join(out_folder, f'{year}')
    if not os.path.exists(csv_by_year_out_loc):
        os.makedirs(name=csv_by_year_out_loc)

    api_string = api_string.replace('year', f'{year}').replace('reporter', f'{reporterid}')
    print(api_string)

    response = requests.get(url=api_string, verify=False)

    if response.status_code != 200:
        print('Could not access the API!')
    else:
        decoded_data = response.content.decode('utf-8')
        csv_file = csv.reader(decoded_data.splitlines())
        datalines = list(csv_file)

        with open(os.path.join(csv_by_year_out_loc, f'Comtrade_Vaccines_Data_{reportername}_{year}.csv'), 'w', newline='') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(datalines)


# Retrieve the data

# Because the API doesn not allow to call multiple countries as a Reporter in one call, we will need to create
# separate calls for each country.

# Receive the list of countries and their respective IDs as described in https://comtrade.un.org/Data/cache/reporterAreas.json

reporters_url = 'https://comtrade.un.org/Data/cache/partnerAreas.json'
reporters_resp = requests.get(url=reporters_url, verify=False)
json_data = json.loads(reporters_resp.text)

reporters_list = [rep for rep in json_data['results']]

for api_check, reporter in enumerate(reporters_list):
    # Need to make the script to sleep every 100 calls, as the API is blocking us for an hour for every 100 calls.
    if api_check !=0 and api_check % 100 == 0:
        time.sleep(3600)
    countryname = reporter['text']
    country_id = reporter['id']
    print(f'\nCountry..: {countryname}')
    for year in args.years:
        print(f'\nReceiving the data for {year} from https://comtrade.un.org/...\n')
        collect_data(api_call_string, reporterid=country_id, reportername=countryname, year=year, out_folder=outputFilesFolder)
        time.sleep(6)
