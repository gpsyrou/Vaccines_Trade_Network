"""
-------------------------------------------------------------------
-- Title:
-- File:    VaccinesTradeNetworkClass.py
-- Purpose: Creation of a class to handle network graph objects.
-- Author:  Georgios Spyrou
-- Date:    11/04/2020
-------------------------------------------------------------------
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx


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


    def generateCountryGraph(self, tradeflow: str, source: str, target: str) -> nx.classes.digraph.DiGraph:
        '''
        Creates  a graph object based on the trade flow, and the source and target
        node directions for the directed graph. Each edge represents a country (Node A) that is either
        importing or exporting to another country (Node B).
        
        Therefore we will have cases like: NodeA ---> NodeB (A exports to B)
                                           NodeA <--- NodeB (A imports from B)
        
        Import tag:
            Country in Reporter , 'Imports' in flow
            Country in Partner,   'Exports' in flow
        
        Export tag:
            Country in Reporter, 'Exports' in flow
            Country in Partner,  'Imports' in flow
            
        Args:
        ----
            tradeflow: 'Imports' or 'Exports' -> Indicating the flow of interest for the base node (NodeA)
            source: Default is 'Reporter'. It can change to 'Partner' if we want to change the direction.
            target: Default is 'Partner'. It can change to 'Reporter' if we want to change the direction.
            
        Returns:
        -------
            CountryGraph: nx.classes.digraph.DiGraph object containing the graph of the network.
        '''

        self.tradeflow  = tradeflow
        self.source = source
        self.target = target
        
        if self.tradeflow == 'Imports':
            self.opposite_flow = 'Exports'
        else:
            self.opposite_flow = 'Imports'

        self.filtered_df = self.createCountrySpecificDF().copy(deep=True)
        
        self.filtered_df = self.filtered_df[((self.filtered_df['Trade Flow']==self.tradeflow) &
                                             (self.filtered_df['Reporter']==self.country)) | 
                                            ((self.filtered_df['Trade Flow']==self.opposite_flow) &
                                             (self.filtered_df['Partner']==self.country))]

        self.filtered_df[[self.source, self.target]] = self.filtered_df[[self.target,
                        self.source]].where(self.filtered_df['Trade Flow'] == self.opposite_flow,
                        self.filtered_df[[self.source, self.target]].values)
                                            
        self.filtered_df['Trade Flow'].replace({self.tradeflow: self.tradeflow, self.opposite_flow: self.tradeflow}, inplace=True)  
        
        self.CountryGraph = nx.from_pandas_edgelist(self.filtered_df,
                                         source=self.source, target=self.target,
                                         edge_attr=['Trade Value (US$)', 'Netweight (kg)','Value_Per_Kg'],
                                         create_using=nx.DiGraph())

        self.tradevalue_w = [self.CountryGraph[u][v]['Trade Value (US$)'] for u,v 
                             in self.CountryGraph.edges()]

        self.valueperkg_w = [int(self.CountryGraph[u][v]['Value_Per_Kg']) for u,v 
                             in self.CountryGraph.edges()]
        
        if self.tradeflow == 'Imports':
            return self.CountryGraph.reverse()
        else:
            return self.CountryGraph


    def plotCountryGraph(self):
        plt.figure(figsize=(15,15))
        
        # Normalize the values of the trade value to appropriate values between 1-10
        self.tdv_norm = [int(((x - np.min(self.tradevalue_w)) / (np.max(self.tradevalue_w) - 
                     np.min(self.tradevalue_w)) + 0.6 )* 4) for x in self.tradevalue_w]
        
        graph = self.generateCountryGraph(self.tradeflow, self.source, self.target)
        nx.draw_networkx(graph, node_size=550, font_size=8, width=self.tdv_norm)
        plt.title(f'Network of {self.tradeflow} for {self.country}')

'''
df_i = VaccinesTradeNetwork(network_df, country='Greece')

G = df_i.generateCountryGraph(tradeflow='Exports', source='Reporter', target='Partner')

df_i.plotCountryGraph()
f = df_i.country_df
f = df_i.filtered_df
'''
