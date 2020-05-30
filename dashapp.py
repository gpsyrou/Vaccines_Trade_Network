import os
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from VaccinesTradeNetworkClass import VaccinesTradeNetwork

os.chdir('C:\\Users\\george\\Desktop\\GitHub\\Projects\\Comtrade_Network')

df = pd.read_csv('Merged_Top_Importers.csv',
                                   skiprows=[0], header = 0, names=['Reporter', 'TradeValue', 'Year'])

network_df = pd.read_csv('Networkd_dataframe.csv', header = 0)

# Create a Plotly figure for a network object
country = 'Belgium'

cntry = VaccinesTradeNetwork(network_df, country=country)

G = cntry.generateCountryGraph(tradeflow='Imports', source='Reporter',
                            target='Partner', agg=True)

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
        colorscale='Viridis',
        reversescale=True,
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

fig = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=20,r=20,t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                )

fig.update_layout(title_text=f'<b><br>Network of {country} for Human Vaccines (Imports)</b>', 
                title_x=0.5,
                title_y=1.0,    
                font=dict(
                        family="'Oswald', sans-serif",
                        size=12,
                        color="#7f7f7f"
    ))


def YearToObject(x):
    options = []
    for i in x:
        options.append({
            'label': i,
            'value': i
        })
    return options

# Dash App starts here
app = dash.Dash()

app.layout = html.Div([
    # Adding a header
	html.H1(children='Global Trade Network of Human Vaccines', 
		    style={
		    		'textAlign': 'center'}
		    ),

    # Dropdown for picking a year of interest
    html.P([
        html.Label("Please select a year"),
        dcc.Dropdown(
        id = 'first_dropdown',
        options = YearToObject(df.Year.unique()),
        placeholder='Year')]
    ,   style = {'width': '400px',
                'fontSize' : '20px',
                'padding-left' : '100px',
                'display': 'inline-block'}),

    # Bar plot graph 
    html.Div(id='output-graph'),

    # Network plot
    dcc.Graph(id = 'plot', figure = fig)
    ])


@app.callback(
    Output(component_id='output-graph', component_property='children'),
    [Input(component_id='first_dropdown', component_property='value')]
    )

def update_output_div(input_value):
    return dcc.Graph(id = 'Bar_Plor',
                  figure = {
                      'data' : [
                          {'x':df[df['Year']==input_value].Reporter, 'y':df[df['Year']==input_value].TradeValue, 'type':'bar', 'name':'First Chart'}
                          ],
                       'layout':{
                       	  'title':f'<b>Trade Value of Vaccines for {input_value} (Imports)</b>',
                       	  'xaxis':{
                       	  		'title':'Country',
                       	  		'standoff': 50
                       	  },
                       	  'yaxis':{
                       	  		'title':'Trade Value in USD ($)',

                       	  },
                       	  'font':{
                       	  		 'family': "'Oswald', sans-serif",
                       	  		 'size': 12,
                       	  		 'color': "#7f7f7f"
                       	  }
                       }
                      })


if __name__ == '__main__':
    app.run_server(port=4050, debug=True)