'''

DPT Diagnostics Dashboard
Tony Du


Web Browser Dashboard for M&A DPT Diagnostics
Visualization and Reporting is generated on the fly
Use 'rundiagnostics.py' to generate input file



v1 Beta 4/26/20

Updates
- initial version
- Supported Diagnostics:
    - MMfile Summary (Generation, Load, Transmission)
    - Top Players
    - Phase3x4x by DM by Period
    - Supply Curve and MCP Sensitivity (partial WIP)



To-Do
- Add MCP and Wheeling rate Information to dashboard (already generated in input file)
- Fix Top Players Pie Chart to show combined non Top Players
- Add MCP and AEC vs Non-Eco distinction to Supply Curve
- Fix card resizing

'''






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
                                                children=[
                                                    dbc.Row(
                                                        children=[
                                                            dbc.Col(html.P(children='Utilities to include'), md = 1),
                                                            dbc.Col(
                                                                dbc.InputGroup(
                                                                    children=[
                                                                        dbc.Input(id='gen-input', type='number', min='1', max='20', value=5),
                                                                        dbc.InputGroupAddon(
                                                                            dbc.Button(id='gen-submit-btn', children='Update', color='primary'),
                                                                            addon_type='append'
                                                                        )
                                                                    ]
                                                                ), md=2
                                                            ),
                                                        ]
                                                    ),
                                                    dbc.Row(
                                                        dbc.Col(children=[dcc.Graph(id='gen-graph')], md=12)
                                                    )
                                                    #dcc.Graph(id='gen-graph')
                                                ], 
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
                                                children=[
                                                    dbc.Row(
                                                        children=[
                                                            dbc.Col(html.P(children='Top players to include'), md = 1),
                                                            dbc.Col(
                                                                dbc.InputGroup(
                                                                    children=[
                                                                        dbc.Input(id='hhi-input', type='number', min='1', max='20', value=10),
                                                                        dbc.InputGroupAddon(
                                                                            dbc.Button(id='hhi-submit-btn', children='Update', color='primary'),
                                                                            addon_type='append'
                                                                        )
                                                                    ]
                                                                ), md=2
                                                            ),
                                                        ],style = {'marginTop' : 10}
                                                    ),
                                                    dbc.Row(
                                                        children=[
                                                            dbc.Col(dcc.Graph(id='hhi-bar'), md=6),
                                                            dbc.Col(dcc.Graph(id='hhi-pie'), md=6)
                                                        ]

                                                    )
                                                ], 
                                                type='default',
                                            )
                                        ],
                                    ),
                                    dcc.Tab(
                                        label='Supply Curve',
                                        children=[
                                            dcc.Loading(
                                                id='loading-supply',
                                                children=[
                                                    dbc.Row(
                                                        children=[
                                                            dbc.Col(dcc.Dropdown(id='supply-owner-drop', clearable=False), md=4)
                                                        ]
                                                    ),
                                                    dbc.Row(
                                                        children=[
                                                            dbc.Col(dcc.Graph(id='supply-graph'))
                                                        ]

                                                    )
                                                ]
                                            )
                                        ], 
                                    ),
                                    dcc.Tab(
                                        label='Phase3X4X',
                                        children=[
                                            dcc.Loading(
                                                id='loading-phase',
                                                children=[
                                                    dbc.Row(
                                                        children=[
                                                            dbc.Col(dcc.Dropdown(id='phase-utility-drop', clearable=False), md=4)
                                                        ]
                                                    ),
                                                    dbc.Row(
                                                        children=[
                                                            dbc.Col(dcc.Graph(id='phase-graph'))
                                                        ]
                                                    )
                                                ]
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
                dbc.Col(dbc.Card(MMSUMMARY_PLOT), md=9),
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
    Output('period-drop', 'value'),
    Output('supply-owner-drop', 'options'),
    Output('phase-utility-drop', 'options'),
    Output('supply-owner-drop', 'value'),
    Output('phase-utility-drop', 'value')],
    [Input('store-df', 'children')]
)
def populate_dropdowns(jsonfile):
    if jsonfile == None:
        raise PreventUpdate
    else:
        dict_df = json.loads(jsonfile)
        df_baa = pd.read_json(dict_df['baa'], orient='split')
        lst_baa = df_baa['DM'].tolist()

        df_gen = pd.read_json(dict_df['gen'], orient='split')
        first_baa = lst_baa[0]
        first_period = lst_periods[0]
        lst_utilities = df_gen[(df_gen['CA'] == first_baa)&(df_gen['PERIOD'] == first_period)]['UTILITY'].unique().tolist()
        first_utility = lst_utilities[0]

        return [{'label':i, 'value':i} for i in lst_baa], [{'label':i, 'value':i} for i in lst_periods], first_baa, first_period,[
            {'label':i, 'value':i} for i in lst_utilities], [{'label':i, 'value':i} for i in lst_utilities], first_utility, first_utility
        

@app.callback(
    Output('gen-graph', 'figure'),
    [Input('baa-drop', 'value'),
    Input('period-drop', 'value'),
    Input('gen-submit-btn', 'n_clicks')],
    [State('store-df', 'children'),
    State('gen-input', 'value')] 
)    
def update_gen_graph(baa, period, n_clicks, jsonfile, num):
    if jsonfile == None:
        raise PreventUpdate
    dict_df = json.loads(jsonfile)
    df = pd.read_json(dict_df['gen'], orient='split')
    df_filter = df[df['CA'] == baa][df['PERIOD'] == period].sort_values(by='gen_MW', ascending=True)
    df_filter = df_filter.tail(num)
    fig = px.bar(df_filter, y='UTILITY', x='gen_MW', orientation = 'h')
    #fig.update_layout(height=450)
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
    [Output('hhi-bar', 'figure'),
    Output('hhi-pie', 'figure')],
    [Input('baa-drop', 'value'),
    Input('period-drop', 'value'),
    Input('hhi-submit-btn', 'n_clicks')],
    [State('hhi-input', 'value'),
    State('store-df', 'children')]
)
def update_hhi_graphs(baa, period, n_clicks, playernum, jsonfile):
    #TODO Update pie chart to group all others not in top10
    if baa == None:
        raise PreventUpdate
    dict_df = json.loads(jsonfile)
    df = pd.read_json(dict_df['hhi'], orient='split')
    df_filter = df[df['DM'] == baa][df['Period'] == period].sort_values(by='HHI', ascending = 'True')
    df_filter = df_filter.tail(playernum)

    fig_bar = px.bar(df_filter, y='Utility', x='HHI', orientation = 'h', title='Top Players - HHI', hover_data=['MW'])
    #fig_bar.update_layout(height=450)

    fig_pie = px.pie(df_filter, values='Share', names='Utility', title='Top Players - Market Share', hover_data=['MW'])
    return fig_bar, fig_pie

