"""
-------------------------------------------------------------------
-- Title:
-- File:    cleanData.py
-- Purpose: Data cleaning and processing for the CSV files as received from the data retrieval process (getData.py)
-- Author:  Georgios Spyrou
-- Date:    29/03/2020
-------------------------------------------------------------------
"""

# Import dependencies
import os
import csv
import pandas as pd

# Some files received contain no data, as no recorded data exist for all countries.
# Before we merge the files to a unique file that will contain the clean data, 
# we will delete the files that contain no relevant data.

# Relative folder path to the executable dataCleaning.py file
dirname = os.path.dirname(__file__)
csv_loc = 'C:\\Users\\george\\Desktop\\GitHub\\Projects\\Comtrade_Network\\CSVFiles'
csv_loc = os.path.join(dirname, 'CSVFiles')

def sniffValidCsv(csv_name: str, csv_loc: str) -> None:
    sniffDf = pd.read_csv(csv_name, delimiter=',', nrows=1, header=[0])
    if sniffDf['Classification'][0] != 'HS':
        print(f'The file {csv_name} does not contain valid data! Deleting file from directory..\n')
        os.remove(os.path.join(csv_loc, csv_name))
    else:
        pass

