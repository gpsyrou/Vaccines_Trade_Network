"""
-------------------------------------------------------------------
-- Title:
-- File:    mainAnalysis.py
-- Purpose: Main data analysis script for the data received regarding the trade (exports/imports) of vaccine products globally for 2019.
-- Author:  Georgios Spyrou
-- Date:    29/03/2020
-------------------------------------------------------------------
"""
''
# Import dependencies
import os
import pandas as pd
import numpy as np

# Custom packages
from Functions import tradeNetworkFunctions as tnf
from VaccinesTradeNetworkClass import VaccinesTradeNetwork

# Plotting and graphs
import matplotlib.pyplot as plt
import seaborn as sns

project_dir = 'C:\\Users\\george\\Desktop\\GitHub\\Projects\\Comtrade_Network'
os.chdir(project_dir)# Read the csv file

# Create a dataframe that contains data from all years
csv_files_loc = os.path.join(project_dir, 'Merged_CSVs')
maindf = pd.concat([pd.read_csv(os.path.join(csv_files_loc,
                                             file)) for file in os.listdir(csv_files_loc)])

# Part 1: Exploratory Data Analysis

# At this stage we need to explore the dataset and identify any potential issues in the data tha require cleaning, and also
# make sure that we understand the features.

summary = maindf.describe()

# As we can see from the summary, few of the features does not seem to provide
# useful information for our analysis, as they either contain only empty values (e.g. 'Qty')
# or they contain fixed values (e.g.'Aggregate Level'). Therefore we will exclude
# the useless columns from our dataset to reduce the noise and the dimensions
# of our feature space.

# Note: More information regarding the feautures can be found here: https://comtrade.un.org/data/MethodologyGuideforComtradePlus.pdf

useful_features_ls = ['Year', 'Period', 'Reporter Code', 'Reporter', 'Partner Code',
                      'Partner', 'Trade Flow', 'Commodity', 'Netweight (kg)',
                      'Trade Value (US$)']
df = maindf[useful_features_ls]


df.groupby(['Reporter']).size()
df.groupby(['Partner']).size()
ls_of_years = list(df.Year.unique())

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


df['Partner'].replace(
    to_replace='United States of America',
    value='USA',
    inplace=True
)

df['Reporter'].replace(
    to_replace='United States of America',
    value='USA',
    inplace=True
)

topn = 15

# Specify if we want to focus on a specific year (e.g. '2018') or 'all'

year = '2017'

# Trade Value
top_importers_2017 = tnf.getAggStatistics(df, feature='Trade Value (US$)',
                                     kind='Imports', year=year)
top_importers_2017[0:topn]


year = '2018'

# Trade Value
top_importers_2018 = tnf.getAggStatistics(df, feature='Trade Value (US$)',
                                     kind='Imports', year=year)
top_importers_2018[0:topn]


year = '2019'

# Trade Value
top_importers_2019 = tnf.getAggStatistics(df, feature='Trade Value (US$)',
                                     kind='Imports', year=year)
top_importers_2019[0:topn]


# Create a file that will contain the aggregate values per country for all years
top_importers_all = [top_importers_2017, top_importers_2018, top_importers_2019]
merged_top_importers = pd.concat(top_importers_all)
merged_top_importers.to_csv('Merged_Top_Importers.csv', index = None)


topImportersDF = pd.read_csv('Merged_Top_Importers.csv',
                             skiprows=[0], header = 0,
                             names=['Reporter', 'Trade Value (US$)', 'Year'])




# Part 2: Network Analysis

# Create the general case of the network (all countries, trade flows, etc)

# In order to create our network we need to transform it in way that can be 
# passed into a Graph object from the networkx library..

network_df = tnf.groupNodesAndAggregate(df, compute_value_per_kg = True)

greece = VaccinesTradeNetwork(network_df, country='Greece')

# Dataframe with all data for a specific country
gr_df = greece.createCountrySpecificDF()

graph = greece.generateCountryGraph(agg=True)

greece.plotCountryGraph()
greece.filtered_df



# Part 3: Time Series Analysis

# Create an object for United Kingdom 
united_kingdom = VaccinesTradeNetwork(df, country='United Kingdom')
united_kingdom_imports_df = united_kingdom.createFlowDF(tradeflow='Imports',
                                                        source='Reporter',
                                                        target='Partner')

united_kingdom_ts = united_kingdom.generateTimeSeries(partner_country='USA',
                                                      timeframe='month')
united_kingdom.plotTimeSeries(partner_list=['USA'], col='Trade Value (US$)',
                              timeframe='month')


united_kingdom_ts.shape
# (120, 7)


######################### ARIMA #############################################
from pandas.tools.plotting import autocorrelation_plot, lag_plot
from statsmodels.tsa.stattools import acf, pacf, adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.arima_model import ARIMA


autocorrelation_plot(united_kingdom_ts['Trade Value (US$)'])

lag_order = 18

# Create a Lag plot
tnf.create_lag_plot(df, lag = lag_order)


################## NN ######################################################























