"""
-------------------------------------------------------------------
-- Title:
-- File:    VaccinesTradeNetworkClass.py
-- Purpose: Creation of a class to handle network graph objects.
-- Author:  Georgios Spyrou
-- Date:    05/04/2020
-------------------------------------------------------------------
"""


import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt

class VaccinesTradeNetwork:
    """
    Class to create a filtered dataframe and network functions for a specified Country, 
    based on a given network that contains the data for all the countries and their trade relationship.
    """


    def __init__(self, df, country: str):
        self.df = df
        self.country = country


    def createCountrySpecificDF(self) -> pd.core.frame.DataFrame:
        '''
        Filter the main dataframe to specific country. The dataframe will contain
        data where the 'Reporter' = country or 'Partner' = country.
        
        Returns:
        -------
            country_df: Filtered dataframe for a specified country.
        '''
        self.country_df = self.df[(self.df['Reporter']==self.country) | (self.df['Partner']==self.country) ]
        return self.country_df


    def generateCountryGraph(self, tradeflow: str, source: str, target: str):
        '''
        '''
        self.tradeflow  = tradeflow
        self.source = source
        self.target = target
        country_df = self.createCountrySpecificDF()
        
        self.CountryGraph = nx.from_pandas_edgelist(country_df[country_df['Trade Flow']==self.tradeflow],
                                         source=self.source, target=self.target,
                                         edge_attr=['Trade Value (US$)', 'Netweight (kg)','Value_Per_Kg'],
                                         create_using=nx.DiGraph())

        return self.CountryGraph


    def plotCountryGraph(self):

        plt.figure(figsize=(15,15))
        
        tradevalue_w = [G[u][v]['Trade Value (US$)'] for u,v in G.edges()]
        valueperkg_w = [int(G[u][v]['Value_Per_Kg']) for u,v in G.edges()]
        
        # Normalize the values of the trade value to appropriate values between 1-10
        tdv_norm = [int(((x - np.min(tradevalue_w)) / (np.max(tradevalue_w) - 
                     np.min(tradevalue_w)) + 0.6 )* 4) for x in tradevalue_w]
        
        nx.draw_networkx(G, node_size=550, font_size=8, width=tdv_norm)



df_i = VaccinesTradeNetwork(network_df, country='Philippines')

df_i.createCountrySpecificDF()

df_i.generateCountryGraph(tradeflow='Imports', sourceflow='Reporter', targetflow='Partner')