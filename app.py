import pathlib
import os


import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc


import pandas as pd
import numpy as np


# global vars
raw_results_dir = 'C:/Users/tdu/python/Raw results/'
lst_baa = ['FG', 'DUK', 'ALGAMS']
lst_utilities = ['NextEra Energy Inc', 'Southern Co']

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
            id='raw-drop', clearable=False, style = {'marginBottom': 10}
        ),
        dbc.Button('Import', id = 'raw-btn', color = 'primary', className = 'mr-1', n_clicks=0),
        html.Div(style = {'marginBottom':50}),
        html.Label('Select BAA', className='lead'),
        dcc.Dropdown(
            id ='baa-drop', clearable = False, style={'marginBottom': 50}, disabled = True
        ),
        html.Label('Select Period', className='lead'),
        dcc.Dropdown(
            id ='period-drop', clearable = False, style={'marginBottom': 50}, disabled = True
        ),
        html.Label('Select Utility(s)', className = 'lead'),
        dcc.Dropdown(
            id = 'utility-drop', multi = True, disabled = True
        ),
    ], 
    #style = {'backgroundColor':'#add8e6'}
)


#unused tab example
TAB_EXAMPLE = [
    dbc.CardHeader(html.H5('Most frequently used words in complaints')),
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
                                        label='Supply Curve',
                                        children=[
                                            dcc.Loading(
                                                id='loading-treemap',
                                                children=[dcc.Graph(id='bank-treemap')],
                                                type='default',
                                            )
                                        ],
                                    ),
                                    dcc.Tab(
                                        label='Top Players',
                                        children=[
                                            dcc.Loading(
                                                id='loading-wordcloud',
                                                children=[
                                                    dcc.Graph(id='bank-wordcloud')
                                                ],
                                                type='default',
                                            )
                                        ],
                                    ),
                                ],
                            )
                        ],
                        md=8,
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

PHASE_PLOT = [
    dbc.CardHeader(html.H3('Phase3X4X By DM By Period')),
    dbc.CardBody(
        [
            dcc.Loading(
                id='loading-banks-hist',
                children=[
                    dbc.Alert(
                        'Not enough data to render this plot, please adjust the filters',
                        id='no-data-alert-bank',
                        color='warning',
                        style={'display': 'none'},
                    ),
                    dcc.Graph(id='bank-sample'),
                ],
                type='default',
            )
        ],
        style={'marginTop': 0, 'marginBottom': 0},
    ),
]


BODY = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(LEFT_COLUMN, md=4, align='center'),
                dbc.Col(dbc.Card(PHASE_PLOT), md=8),
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



app.layout = html.Div(children=[NAVBAR, BODY])
if __name__ == '__main__':
    app.run_server(host='127.0.0.1', port='8050', debug=True)