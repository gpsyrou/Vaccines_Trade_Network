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

def getAggStatistics(df: pd.core.frame.DataFrame, feature: str,
                     kind: str, year: str) -> pd.core.frame.DataFrame:
    '''
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
    '''
    if year == 'all':
        df = df.loc[df['Trade Flow'] == kind, [feature,
            'Reporter']].groupby(['Reporter']).agg(['sum']).reset_index()
    else:
        df = df.loc[(df['Trade Flow'] == kind) &
                    (df['Period'] > f'{year}-01-01') & (df['Period'] <= f'{year}-12-31'), 
                    [feature,'Reporter']].groupby(['Reporter']).agg(['sum']).reset_index()

    df_sorted = df.sort_values(by=(feature,'sum'), ascending=False)
    
    return df_sorted


def plotTopnCountries(df: pd.core.frame.DataFrame, feature: str,
                      topn: int, kind: str, year: str) -> None:
    '''
    Create a bar plot of the top-N countries compared to an aggregated column.        
    '''
    if kind != 'Import' and kind != 'Export':
        raise ValueError('Trade flow is not set to Import or Export')

    plt.figure(figsize=(8,6))
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
        plt.title(f'Top-{topn} {kind}ers of vaccines around the globe in {year}')
    plt.xlabel(f'{kind}er Country')
    if feature == 'Trade Value (US$)':
        plt.ylabel(f'Total amount of {kind}s in US$')
    else:
        plt.ylabel(f'Total amount of {kind}s in Netweight (kg)')
    plt.grid(True, alpha = 0.3)
    plt.show()


def groupNodesAndAggregate(df, compute_value_per_kg = True)  -> pd.core.frame.DataFrame:
    
    net_df = df.groupby(['Reporter','Partner','Trade Flow']).agg(
        {'Trade Value (US$)':'sum','Netweight (kg)':'sum'}).reset_index()
    
    # Here we will introduce a new feature which is the Price/Kg.
    if compute_value_per_kg:
        net_df['Value_Per_Kg'] = net_df['Trade Value (US$)']/net_df['Netweight (kg)']
        net_df['Value_Per_Kg'].replace([np.inf, -np.inf], 0, inplace=True)
    else:
        pass
    
    return net_df
