"""
-------------------------------------------------------------------
-- Title:
-- File:    tradeNetworkFunctions.py
-- Purpose: Scripts that contains all the required functions for the main analysis part of the Vaccines network.
-- Author:  Georgios Spyrou
-- Date:    05/04/2020
-------------------------------------------------------------------
"""


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from pandas.plotting import autocorrelation_plot, lag_plot
from statsmodels.tsa.stattools import acf, pacf, adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.arima_model import ARIMA


def getAggStatistics(df: pd.core.frame.DataFrame, feature: str,
                     kind: str, year: str) -> pd.core.frame.DataFrame:
    """
    Given a dataframe and a feature column (numerical), identify the top
    importers/exporters.
    
    Args:
    ----
        df: DataFrame that contains the data and the required features.
        feature: Numerical feature to aggregate (e.g. 'Trade Value (US$)', 'Netweight (kg)')
        kind: 'Imports', 'Exports'
        year: Specify year of interest or 'all' for all years.
    Returns:
    -------
        df_sorted: Sorted dataframe that contains the aggregated values.
    """
    if year == 'all':
        df = df.loc[df['Trade Flow'] == kind, [feature,
            'Year', 'Reporter']].groupby(['Year', 'Reporter']).agg(['sum']).reset_index()
    else:
        df = df.loc[(df['Trade Flow'] == kind) &
                    (df['Period'] > f'{year}-01-01') & (df['Period'] <= f'{year}-12-31'), 
                    [feature,'Reporter']].groupby(['Reporter']).agg(['sum']).reset_index()
    
        df['Year'] = int(year)

    df_sorted = df.sort_values(by=(feature,'sum'), ascending=False)
    
    return df_sorted


def barplotTopnCountries(df: pd.core.frame.DataFrame, feature: str,
                      topn: int, kind: str, year: str, figsize=(12,6)) -> None:
    """
    Create a bar plot of the top-N countries compared to an aggregated column.        
    """
    if kind != 'Import' and kind != 'Export':
        raise ValueError('Trade flow is not set to Import or Export')

    plt.figure(figsize=figsize)
    g = sns.barplot(x='Reporter', y=(feature,'sum'), data=df[0:topn],
                    palette='muted')

    if topn > 5 and topn <= 10:
        rot = 40
    elif topn > 10:
        rot = 75
    else:
        rot = 0

    g.set_xticklabels(g.get_xticklabels(), rotation=rot)
    plt.ticklabel_format(style='plain', axis='y')
    if year == 'all':
        plt.title(f'Top-{topn} {kind}ers of vaccines around the globe')
    else:
        plt.title(f'Top-{topn} {kind}ers of vaccines in {year}')
    plt.xlabel(f'{kind}er Country')
    if feature == 'Trade Value (US$)':
        plt.ylabel(f'Total amount of {kind}s in US$')
    else:
        plt.ylabel(f'Total amount of {kind}s in Netweight (kg)')
    plt.grid(True, alpha = 0.3)
    plt.show()


def groupNodesAndAggregate(df, how='year', compute_value_per_kg=True)  -> pd.core.frame.DataFrame:
    
    if how == 'year':
        dff = df.groupby(['Reporter','Partner','Trade Flow','Period']).agg(
            {'Trade Value (US$)':'sum','Netweight (kg)':'sum'}).reset_index()
    elif how == 'month':
        dff = df.groupby(['Reporter','Partner','Trade Flow','Period']).agg(
            {'Trade Value (US$)':'sum','Netweight (kg)':'sum'}).reset_index()
    else:
        raise ValueError('Incorrect timeframe - Please pick \'month\' or \'year\'')

     # Here we will introduce a new feature which is the Price/Kg.
    if compute_value_per_kg:
        dff['Value_Per_Kg'] = dff['Trade Value (US$)']/dff['Netweight (kg)']
        dff['Value_Per_Kg'].replace([np.inf, -np.inf], 0, inplace=True)
    else:
        pass       
        
    return dff


