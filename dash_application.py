import os
import math
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go

import dash
import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Input, Output

# Custom packages
from utilities import trade_network_functions as tnf
from VaccinesTradeNetworkClass import VaccinesTradeNetwork

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

df = df[df['Reporter'].notna()]

#------- Data loading and cleaning finishes here ------- 

#------- App Layout ---------------

def SelectionToObject(x):
    options = []
    for i in x:
        options.append({
            'label': i,
            'value': i
        })
    return options

app.layout = html.Div([
    html.H1("Global Trade Network of Human Vaccines", style={'text-align': 'center'}),

    # Dropdown for selecting a year
    html.P([
        html.Label("Please select an importer country"),
        dcc.Dropdown(
        id = 'reporter_dropdown',
        options = SelectionToObject(df.Reporter.unique()),
        placeholder='Importer')]
    ,   style = {'width': '400px',
                'fontSize' : '20px',
                'padding-left' : '100px',
                'display': 'inline-block'}),

    # Dropdown for selecting a country
    html.P([
        html.Label("Please select an exporter country"),
        dcc.Dropdown(
        id = 'partner_dropdown',
        options = SelectionToObject(df.Partner.unique()),
        placeholder='Exporter')]
    ,   style = {'width': '400px',
                'fontSize' : '20px',
                'padding-left' : '100px',
                'display': 'inline-block'}),

    html.Div(children=[
        html.Div(
            dcc.Graph(
                id='imports_between_two_countries_value',
                style={'width': '1200'},
            ), style={'display': 'inline-block'}),
        html.Div(
            dcc.Graph(
                id='imports_between_two_countries_kg',
                style={'width': '1200'},
            ), style={'display': 'inline-block'})
    ], style={'width': '120%', 'display': 'inline-block'})

])
#-------- Callback --------

@app.callback(
    [Output(component_id='imports_between_two_countries_value', component_property='figure'),
     Output(component_id='imports_between_two_countries_kg', component_property='figure')],
    [Input(component_id='reporter_dropdown', component_property='value'),
    Input(component_id='partner_dropdown', component_property='value')]
)

def update_lineplot(reporter_country, partner_country):
    print(reporter_country)
    print(partner_country)
    
    df_cp = df.copy()
    df_cp = VaccinesTradeNetwork(df_cp, country=reporter_country)

    df_as_timeseries = df_cp.generateTimeSeries(partner_country=partner_country, timeframe='month')

    fig_lineplot_val = go.Figure()
    fig_lineplot_val.add_trace(go.Scatter(x=df_as_timeseries['Period'], y=df_as_timeseries['Trade Value (US$)'], name='Trade Value (US$)',
                         line=dict(color='royalblue', width=2), mode='lines+markers'))
    fig_lineplot_val.update_layout(xaxis_title='Period', yaxis_title='Trade Value (US$)', title='Change of Trade Value', font_family="Arial", font_color="black")

    fig_lineplot_kg = go.Figure()
    fig_lineplot_kg.add_trace(go.Scatter(x=df_as_timeseries['Period'], y=df_as_timeseries['Value_Per_Kg'], name='Value Per Kg',
                        line=dict(color='firebrick', width=2), mode='lines+markers'))
    fig_lineplot_kg.update_layout(xaxis_title='Period', yaxis_title='Value_Per_Kg', title='Change of Value per Kg', font_family="Arial", font_color="black")

    return fig_lineplot_val, fig_lineplot_kg


if __name__ == '__main__':
    app.run_server(debug=True)