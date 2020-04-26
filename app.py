import pathlib
import os
import glob


import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

import pandas as pd
import numpy as np


# global vars
dir_diagnostics = 'C:/Users/tdu/python/python-diagnostics-dashboard/diagnostics/'
lst_baa = ['FG', 'DUK', 'ALGAMS']
lst_utilities = ['NextEra Energy Inc', 'Southern Co']
lst_periods = ['S_SP1', 'S_SP2', 'S_P', 'S_OP', 'W_SP', 'W_P', 'W_OP', 'H_SP', 'H_P', 'H_OP']





app = dash.Dash(__name__, external_stylesheets=[dbc.themes.YETI])
server = app.server  # for Heroku deployment


NAVBAR = dbc.Navbar(
    children=[
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(html.Img(src=app.get_asset_url('cra-logo.png'), height='30px')),
                    dbc.Col(
                        dbc.NavbarBrand('Apollo 11 - Diagnostics Dashboard', className='ml-2')
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
        html.H4(children='Inputs', className='display-5', style = {'fontSize': 36}),
        html.Hr(className='my-2'),
        html.Label('Select raw results folder', className='lead'),
        dcc.Dropdown(
            id='raw-drop', clearable=False, style = {'marginBottom': 10},
            options=[{'label':i, 'value':i} for i in os.listdir(dir_diagnostics)]
        ),
        dbc.Button('Import', id = 'import-btn', color = 'primary', className = 'mr-1', n_clicks = 0, disabled = True),
        html.Div(style = {'marginBottom':50}),

        html.Label('Select BAA', className='lead'),
        dcc.Dropdown(
            id ='baa-drop', clearable = False, style={'marginBottom': 50}, disabled = True
        ),
        html.Label('Select Period', className='lead'),
        dcc.Dropdown(
            id ='period-drop', clearable = False, style={'marginBottom': 50}, disabled = True,
            options = [{'label':i, 'value':i} for i in lst_periods]
        ),
        html.Label('Select Utility(s)', className = 'lead'),
        dcc.Dropdown(
            id = 'utility-drop', multi = True, disabled = True
        ),
    ], 
    #style = {'backgroundColor':'#add8e6'}
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
                                id='tabs',
                                children=[
                                    dcc.Tab(
                                        label='Generation',
                                        children=[
                                            dcc.Loading(
                                                id='loading-gen',
                                                children=[dcc.Graph(id='gen-graph')],
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
                                                id = 'loading-transmission',
                                                children = [dcc.Graph(id = 'transmission-graph')]
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

SC_PLOT = [
    dbc.CardHeader(html.H3('Supply Curve')),
    dbc.CardBody(
        dcc.Graph(id = 'supply-graph')
    )
]

TOP_PLOT = [
    dbc.CardHeader(html.H3('Top Players')),
    dbc.CardBody(
        dcc.Graph(id = 'topplayers-graph')
    )
]


BODY = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(LEFT_COLUMN, md=4, align='center'),
                dbc.Col(dbc.Card(MMSUMMARY_PLOT), md=8),
            ],
            style={'marginTop': 30},
        ),
        dbc.Row(
            [
                dbc.Col(dbc.Card(SC_PLOT), md = 6),
                dbc.Col(dbc.Card(TOP_PLOT), md = 6)
            ],
        )
    ],
    className='mt-12', fluid = True
)


@app.callback(
    Output('import-btn', 'disabled'),
    [Input('raw-drop', 'value')]
)
def enable_submitbtn(value):
    if value != None:
        return False
    else:
        return True

@app.callback(
    [Output('baa-drop', 'disabled'),
    Output('period-drop', 'disabled'),
    Output('utility-drop', 'disabled'),],
    [Input('import-btn', 'n_clicks')])

def enable_dropdowns(n_clicks):
    if n_clicks == 0:
        return True, True, True
    else:
        return False, False, False



app.layout = html.Div(children=[NAVBAR, BODY])
if __name__ == '__main__':
    app.run_server(host='127.0.0.1', port='8050', debug=True)