# Create a lag plot of a Time Series
def create_lag_plot(series_name, lag = 1):
    """
    Plot a lag-plot for a time series for a chosen number of lags
    
    Parameters:
    
    series_name: Name of the Time Series
    lag: Number of lags
    
    """
    plt.figure(figsize = (8,5))
    plt.title('Lag Plot of the Trade Value of Imports')
    plt.xlim(min(series_name), max(series_name))
    plt.ylim(min(series_name), max(series_name))
    lag_plot(series_name, lag = lag)
    plt.show()
    
# Plot ACF or PACF of a Time Series
def plot_acf_pacf(df, lag = 1, kind = 'acf'):
    """
    Plot either Autocorrelation plot(acf) or Partial Autocorrelation plot(pacf)
    for a given time series with a specified lag value
    
    Parameters:
    df: DataFrame
    kind: 'acf' or 'pacf'
    lag: Number of lags to use
    
    """
    if kind not in ['acf','pacf']:
        raise ValueError('Not a valid plot')
    else:
        if kind == 'acf':
            plot_acf(df, lags = lag)
        else:
            plot_pacf(df, lags = lag)
            
    plt.ylabel('Correlation')
    plt.xlabel('Lag Values')
    plt.show()
    
    
# Split the series in Training and Test sets
def split_test_train(df, num_months_test = 1):
    """
    Split a Time Series object into Train and Test sets.
    
    Parameters:
    df: Series object
    num_months_test: Number of months to keep as test set (rest will be training set)
    
    """
    train_set = df.iloc[0:len(df)-num_months_test]
    test_set = df.iloc[len(df)-num_months_test:len(df)]
    
    return train_set, test_set

# Function that calculates the rolling mean and standard deviation, as well as performing the Dickey-Fuller Test
def stationarity_checking(df, window, figsize=(10,6)):
    """
    Function that calculates the rolling mean and standard deviation, 
    as well as performing the Dickey-Fuller Test
    
    Parameters:
    
    df: Time Series object
    window: size of the rolling average window
    
    """ 
    # Calculating rolling mean and standard deviation:
    rolling_mn = df.rolling(window).mean()
    rolling_std = df.rolling(window).std()
    
    plt.figure(figsize=figsize)
    plt.plot(df, color = 'blue',label = 'Original TS')
    plt.plot(rolling_mn, color = 'red', label = 'Rolling Mean')
    plt.plot(rolling_std, color = 'black', label = 'Rolling St.Dev.')
    plt.legend(loc = 'best')
    plt.grid(True, color = 'lightgrey')
    plt.title('Rolling Mean & Standard Deviation of the Trade Value of Vaccines', fontsize = 10)
    
    # Dickey-Fuller test:
    print('Results of Dickey-Fuller Test:')
    fuller_test = adfuller(df, autolag = 'AIC')
    results_ts = pd.Series(fuller_test[0:4], index = ['Test Statistic','P-value','#Lags Used','Number of Observations Used'])
    for key,value in fuller_test[4].items():
        results_ts['Critical Value (%s)'%key] = value
    print(results_ts)
    

def split_into_samples(seq, n_steps_past, n_steps_future):
    """Create a function that splits a Univariate series into
    multiple samples of the form [x1,x2,x3] --> [x4]
    
    Parameters:
    seq (pandas.Series): Univariate series
    n_steps_past (int): Number of steps in the past each sample will have
    n_steps_future (int): Number of future steps
    
    """
    
    X_Series, Y_Series = list(), list()

    for step in range(0,len(seq)): 
        
        val_past = step + n_steps_past
        val_fwd = val_past + n_steps_future
        
        if val_fwd > len(seq):
            break
                
        # Get past values
        X_Series.append(seq.values[step:val_past])
        # Get forward values
        Y_Series.append(seq.values[val_past:val_fwd])

    return np.array(X_Series), np.array(Y_Series)


def compute_RMSE(true_val, predicted_val) -> float:
    '''
    Compute the Root Mean Squared Error (RMSE) for two series - one describing
    the real values and the other the predicted.
    '''
    from sklearn.metrics import mean_squared_error
    rms = np.sqrt(mean_squared_error(np.array(true_val), predicted_val))
    print('RMSE: {0}'.format(rms))
    return rms