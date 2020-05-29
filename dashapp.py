import os
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

os.chdir('C:\\Users\\george\\Desktop\\GitHub\\Projects\\Comtrade_Network')

topn = 10

merged_top_importers = pd.read_csv('Merged_Top_Importers.csv',
                                   skiprows=[0], header = 0, names=['Reporter', 'TradeValue', 'Year'])

def YearToObject(x):
    options = []
    for i in x:
        options.append({
            'label': i,
            'value': i
        })
    return options


app = dash.Dash()

app.layout = html.Div([

	html.Br(),
    html.Br(),

    dcc.Dropdown(
        id = 'first_dropdown',
        options = YearToObject(merged_top_importers.Year.unique()),
        placeholder='Select a Year'
    ),


    html.Div(id='output-graph')

    ])

@app.callback(
    Output(component_id='output-graph', component_property='children'),
    [Input(component_id='first_dropdown', component_property='value')]
    )

def update_output_div(input_value):
    return dcc.Graph(id = 'Bar_Plor',
                  figure = {
                      'data' : [
                          {'x':merged_top_importers[merged_top_importers['Year']==input_value].Reporter, 'y':merged_top_importers[merged_top_importers['Year']==input_value].TradeValue, 'type':'bar', 'name':'First Chart'}
                          ],
                       'layout':{
                       	  'title':f'Total Trade Value of Imports of Vaccines for {input_value}',
                       	  'xaxis':{
                       	  		'title':'Country'
                       	  },
                       	  'yaxis':{
                       	  		'title':'Trade Value in USD ($)'
                       	  }
                       }
                      })


if __name__ == '__main__':
    app.run_server(port=4050, debug=True)