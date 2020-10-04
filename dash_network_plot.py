import os
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets) 


os.chdir(r'D:\GitHub\Projects\Comtrade_Network')
from VaccinesTradeNetworkClass import VaccinesTradeNetwork

df = pd.read_csv('Networkd_dataframe.csv', header = 0)


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

    # Network plot
    dcc.Graph(id='network_plot')


])

#-------- Callback --------

@app.callback(
    Output(component_id='network_plot', component_property='figure'),
    [Input(component_id='reporter_dropdown', component_property='value')]
)


def update_network(reporter_country):
    cntry = VaccinesTradeNetwork(df, country=reporter_country)

    G = cntry.generateCountryGraph(agg=False)

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

    fig.update_layout(title_text=f'<b><br>Network of {reporter_country} for Human Vaccines (Imports)</b>', 
                    title_x=0.5,
                    title_y=1.0,    
                    font=dict(
                            family="'Oswald', sans-serif",
                            size=12,
                            color="#7f7f7f"
        ))

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
