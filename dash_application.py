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
        html.Label("Please select a year"),
        dcc.Dropdown(
        id = 'years_dropdown',
        options = SelectionToObject(df.Year.unique()),
        placeholder='Year')]
    ,   style = {'width': '400px',
                'fontSize' : '20px',
                'padding-left' : '100px',
                'display': 'inline-block'}),

    # Dropdown for selecting a country
    html.P([
        html.Label("Please select an importer country"),
        dcc.Dropdown(
        id = 'countries_dropdown',
        options = SelectionToObject(df.Partner.unique()),
        placeholder='Country')]
    ,   style = {'width': '400px',
                'fontSize' : '20px',
                'padding-left' : '100px',
                'display': 'inline-block'}),


    dcc.Graph(id='imports_over_years_per_country', figure={})

])


#-------- Callback --------

@app.callback(
    Output(component_id='imports_over_years_per_country', component_property='figure'),
    [Input(component_id='years_dropdown', component_property='value'),
    Input(component_id='countries_dropdown', component_property='value')]
)



if __name__ == '__main__':
    app.run_server(debug=True)