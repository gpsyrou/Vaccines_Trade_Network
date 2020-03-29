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
csv_loc = os.path.join(dirname, 'CSVFiles')

def sniffValidCSV(csv_name: str, csv_folder: str) -> None:
    '''
    Sniff a csv file to check if it contains valid data.
    The csv files that are not valid will not have a string 'HS' as their first value of the 'Classification' column.

    Args:
    ----
        csv_name: Path to the csv_file that needs checking.
        csv_folder: Path to the folder that contains all the csv files.
    '''
    try:
        sniffDf = pd.read_csv(os.path.join(csv_folder, csv_name), delimiter=',', nrows=1, header=[0])
        try:
            if sniffDf['Classification'][0] != 'HS':
                print(f'The file {csv_name} does not contain valid data! Deleting file from directory..\n')
                os.remove(os.path.join(csv_folder, csv_name))
            else:
                print(f'File {csv_name} contained data..\n')
                pass
        except KeyError:
                print(f'The file {csv_name} is not a possible argument combination..\n')
                os.remove(os.path.join(csv_folder, csv_name))
    except OSError:
        print(f'Bad formated file: {csv_name}')


# Run the process to delete the files that do not contain relevant data for our analysis
for file in os.listdir(csv_loc):
    sniffValidCSV(file, csv_loc)