@app.callback(
    Output('phase-graph', 'figure'),
    [Input('baa-drop', 'value'),
    Input('period-drop', 'value'),
    Input('phase-utility-drop', 'value')],
    [State('store-df', 'children')]
)
def update_phase_graph(baa, period, utility, jsonfile):
    if utility == None:
        raise PreventUpdate
    dict_df = json.loads(jsonfile)
    df = pd.read_json(dict_df['phase'], orient='split')
    df_filter = df[(df['DM'] == baa) & (df['Period'] == period) & (df['Utility'] == utility)]
    fig = go.Figure(data=[
        go.Bar(name='3X Gen', x=df_filter['CA'] , y=df_filter['3X']),
        go.Bar(name='4X Gen', x=df_filter['CA'] , y=df_filter['4X'])
    ])
    fig.update_layout(barmode='group')
    return fig


@app.callback(
    Output('supply-graph', 'figure'),
    [Input('baa-drop', 'value'),
    Input('period-drop', 'value'),
    Input('supply-owner-drop', 'value')],
    [State('store-df', 'children')]
)

def update_supply_graph(baa, period, utility, jsonfile):
    if utility == None:
        raise PreventUpdate
    dict_df = json.loads(jsonfile)

    df_load = pd.read_json(dict_df['loads'], orient='split')
    df_load = df_load[(df_load['CA'] == baa) & (df_load['PERIOD'] == period) & (df_load['UTILITY'] == utility)]
    load_slice = df_load.loc[:,'LOAD']
    if len(load_slice) == 0:
        loadreq = 0
    else:
        loadreq = float(load_slice)

    df = pd.read_json(dict_df['supply'], orient='split')
    df_filter = df[(df['BAA'] == baa) & (df['Period'] == period) & (df['Owner'] == utility)].sort_values(by=['MC'])
    df_filter['cum_MW'] = df_filter['Capacity'].cumsum()

    fig = px.scatter(df_filter, x='cum_MW', y='MC', color ='Type', hover_name = 'Generator', hover_data=['Capacity'])
    fig.update_layout(shapes=[
        dict(
        type= 'line',
        yref= 'paper', y0= 0, y1= 1,
        xref= 'x', x0=loadreq, x1=loadreq
        )
    ])
    return fig



app.title = 'Diagnostics Dashboard'
app.layout = html.Div(children=[NAVBAR, BODY])
if __name__ == '__main__':
    app.run_server(host='127.0.0.1', port='8050', debug=True)