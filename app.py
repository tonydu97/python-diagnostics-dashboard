import pathlib
import os
import glob


import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import pandas as pd
import numpy as np
import json
import plotly.graph_objects as go
import plotly.express as px




# global vars
dir_absolute = 'C:/Users/tdu/python/python-diagnostics-dashboard/diagnostics/'
dirname = os.path.dirname(__file__)
path_d = os.path.join(dirname, 'diagnostics/')
#lst_rel = [f for f in os.listdir(relative_path) if f.endswith('.xlsx')]
#lst_rel = os.listdir(relative_path)
lst_baa = ['FG', 'DUK', 'ALGAMS']
lst_utilities = ['NextEra Energy Inc', 'Southern Co']
lst_periods = ['S_SP1', 'S_SP2', 'S_P', 'S_OP', 'W_SP', 'W_P', 'W_OP', 'H_SP', 'H_P', 'H_OP']





app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server  # for Heroku deployment


NAVBAR = dbc.Navbar(
    children=[
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(html.Img(src=app.get_asset_url('cra-logo.png'), height='30px')),
                    dbc.Col(
                        dbc.NavbarBrand('DPT Diagnostics Dashboard - Beta', className='ml-2')
                    ),
                ],
                align='center',
                no_gutters=True,
            ),
        )
    ],
    color='light',
    #dark=True,
    sticky='top',
)

LEFT_COLUMN = dbc.Jumbotron(
    [
        dcc.Loading(
            id = 'loading-inputs',
            children = [
                html.Div(id='store-df', style={'display' : 'none'}),
                dbc.Container(
                    [
                        html.H4(children='Inputs', className='display-5', style = {'fontSize': 36}),
                        html.Hr(className='my-2'),
                        html.Label('Select diagnostics file', className='lead'),
                        dcc.Dropdown(
                            id='file-drop', clearable=False, style = {'marginBottom': 10, 'fontSize': 14},
                            #options=[{'label':i, 'value':i} for i in os.listdir(dir_diagnostics)]
                            options=[{'label':i, 'value':i} for i in [f for f in os.listdir(path_d) if f.endswith('.xlsx')]]
                        ),
                        dbc.Button('Import', id = 'import-btn', color = 'primary', className = 'mr-1', n_clicks = 0, disabled = True),
                        html.Div(style = {'marginBottom':25}),
                        html.Label('Select BAA', className='lead'),
                        dcc.Dropdown(
                            id ='baa-drop', clearable = False, style={'marginBottom': 25}, disabled = True
                        ),
                        html.Label('Select Period', className='lead'),
                        dcc.Dropdown(
                            id ='period-drop', clearable = False, style={'marginBottom': 0}, disabled = True,
                            options = [{'label':i, 'value':i} for i in lst_periods]
                        )
                    ], fluid = True
                )
            ]

        )
    ],fluid = True
)


MMSUMMARY_PLOT = [
    dbc.CardHeader(html.H5('Mmfile Summary')),
    dbc.CardBody(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dcc.Tabs(
                                id='top-tabs',
                                children=[
                                    dcc.Tab(
                                        label='Generation',
                                        children=[
                                            dcc.Loading(
                                                id='loading-gen',
                                                children=[dcc.Graph(id='gen-graph')], #graph fixed size set in callback function on figure
                                                type='default',
                                            )
                                        ],
                                    ),
                                    dcc.Tab(
                                        label='Load',
                                        children=[
                                            dcc.Loading(
                                                id='loading-load',
                                                children=[dcc.Graph(id='load-graph')],
                                                type='default',
                                            )
                                        ],
                                    ),
                                    dcc.Tab(
                                        label='Transmission',
                                        children=[
                                            dcc.Loading(
                                                id ='loading-transmission',
                                                children = [dcc.Graph(id='tx-graph')],
                                                type = 'default',
                                            )
                                        ],
                                    ),
                                ],
                            )
                        ],
                        #md=12,
                    ),
                ]
            )
        ]
    ),
]


BOTTOM_PLOTS = [
    dbc.CardHeader(html.H5('Additional Diagnostics')),
    dbc.CardBody(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dcc.Tabs(
                                id='bottom-tabs',
                                children=[
                                    dcc.Tab(
                                        label='Top Players',
                                        children=[
                                            dcc.Loading(
                                                id='loading-hhi',
                                                children=[dcc.Graph(id='hhi-graph')], 
                                                type='default',
                                            )
                                        ],
                                    ),
                                    dcc.Tab(
                                        label='Supply Curve',
                                        children=[
                                            dcc.Loading(
                                                id='loading-supply',
                                                children=[dcc.Graph(id='supply-graph')],
                                                type='default',
                                            )
                                        ],
                                    ),
                                    dcc.Tab(
                                        label='Phase3X4X',
                                        children=[
                                            dcc.Loading(
                                                id ='loading-phase',
                                                children = [dcc.Graph(id='phase-graph')],
                                                type = 'default',
                                            )
                                        ],
                                    ),
                                ],
                            )
                        ],
                    ),
                ]
            )
        ]
    ),
]


