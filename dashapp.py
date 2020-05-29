import os
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

os.chdir('C:\\Users\\george\\Desktop\\GitHub\\Projects\\Comtrade_Network')

topn = 10

merged_top_importers = pd.read_csv('Merged_Top_Importers.csv',
                                   skiprows=[0], header = 0, names=['Reporter', 'Trade Value (US$)', 'Year'])

def createObject(x):
    options = []
    for i in x:
        options.append({
            'label': i,
            'value': i
        })
    return options

x_axis = merged_top_importers['Reporter'][0:topn].values
y_axis = merged_top_importers['Trade Value (US$)'][0:topn].values


app = dash.Dash()

app.layout = html.Div([

    dcc.Dropdown(
        id = 'first_dropdown',
        options = createObject(merged_top_importers.Year.unique()),
        placeholder='Select a Date'
    ),
    html.Div(id='output-graph')

    ])

@app.callback(
    Output(component_id='output-graph', component_property='children'),
    [Input(component_id='first_dropdown', component_property='options')]
    )

def update_output_div(input_value):
    return dcc.Graph(id = 'Bar_Plor',
                  figure = {
                      'data' : [
                          {'x':x_axis, 'y':y_axis, 'type':'bar', 'name':'First Chart'}
                          ]
                      })


if __name__ == '__main__':
    app.run_server(port=4050, debug=True)