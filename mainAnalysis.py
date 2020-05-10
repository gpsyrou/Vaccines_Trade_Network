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
import os
import pandas as pd
import numpy as np

from Functions import tradeNetworkFunctions as tnf
from VaccinesTradeNetworkClass import VaccinesTradeNetwork

# Plotting and graphs
import matplotlib.pyplot as plt
import seaborn as sns

csv_file_location = 'C:\\Users\\george\\Desktop\\GitHub\\Projects\\Comtrade_Network\\Merged_CSVs\\Comtrade_Vacciness_Data_2018'
# Read the csv file
maindf = pd.read_csv(csv_file_location, delimiter=',',
                     header=[0], encoding='utf-8')

# Part 1: Exploratory Data Analysis

# At this stage we need to explore the dataset and identify any potential issues in the data tha require cleaning, and also
# make sure that we understand the features.

summary = maindf.describe()

year = 2018

# As we can see from the summary, few of the features does not seem to provide
# useful information for our analysis, as they either contain only empty values (e.g. 'Qty')
# or they contain fixed values (e.g.'Aggregate Level'). Therefore we will exclude
# the useless columns from our dataset to reduce the noise and the dimensions
# of our feature space.

# Note: More information regarding the feautures can be found here: https://comtrade.un.org/data/MethodologyGuideforComtradePlus.pdf

useful_features_ls = ['Period', 'Reporter Code', 'Reporter', 'Partner Code',
                      'Partner', 'Trade Flow', 'Commodity', 'Netweight (kg)',
                      'Trade Value (US$)']
df = maindf[useful_features_ls]


df.groupby(['Reporter']).size()
df.groupby(['Partner']).size()


# We will consider both 'Re-imports' and 'Re-exports' as 'Imports' and 'Exports'
# respectively and we will drop the entries where we dont have info about
# the trade flow.
df['Trade Flow'].unique()

trade_flow_dict = {'Re-imports':'Imports', 
                   'Re-exports':'Exports',
                   'Imports':'Imports', 
                   'Exports':'Exports'}

df['Trade Flow'] = df['Trade Flow'].map(trade_flow_dict)

# Now we can observe that we have a node called 'World' but we would like to 
# analyze the trade relationships between specific countries. Thus we will
# exclude from the analysis the cases where the reporter or partner is 'World'
df = df[df.Partner != 'World']

# Period will be our datetime column
df['Period'] = pd.to_datetime(df['Period'], format='%Y%m')

# Except the nodes of our analysis which will correspond to countries, the other
# main features of interest are the Netweigh of the export/import in kilograms
# as well as the Trade Value in US dollars($).

# Lets find the top  countries that import/export vaccines in terms of US dollars.
topn = 10

# Trade Value
top_importers = tnf.getAggStatistics(df, feature='Trade Value (US$)',
                                     kind='Imports')
top_exporters = tnf.getAggStatistics(df, feature='Trade Value (US$)',
                                     kind='Exports')

tnf.plotTopnCountries(df=top_importers, feature='Trade Value (US$)',
                      topn=topn, kind='Import', year=year)
tnf.plotTopnCountries(df=top_exporters, feature='Trade Value (US$)',
                      topn=topn, kind='Export', year=year)


# Netweight
top_importers = tnf.getAggStatistics(df, feature='Netweight (kg)',
                                     kind='Imports')
top_exporters = tnf.getAggStatistics(df, feature='Netweight (kg)',
                                     kind='Exports')

tnf.plotTopnCountries(df=top_importers, feature='Netweight (kg)',
                      topn=topn, kind='Import', year=year)
tnf.plotTopnCountries(df=top_exporters, feature='Netweight (kg)',
                      topn=topn, kind='Export', year=year)


# Part 2: Network Analysis

# Create the general case of the network (all countries, trade flows, etc)

# In order to create our network we need to transform it in way that can be 
# passed into a Graph object from the networkx library..

network_df = tnf.groupNodesAndAggregate(df, compute_value_per_kg = True)

greece = VaccinesTradeNetwork(network_df, country='Greece')

graph = greece.generateCountryGraph(tradeflow='Imports', source='Reporter',
                            target='Partner', agg=True)


greece.plotCountryGraph()
greece.filtered_df