BODY = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(LEFT_COLUMN, md=3, align='center'),
                dbc.Col(dbc.Card(MMSUMMARY_PLOT)),
            ],
            style={'marginTop': 30},
        ),
        dbc.Row(
            [
                dbc.Col(dbc.Card(BOTTOM_PLOTS))
            ],
            style={'marginTop': 30},
        ),
    ],
    className='mt-12', fluid = True
)


@app.callback(
    Output('import-btn', 'disabled'),
    [Input('file-drop', 'value')]
)
def enable_submitbtn(value):
    if value != None:
        return False
    else:
        raise PreventUpdate

@app.callback(
    [Output('baa-drop', 'disabled'),
    Output('period-drop', 'disabled')],
    [Input('import-btn', 'n_clicks')]
)

def enable_dropdowns(n_clicks):
    if n_clicks == 0:
        raise PreventUpdate
    else:
        return False, False

@app.callback(
    Output('store-df', 'children'),
    [Input('import-btn', 'n_clicks')],
    [State('file-drop', 'value')]
)

def load_df(n_clicks, file):
    if n_clicks == 0:
        raise PreventUpdate
    else:
        dict_df = pd.read_excel(path_d + file, sheet_name=None)
        dict_out = {}
        for key in dict_df:
            dict_out[key] = dict_df[key].to_json(orient='split')
        return json.dumps(dict_out)
 

@app.callback(
    [Output('baa-drop', 'options'),
    Output('period-drop', 'options'),
    Output('baa-drop', 'value'),
    Output('period-drop', 'value')],
    [Input('store-df', 'children')]
)

def populate_dropdowns(jsonfile):
    if jsonfile == None:
        raise PreventUpdate
    else:
        dict_df = json.loads(jsonfile)
        df_baa = pd.read_json(dict_df['baa'], orient='split')
        lst_baa = df_baa['DM'].tolist()
        return [{'label':i, 'value':i} for i in lst_baa], [{'label':i, 'value':i} for i in lst_periods], lst_baa[0], lst_periods[0]

@app.callback(
    Output('gen-graph', 'figure'),
    [Input('baa-drop', 'value'),
    Input('period-drop', 'value')],
    [State('store-df', 'children')] 
)    

def update_gen_graph(baa, period, jsonfile):
    dict_df = json.loads(jsonfile)
    df = pd.read_json(dict_df['gen'], orient='split')
    df_filter = df[df['CA'] == baa][df['PERIOD'] == period].sort_values(by='gen_MW', ascending=True)
    fig = px.bar(df_filter, y='UTILITY', x='gen_MW', orientation = 'h')
    fig.update_layout(height=450)
    return fig

@app.callback(
    Output('load-graph', 'figure'),
    [Input('baa-drop', 'value'),
    Input('period-drop', 'value')],
    [State('store-df', 'children')] 
)    

def update_load_graph(baa, period, jsonfile):
    dict_df = json.loads(jsonfile)
    df = pd.read_json(dict_df['loads'], orient='split')
    df_filter = df[df['CA'] == baa][df['PERIOD'] == period].sort_values(by='LOAD', ascending=True)
    fig = px.bar(df_filter, y='UTILITY', x='LOAD', orientation = 'h')
    fig.update_layout(height=450)
    return fig

@app.callback(
    Output('tx-graph', 'figure'),
    [Input('baa-drop', 'value'),
    Input('period-drop', 'value')],
    [State('store-df', 'children')] 
)    

def update_tx_graph(baa, period, jsonfile):
    dict_df = json.loads(jsonfile)
    df = pd.read_json(dict_df['tx'], orient='split')
    df_filter = df[(df['To_CA'] == baa) | (df['From_CA'] == baa)][df['PERIOD'] == period].sort_values(by='To_CA', ascending=True)
    unique = pd.unique(df_filter[['To_CA', 'From_CA']].values.ravel('K')).tolist()
    unique.remove(baa)

    df_graph = pd.DataFrame(index=unique)
    df_from = df_filter[df_filter['From_CA'] != baa].set_index(['From_CA'])
    df_to = df_filter[df_filter['To_CA'] != baa].set_index(['To_CA'])
    df_graph['To_CA'] = df_to['tx_line_MW']
    df_graph['From_CA'] = df_from['tx_line_MW']    

    fig = go.Figure(data=[
        go.Bar(name='To_CA', x=df_graph.index , y=df_graph['To_CA']),
        go.Bar(name='From_CA', x=df_graph.index , y=df_graph['From_CA'])
    ])
    fig.update_layout(barmode='group')
    return fig


@app.callback(
    Output('hhi-graph', 'figure'),
    [Input('baa-drop', 'value'),
    Input('period-drop', 'value')],
    [State('store-df', 'children')]
)

def update_hhi_graph(baa, period, jsonfile):
    dict_df = json.loads(jsonfile)
    df = pd.read_json(dict_df['hhi'], orient='split')
    df_filter = df[df['DM'] == baa][df['Period'] == period].sort_values(by='HHI', ascending = 'True')
    df_filter = df_filter.tail(10)
    fig = px.bar(df_filter, y='Utility', x='HHI', orientation = 'h')
    fig.update_layout(height=450)
    return fig



app.layout = html.Div(children=[NAVBAR, BODY])
if __name__ == '__main__':
    app.run_server(host='127.0.0.1', port='8050', debug=True)