"""
-------------------------------------------------------------------
-- Title:   
-- File:    getData.py
-- Purpose: Gather monthly data for multiple years for the imports/exports of Vaccines products around the world, from  https://comtrade.un.org/Data/
-- Author:  Georgios Spyrou
-- Date:    28/03/2020
-------------------------------------------------------------------
"""

import requests
import csv
import json
import time
import os

# Setting up the parameters for the API calls to received the data
# Reference: https://comtrade.un.org/data/doc/api/#DataAvailabilityRequests

max_rec= 100000
output_fmt = 'csv'
trade_type = 'C'            # Commodities
frequency = 'M'             # Monthly
px = 'HS'                   # Classification for products
cc = 300220                 # Subcategory --> 300220 code for Vaccines
reporter = 'all'
partner = 0                 # world
rg='all'

# Connection string to comtrade.un.org
api_call_string = f'http://comtrade.un.org/api/get?max={max_rec}&type={trade_type}&freq={frequency}&px={px}&ps=year&r={reporter}&p={partner}&rg={rg}&cc={cc}&fmt={output_fmt}'


def getDataCall(api_string: str, year: int, out_folder: str) -> None:
    '''
    Create a .csv file that contains the data as received from  https://comtrade.un.org/Data/, for a specific year.

    Args: 
    ----
        api_string: String that contains the URL for the API call. The string already contains all the paremeters required for the call.
        year: Specify year of interest.
    Returns:
    -------
        None: The output is a .csv file that contains the data for a specified year.
    '''
    api_string = api_string.replace('year',f'{year}')
    print(api_string)

    response = requests.get(url=api_string)

    if response.status_code != 200:
        print('Could not access the API!')
    else:
        decoded_data = response.content.decode('utf-8')
        csv_file = csv.reader(decoded_data.splitlines())
        datalines = list(csv_file)

        with open(os.path.join(outputFilesFolder,f'Comtrade_Vaccines_Data_{year}.csv'), 'w', newline='') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(datalines)

outputFilesFolder = 'CSVFiles\\'
if not os.path.exists(outputFilesFolder):
    os.makedirs(name=outputFilesFolder)

# Get the data as separate csv files, each for every year of interest
years_ls = [2016, 2017, 2018, 2019]

for year in years_ls:
    print(f'Receiving the data for {year} from https://comtrade.un.org/...\n')
    getDataCall(api_call_string, year=year, out_folder=outputFilesFolder)
    time.sleep(5)
