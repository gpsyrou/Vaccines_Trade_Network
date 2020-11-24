import os
import math
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import networkx as nx

# Custom packages
from utilities import trade_network_functions as tnf
from VaccinesTradeNetworkClass import VaccinesTradeNetwork

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets) 

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

df = df[df.Partner != 'World']

df['Period'] = pd.to_datetime(df['Period'], format='%Y%m')

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

    # Dropdown for selecting a reporter country
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

    # Dropdown for selecting a partner country
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

    # Line Plots
    html.Div([
        html.Div([
            html.Div([
                dcc.Graph(id='imports_between_two_countries_value')
            ], className="six columns"),

            html.Div([
                dcc.Graph(id='imports_between_two_countries_kg')
            ], className="six columns"),
        ], className="row")
    ]),

     # Network plot
    dcc.Graph(id='network_plot'), 

    # Data table
    dash_table.DataTable(
        id='table',
        style_table={
            'maxHeight': '50ex',
            'overflowY': 'auto',
            'width': '80%',
            'minWidth': '95%',
            'margin-left': '80px',
            'margin-right': '80px'
        },

        style_cell={'textAlign': 'left'}, 

        fixed_rows={'headers': True},
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ],
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        })

])
#-------- Callback --------

@app.callback(
    [Output(component_id='imports_between_two_countries_value', component_property='figure'),
     Output(component_id='imports_between_two_countries_kg', component_property='figure'),
     Output(component_id='network_plot', component_property='figure'),
     Output(component_id='table', component_property='data'),
     Output(component_id='table', component_property='columns')],
    [Input(component_id='reporter_dropdown', component_property='value'),
    Input(component_id='partner_dropdown', component_property='value')]
)

def update_lineplot(reporter_country, partner_country):
    print(reporter_country)
    print(partner_country)
    
    df_cp = df.copy()
    df_cp = VaccinesTradeNetwork(df_cp, country=reporter_country)

    df_as_timeseries = df_cp.generateTimeSeries(partner_country=partner_country, timeframe='month')

    # Lineplot for Trade Value
    fig_lineplot_val = go.Figure()

    fig_lineplot_val.add_trace(go.Scatter(
        x=df_as_timeseries['Period'],
        y=df_as_timeseries['Trade Value (US$)'],
        name='Trade Value (US$)',
        line=dict(color='royalblue', width=2),
        mode='lines+markers'))

    fig_lineplot_val.update_layout(
        xaxis_title='Period',
        yaxis_title='Trade Value',
        title='Monthly Change of Trade Value in US$',
        title_x=0.10,
        title_y=0.85, 
        font=dict(
            family="'Oswald', sans-serif",
            size=12,
            color="#7f7f7f"
        ))

    # Lineplot for Value per Kg
    fig_lineplot_kg = go.Figure()
    fig_lineplot_kg.add_trace(go.Scatter(
        x=df_as_timeseries['Period'],
        y=df_as_timeseries['Value_Per_Kg'],
        name='Value Per Kg',
        line=dict(color='firebrick', width=2),
        mode='lines+markers'))

    fig_lineplot_kg.update_layout(
        xaxis_title='Period',
        yaxis_title='Value_Per_Kg',
        title='Change of Value per Kilogram in US$',
        title_x=0.10,
        title_y=0.85,  
        font=dict(
            family="'Oswald', sans-serif",
            size=12,
            color="#7f7f7f"
        ))

    # Network graph
    G = df_cp.generateCountryGraph(agg=True)
    
    pos = nx.layout.spring_layout(G)

    edge_x = []
    edge_y = []
    node_trade_values = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)
        node_trade_values.append(G.edges[edge]['Trade Value (US$)'])

    # Set up the Edges
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.7, color='#888'),
        hoverinfo='text',
        mode='lines')

    node_x = []
    node_y = []
    node_text = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)

    # Set up the Nodes
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='Redor',
            reversescale=False,
            color=[],
            size=16,
            colorbar=dict(
                thickness=15,
                title='Trade Value (US$)',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))

    node_trace.marker.color = node_trade_values
    node_trace.text = node_text

    fig_network = go.Figure(data=[edge_trace, node_trace],
                layout=go.Layout(
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=80,r=40,t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )

    fig_network.update_layout(title_text=f'<b><br>Network of imports for {reporter_country}</b>', 
                    title_x=0.05,
                    title_y=1.0,    
                    font=dict(
                            family="'Oswald', sans-serif",
                            size=12,
                            color="#7f7f7f"
        ))

    # Data Table
    columns=[{"name": i, "id": i} for i in df_as_timeseries.columns]
    data = df_as_timeseries.to_dict(orient='records')

    return fig_lineplot_val, fig_lineplot_kg, fig_network, data, columns


if __name__ == '__main__':
    app.run_server(debug=True)