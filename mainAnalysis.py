"""
-------------------------------------------------------------------
-- Title:
-- File:    mainAnalysis.py
-- Purpose: Main data analysis script for the data received regarding the trade (exports/imports) of vaccine products globally for 2019.
-- Author:  Georgios Spyrou
-- Date:    29/03/2020
-------------------------------------------------------------------
"""

# Import dependencies
import pandas as pd

csv_file_location = 'C:\\Users\\george\\Desktop\\GitHub\\Projects\\Comtrade_Network\\Merged_CSVs\\Comtrade_Vacciness_Data_2019'
# Read the csv file
maindf = pd.read_csv(csv_file_location, delimiter=',', header=[0], encoding='utf-8')

maindf.shape # (12863, 35)
maindf.head(10)

df = maindf[['Period', 'Reporter', 'Partner', 'Trade Flow', 'Commodity','Trade Value (US$)', 'Qty Unit', 'Qty']]

df.groupby(['Reporter', 'Partner'])['Trade Value (US$)'].sum()