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

from Functions import tradeNetworkFunctions as tnf

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


    def createFlowDF(self, tradeflow: str, source: str, target: str):
        '''
        Creates  a dataframe on the trade flow, and the source and target
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
        
        return self.filtered_df

    def generateCountryGraph(self, agg: bool) -> nx.classes.digraph.DiGraph:
        '''
        Generates a graph object for a specified country
        Returns:
        -------
            CountryGraph: nx.classes.digraph.DiGraph object containing the graph of the network.
        '''

        self.agg = agg

        if agg  is True:
            self.filtered_df= tnf.groupNodesAndAggregate(self.filtered_df,
                                                         compute_value_per_kg=True)
        
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
        
        graph = self.generateCountryGraph(self.agg)
        
        nx.draw_networkx(graph, node_size=550, font_size=8, width=self.tdv_norm)
        
        plt.title(f'Network of {self.tradeflow} for {self.country}',
                  fontsize=16)
        
    def generateTimeSeries(self, partner_country='all', timeframe=None) -> pd.core.frame.DataFrame:
        '''
        Create a dataframe containing data for a specific partner country and 
        for a predefined timeframe which can be either 'year' or 'month'.
        
        Args:
        ----
            partner_country: 'all' or name of Partner country
            timeframe: 'month' or 'year'
        '''
        
        if partner_country!='all':
            df = self.filtered_df[self.filtered_df['Partner'] == partner_country]
        else:
            df = self.filtered_df
            
        if timeframe == 'year':
            df = tnf.groupNodesAndAggregate(df)
            df['Period'] = df['Year'].map(lambda x: str(x) + '-12-31')
            df.set_index(pd.to_datetime(df['Period']), inplace=True)
        elif timeframe == 'month':
            pass
        else:
            raise ValueError('Incorrect timeframe - Please pick \'month\' or \'year\'')
        
        return df