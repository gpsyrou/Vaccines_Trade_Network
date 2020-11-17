"""
-------------------------------------------------------------------
-- Title:
-- File:    mainAnalysis.py
-- Purpose: Main data analysis script for the data received regarding the trade (exports/imports) of vaccine products globally for 2019.
-- Author:  Georgios Spyrou
-- Date:    29/03/2020
-------------------------------------------------------------------
"""

import os
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns

project_dir = r'D:\GitHub\Projects\Comtrade_Network'
os.chdir(project_dir)

# Custom packages
from utilities import trade_network_functions as tnf
from VaccinesTradeNetworkClass import VaccinesTradeNetwork

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

'''
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
'''

top_importers_all_years = tnf.getAggStatistics(df, feature='Trade Value (US$)',
                                     kind='Imports', year='all')


# Create a file that will contain the aggregate values per country for all years
top_importers_all_years.to_csv('Merged_Top_Importers_All_Years.csv', index=None)

topImportersDF = pd.read_csv('Merged_Top_Importers.csv',
                             skiprows=[0], header = 0,
                             names=['Reporter', 'Trade Value (US$)', 'Year'])




# Part 2: Network Analysis

# Create the general case of the network (all countries, trade flows, etc)

# In order to create our network we need to transform it in way that can be 
# passed into a Graph object from the networkx library..

network_df = tnf.groupNodesAndAggregate(df, how='month', compute_value_per_kg = True)

argentina = VaccinesTradeNetwork(network_df, country='Argentina')

# Dataframe with all data for a specific country
argentina_df = argentina.createCountrySpecificDF()

graph = argentina.generateCountryGraph(agg=True)

argentina.plotCountryGraph()
argentina.filtered_df



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



# Holt Winter's Exponential Smoothing (HWES)
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.model_selection import train_test_split

train, test = tnf.split_test_train(united_kingdom_ts['Trade Value (US$)'], num_months_test=12)

hwes_model = ExponentialSmoothing(train)
model_fit = hwes_model.fit()

yhat = model_fit.predict(start=len(train), end=len(train))
print(yhat)

# ARIMA
from pandas.tools.plotting import autocorrelation_plot, lag_plot
from statsmodels.tsa.stattools import acf, pacf, adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.arima_model import ARIMA


autocorrelation_plot(united_kingdom_ts['Trade Value (US$)'])

lag_order = 18

# Create a Lag plot
tnf.create_lag_plot(df, lag = lag_order)


# RNN


# Create an object for United Kingdom 
united_kingdom = VaccinesTradeNetwork(df, country='United Kingdom')

united_kingdom_imports_df = united_kingdom.createFlowDF(tradeflow='Imports',
                                                        source='Reporter',
                                                        target='Partner')

united_kingdom_ts = united_kingdom.generateTimeSeries(partner_country='USA',
                                                      timeframe='month')

plt.rcParams['axes.facecolor'] = 'whitesmoke'
united_kingdom.plotTimeSeries(partner_list=['USA'], timeframe='month')


# Architecture for the Neural Network

from keras.models import Sequential
from keras.layers import LSTM
from keras.layers import Dropout
from keras.layers import Dense
from keras.layers import Bidirectional

time_series_uk_to_usa = united_kingdom_ts['Trade Value (US$)']

# Split the series into train and test sets
# parameter num_months_test defines how many months we take as test data
train, test = tnf.split_test_train(time_series_uk_to_usa, num_months_test=12)
print(f'Shape of train is {train.shape}\nShape of test is {test.shape}')


train = train.values.reshape(-1, 1)

# Normalize data
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler(feature_range = (0,1))

train_scaled = scaler.fit_transform(train)

prediction_window = 12

n_steps_past = 12
n_steps_future = 1
n_features = 1

X, y = tnf.split_into_samples(pd.Series(np.concatenate(train_scaled)),
                              n_steps_past=n_steps_past,
                              n_steps_future=n_steps_future)
print(f'Shape of X is {X.shape}\nShape of y is {y.shape}')

X = X.reshape((X.shape[0], n_steps_past, n_features))

# Define the model
model = Sequential()
model.add(Bidirectional(LSTM(50, activation='relu'), input_shape=(n_steps_past, n_features)))
model.add(Dropout(0.2))
model.add(Dense(n_features))
model.compile(optimizer='adam', loss='mean_squared_error')

# Train the model
model.fit(X, y, epochs=500, batch_size=32, verbose=1)


# Reshape the test data
test_reshaped = test.values.reshape(-1, 1)
test_scaled = scaler.transform(test_reshaped)

# Add the last n_steps_past observations to predict the future values
test_series = np.concatenate((train_scaled[-n_steps_past:], test_scaled))

# For the predictions we take run through the n_steps_past values from the training
# data for the first iteration, then predict the next value in the series and this
# value the gets feed into the series to assist with the prediction of the next
# (and so on)
predictions = []
history = train_scaled[-n_steps_past:]
for i in range(n_steps_past):
    x_ser = history[i:i+n_steps_past].reshape((1, n_steps_past, n_features))
    yhat = model.predict(x_ser, verbose=0)
    history = np.vstack((history, yhat))
    predictions.append(scaler.inverse_transform(yhat))
    print(f'Predicted Value: {predictions[i][0]}, true value: {test_reshaped[i]}')


predicted = [i[0][0] for i in predictions]

# Compare the predictions visually
plt.figure(figsize=(8,6))
plt.plot(test[0:prediction_window], marker='.', color= 'blue', label='True')
plt.plot(pd.Series(predicted[0:prediction_window], index=test.index[0:prediction_window]),
         marker='.', color='red', label='Predicted')
plt.grid(True, alpha=0.4)
plt.title('Bidirectional LSTM Neural Network - Results')
plt.legend()

