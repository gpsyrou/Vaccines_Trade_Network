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
import matplotlib.pyplot as plt
import seaborn as sns

def getAggStatistics(df: pd.core.frame.DataFrame, feature: str,
                     kind: str) -> pd.core.frame.DataFrame:
    '''
    Given a dataframe and a feature column (numerical), identify the top
    importers/exporters.
    
    Args:
    ----
        df: DataFrame that contains the data and the required features.
        feature: Numerical feature to aggregate (e.g. 'Trade Value (US$)', 'Netweight (kg)')
        kind: 'Imports', 'Exports'
    Returns:
    -------
        df_sorted: Sorted dataframe that contains the aggregated values.
    '''
    df = df.loc[df['Trade Flow'] == kind, [feature,
                'Reporter']].groupby(['Reporter']).agg(['sum']).reset_index()

    df_sorted = df.sort_values(by=(feature,'sum'), ascending=False)
    
    return df_sorted


def plotTopnCountries(df: pd.core.frame.DataFrame, feature: str,
                      topn: int, kind: str, year: int) -> None:
    '''
    Create a bar plot of the top-N countries compared to an aggregated column.        
    '''
    if kind != 'Import' and kind != 'Export':
        raise ValueError('Trade flow is not set to Import or Export')

    plt.figure(figsize=(10,10))
    g = sns.barplot(x='Reporter', y=(feature,'sum'), data=df[0:topn],
                    palette='muted')

    if topn > 5 and topn <= 10:
        rot = 60
    elif topn > 10:
        rot = 75
    else:
        rot = 0

    g.set_xticklabels(g.get_xticklabels(), rotation=rot)
    plt.ticklabel_format(style='plain', axis='y')
    plt.title(f'Top-{topn} {kind}ers of vaccines around the globe in {year}')
    plt.xlabel(f'{kind}er Country')
    if feature == 'Trade Value (US$)':
        plt.ylabel(f'Total amount of {kind}s in US$')
    else:
        plt.ylabel(f'Total amount of {kind}s in Netweight (kg)')
    plt.grid(True, alpha = 0.3)
    plt.show()

