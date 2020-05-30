import os
import pandas as pd
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# https://dash.plotly.com/layout

os.chdir('C:\\Users\\george\\Desktop\\GitHub\\Projects\\Comtrade_Network')

df = pd.read_csv('Merged_Top_Importers.csv',
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
    # Adding a header
	html.H1(children='Global Trade Network of Human Vaccines', 
		    style={
		    		'textAlign': 'center'}
		    ),

	html.Br(),

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
                          {'x':df[df['Year']==input_value].Reporter, 'y':df[df['Year']==input_value].TradeValue, 'type':'bar', 'name':'First Chart'}
                          ],
                       'layout':{
                       	  'title':f'Trade Value of Vaccines for {input_value} (Imports)',
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