import os
import pandas as pd

import plotly.express as px

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

#------ Import data and clean up the dataframe ------
project_dir = r'D:\GitHub\Projects\Comtrade_Network'
os.chdir(project_dir)# Read the csv file

# Create a dataframe that contains data from all years
csv_files_loc = os.path.join(project_dir, 'Merged_CSVs')
df = pd.concat([pd.read_csv(os.path.join(csv_files_loc,
                                             file)) for file in os.listdir(csv_files_loc)])


useful_features_ls = ['Year', 'Period', 'Reporter Code', 'Reporter', 'Partner Code',
                      'Partner', 'Trade Flow', 'Commodity', 'Netweight (kg)',
                      'Trade Value (US$)']

df = df[useful_features_ls]

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

#------- Data loading and cleaning finishes here ------- 

#------- App Layout ---------------

app.layout = html.Div([
    html.H1("Global Trade Network of Human Vaccines", style={'text-align': 'center'}),

    dcc.Dropdown(id='select_year',
                options=[
                    {"label": "2010", "value": 2010},
                    {"label": "2011", "value": 2011},
                    {"label": "2012", "value": 2012},
                    {"label": "2013", "value": 2013},
                    {"label": "2014", "value": 2014},
                    {"label": "2015", "value": 2015},
                    {"label": "2016", "value": 2016},
                    {"label": "2017", "value": 2017},
                    {"label": "2018", "value": 2018},
                    {"label": "2019", "value": 2019}],
                multi=False,
                value=2010,
                style={'widht': "40%"}   
                ),


])


if __name__ == '__main__':
    app.run_server(debug=True)