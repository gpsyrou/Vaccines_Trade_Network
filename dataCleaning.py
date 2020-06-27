"""
-------------------------------------------------------------------
-- Title:
-- File:    cleanData.py
-- Purpose: Data cleaning and processing for the CSV files as received from the data retrieval process (getData.py).
            The script deletes the files that do not contain data, and merges all the rest csv to a unique one.
-- Author:  Georgios Spyrou
-- Date:    29/03/2020
-------------------------------------------------------------------
"""

# Import dependencies
import os
import sys
import csv
import pandas as pd

# Some files received contain no data, as no recorded data exist for all countries.
# Before we merge the files to a unique file that will contain the clean data,
# we will delete the files that contain no relevant data.

# Relative folder path to the executable dataCleaning.py file
dirname = os.path.dirname(__file__)

year = str(sys.argv[1])

csv_loc = os.path.join(dirname, 'CSVFiles', year)


def sniffValidCSV(csv_name: str, csv_folder: str) -> None:
    """
    Sniff a csv file to check if it contains valid data.
    The csv files that are not valid will not have a string 'HS' as their first value of the 'Classification' column.

    Args:
    ----
        csv_name: Path to the csv_file that needs checking.
        csv_folder: Path to the folder that contains all the csv files.
    """
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
        print(f'Badly formated file: {csv_name}')
        os.remove(os.path.join(csv_folder, csv_name))


def readDataFrame(filepath):
    try:
        df = pd.read_csv(os.path.join(filepath), encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(os.path.join(filepath), encoding='latin-1')
    return df


# Run the process to delete the files that do not contain relevant data for our analysis
for file in os.listdir(csv_loc):
    sniffValidCSV(file, csv_loc)

# Merge the clean CSV files to a unique csv file.
combined_csvs = pd.concat([readDataFrame(os.path.join(csv_loc, f)) for f in os.listdir(csv_loc)])

# Create a csv file
if not os.path.exists(os.path.join(dirname, 'Merged_CSVs')):
    os.mkdir(os.path.join(dirname, 'Merged_CSVs'))

combined_csvs.to_csv(f"Merged_CSVs\\Comtrade_Vacciness_Data_{year}", index=False)
