'''

DPT Diagnostics Dashboard
Tony Du


Web Browser Dashboard for M&A DPT Diagnostics
Visualization and Reporting is generated on the fly
Use 'rundiagnostics.py' to generate input file


v3 Beta 6/8/20

Updates
- Show Net GEneration for players without load
- Wheeling Rates table updates
- MCP line for Supply Curve
- Download 3x4x all periods button in phase tab

To-Do
- Fix Card/Tab resizing
- Refactoring for caching dataframes 


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
import dptlib as dpt


# global vars
dirname = os.path.dirname(__file__)
path_d = os.path.join(dirname, 'output/')
lst_periods = ['S_SP1', 'S_SP2', 'S_P', 'S_OP', 'W_SP', 'W_P', 'W_OP', 'H_SP', 'H_P', 'H_OP']

#raw_results_dir = 'X:/DC/Project/Energy&Environ/EMacan26602.00-Project Alice/Analysis - Jagali/Results/Raw results'
raw_results_dir = 'C:/Users/tdu/python/Raw results'
lst_runs = [d for d in os.listdir(raw_results_dir) if os.path.isdir(os.path.join(raw_results_dir, d))]
lst_runs.sort(reverse = True)
try:
    lst_runs.remove('~old')
except:
    pass

# downloadable diagnostics
lst_diagnostics = ['Dashboard Input File','Phase 3X & 4X Processor']




app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server  # for Heroku deployment


NAVBAR = dbc.Navbar(
    [
        html.Img(src=app.get_asset_url('branding.png'), height='40px'),
        dbc.Nav(
            [
                dbc.NavItem(dbc.NavLink('DPT Dashboard', href='/dashboard', id='dashboard-link', active=True)),
                dbc.NavItem(dbc.NavLink('Diagnostics Library - Generate XLSX', id='download-link', href='/download'))
            ], navbar=True, style={'marginLeft': '20px'}
        )

    ],
    color='dark',
    dark=True,
)

LEFT_COLUMN = dbc.Jumbotron(
    [
        dcc.Loading(
            id = 'loading-inputs',
            children = [
                html.Div(id='store-df', style={'display' : 'none'}),
                html.Div(id='store-mcp', style={'display' : 'none'}),
                dbc.Container(
                    [
                        html.H4(children='Inputs', className='display-5', style = {'fontSize': 36}),
                        html.Hr(className='my-2'),
                        html.Label('Select diagnostics file', className='lead'),
                        dcc.Dropdown(
                            id='file-drop', clearable=False, style = {'marginBottom': 10, 'fontSize': 14},
                            options=[{'label':i, 'value':i} for i in [f for f in os.listdir(path_d) if f.startswith('d_')]]
                        ),
                        dbc.Button('Import', id = 'import-btn', color = 'primary', className = 'mr-1', n_clicks = 0, disabled = True),
                        html.Div(style = {'marginBottom':25}),
                        html.Label('Select Destination Market', className='lead'),
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
    ],fluid = True#, style={'height':'100%'}
)


DPTSUMMARY_PLOT = [
    dbc.CardHeader(html.H5('DPT input file summary')),
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
                                                            dbc.Col(html.P(children='Utilities to include'), width=1),
                                                            dbc.Col(
                                                                dbc.InputGroup(
                                                                    children=[
                                                                        dbc.Input(id='gen-input', type='number', min='1', max='20', value=5),
                                                                        dbc.InputGroupAddon(
                                                                            dbc.Button(id='gen-submit-btn', children='Update', color='primary'),
                                                                            addon_type='append'
                                                                        )
                                                                    ]
                                                                ), width=2
                                                            ),
                                                        ], style={'marginTop': 10}
                                                    ),
                                                    dbc.Row(
                                                        dbc.Col(children=[dcc.Graph(id='gen-graph')], width=12)
                                                    )
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
                                        label='Transmission (From CA)',
                                        children=[
                                            dcc.Loading(
                                                id ='loading-transmission',
                                                children = [
                                                    dbc.Row(dbc.Col(html.H5('SIL:', id='sil')), style={'marginTop': 10}),
                                                    dbc.Row(dbc.Col(dcc.Graph(id='tx-graph'), width=12)),
                                                    
                                                    ],
                                                type = 'default',
                                            )
                                        ],
                                    ),
                                    dcc.Tab(
                                        label='MCP and Wheeling Rates',
                                        children=[
                                            dcc.Loading(
                                                id='loading-MCP-Wheel',
                                                children=[
                                                    dbc.Row(
                                                        children=[
                                                            dbc.Col(html.H5('MCPs')),
                                                            dbc.Col(html.H5('Wheeling Rates'))
                                                        ], style={'marginTop': 10}
                                                    ),
                                                    dbc.Row(
                                                        children=[
                                                            dbc.Col(id='mcp-table'),
                                                            dbc.Col(id='wheeling-table')
                                                        ]
                                                    )
                                                ]
                                            )
                                        ]
                                    )
                                ],
                            )
                        ],
                        #width=12,
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
                                        label='Top Player (HHI by Utility)',
                                        children=[
                                            dcc.Loading(
                                                id='loading-hhi',
                                                children=[
                                                    dbc.Row(
                                                        children=[
                                                            dbc.Col(html.P(children='Top players to include'), width=1),
                                                            dbc.Col(
                                                                dbc.InputGroup(
                                                                    children=[
                                                                        dbc.Input(id='hhi-input', type='number', min='1', max='20', value=10),
                                                                        dbc.InputGroupAddon(
                                                                            dbc.Button(id='hhi-submit-btn', children='Update', color='primary'),
                                                                            addon_type='append'
                                                                        )
                                                                    ]
                                                                ), width=2
                                                            ),
                                                        ],style = {'marginTop' : 10}
                                                    ),
                                                    dbc.Row(
                                                        children=[
                                                            dbc.Col(dcc.Graph(id='hhi-bar'), width=6),
                                                            dbc.Col(dcc.Graph(id='hhi-pie'), width=6)
                                                        ]

                                                    )
                                                ], 
                                                type='default',
                                            )
                                        ],
                                    ),
                                    dcc.Tab(
                                        label='Supply Curve (DPT input file)',
                                        children=[
                                            dcc.Loading(
                                                id='loading-supply',
                                                children=[
                                                    dbc.Row(
                                                        children=[
                                                            dbc.Col(dcc.Dropdown(id='supply-owner-drop', clearable=False), width=4)
                                                        ]
                                                    ),
                                                    dbc.Row(
                                                        children=[
                                                            dbc.Col(dcc.Graph(id='supply-graph'))
                                                        ]
                                                    ),
                                                    dbc.Row(
                                                        children=[
                                                            dbc.Col(html.H5('Marginal Unit')),
                                                            dbc.Col(html.H5('Economic Units')),
                                                            dbc.Col(html.H5('Uneconomic Units'))                                                            
                                                        ]
                                                    ),
                                                    dbc.Row(
                                                        children=[
                                                            dbc.Col(id='marginal-table'),
                                                            dbc.Col(id='eco-table'),
                                                            dbc.Col(id='uneco-table')
                                                        ]
                                                    )
                                                ]
                                            )
                                        ], 
                                    ),
                                    dcc.Tab(
                                        label='Phase3X4X (3x - Round 1 and 4x)',
                                        children=[
                                            dcc.Loading(
                                                id='loading-phase',
                                                children=[
                                                    dbc.Button('Download for all periods - Requires Imported Diagnostic File', id='phase-modal-btn', color='primary'),
                                                    dbc.Modal(
                                                        [
                                                            dbc.ModalHeader('Generate Phase3X4X by Owner by DM by Period'),
                                                            dbc.ModalBody(id='phase-modal-body')
                                                        ], id='phase-modal', size='lg'

                                                    ),
                                                    dbc.Row(
                                                        children=[
                                                            dbc.Col(
                                                                dash_table.DataTable(
                                                                    id='phase-datatable',
                                                                    editable=True,
                                                                    filter_action='native',
                                                                    sort_action='native',
                                                                    sort_mode='multi',
                                                                    page_action='none',
                                                                    style_cell={'width': '20%'},
                                                                    fixed_rows={'headers':True},
                                                                    style_table={'height': '500px', 'overflowY': 'auto'}
                                                                )
                                                            )
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
                dbc.Col(LEFT_COLUMN, width=3, align='center'),
                dbc.Col(dbc.Card(DPTSUMMARY_PLOT), width=9),
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

DOWNLOAD = dbc.Container(
    [
        dbc.Jumbotron(
            [
                html.H2('Select Input Folder and Diagnostic'),
                html.Div(style = {'marginBottom':'10px'}),
                html.Label('Raw Results Folder'),
                dcc.Dropdown(id='dl-case-dropdown', options=[{'label':i, 'value':i} for i in lst_runs], clearable=False, style = {'marginBottom': '20px'}),
                html.Label('Diagnostic to Generate'),
                dcc.Dropdown(id='dl-diagnostic-dropdown', options = [{'label':i, 'value':i} for i in lst_diagnostics], clearable=False, style = {'marginBottom': '20px'}),
                html.Label('Output Directory'),
                html.Div(style = {'marginBottom':'10px'}),
                dcc.Input(id='dl-output-textbox', value=dirname+'\\output\\', size = '125'),
                html.Hr(),
                html.H2('Diagnostic-specific Inputs'),
                dcc.Loading(html.Div(id='dl-diagnostic-inputs'))
            ], style={'marginTop': 30}
        )
    ]
)

@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname in ['/', '/dashboard']:
        return [NAVBAR, BODY]
    elif pathname == '/download':
        return [NAVBAR, DOWNLOAD]
    return dbc.Jumbotron(
        [
            html.H1('404: Not found', className='text-danger'),
            html.Hr(),
            html.P(f'The pathname {pathname} is invalid'),
        ]
    )

@app.callback(
    [Output('dashboard-link', 'active'),
    Output('download-link', 'active')],
    [Input('url', 'pathname')]
)
def update_active_link(pathname):
    if pathname in ['/', '/dashboard']:
        return True, False
    elif pathname == '/download':
        return False, True
    return False, False

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
        first_baa = lst_baa[0]
        first_period = lst_periods[0]

        return [{'label':i, 'value':i} for i in lst_baa], [{'label':i, 'value':i} for i in lst_periods], first_baa, first_period

@app.callback(
    [Output('supply-owner-drop', 'value'),
    Output('supply-owner-drop', 'options')],
    [Input('baa-drop', 'value'),
    Input('period-drop', 'value')],
    [State('store-df', 'children')]
)

def populate_owner_dropdown(baa, period, jsonfile):
    # if baa == None | period == None:
    #     raise PreventUpdate
    dict_df = json.loads(jsonfile)
    df = pd.read_json(dict_df['supply'], orient='split')
    df = df[(df['BAA'] == baa) & (df['Period'] == period)]
    lst_owners = df['Owner'].unique().tolist()
    return lst_owners[0], [{'label':i, 'value':i} for i in lst_owners]

@app.callback(
    [Output('mcp-table', 'children'),
    Output('wheeling-table', 'children')],
    #Output('store-mcp', 'children')],
    [Input('baa-drop', 'value')],
    [State('store-df','children'),
    State('file-drop', 'value')]
)

def update_mcp_wheeling_tables(baa, jsonfile, excelfilename):
    dict_df = json.loads(jsonfile)
    df_mcp = pd.read_json(dict_df['mcp'], orient='split')
    df_mcp = df_mcp[(df_mcp['CA'] == baa)]
    df_mcp = df_mcp[['PERIOD', 'MCP']]
    if excelfilename.find('plus') != -1:
        df_mcp['MCP'] *= 1.1
    if excelfilename.find('minus') != -1:
        df_mcp['MCP'] *= 0.9
    df_mcp['MCP'] = df_mcp['MCP'].round(2)
    mcp_table = dbc.Table.from_dataframe(df_mcp, bordered=True, hover=True)

    df_wheel = pd.read_json(dict_df['wheel'], orient='split')
    wheel_to = df_wheel[(df_wheel['To_CA'] == baa)]
    wheel_to = wheel_to[['To_CA', 'On-Peak', 'Off-Peak']].iloc[[0]]
    wheel_from = df_wheel[(df_wheel['From_CA'] == baa)]
    wheel_from = wheel_from[['To_CA', 'On-Peak', 'Off-Peak']]
    wheel_to_table = dbc.Table.from_dataframe(wheel_to, bordered=True, hover=True)
    wheel_from_table = dbc.Table.from_dataframe(wheel_from, bordered=True, hover=True)
    return [mcp_table], [html.Div(children=[wheel_to_table, wheel_from_table])]


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
    df_gen = df[df['CA'] == baa][df['PERIOD'] == period].sort_values(by='gen_MW', ascending=True)
    df_gen = df_gen.tail(num).set_index('UTILITY')

    df_load = pd.read_json(dict_df['loads'], orient='split')
    df_load = df_load[df_load['CA'] == baa][df_load['PERIOD'] == period].set_index('UTILITY')

    df_gen['LOAD'] = df_load['LOAD']
    df_gen = df_gen.fillna(0)
    df_gen['net_gen'] = df_gen['gen_MW'] - df_gen['LOAD']

    


    fig = go.Figure(data=[
        go.Bar(name='Net Generation', y=df_gen.index , x=df_gen['net_gen'], orientation='h'),
        go.Bar(name='Generation', y=df_gen.index , x=df_gen['gen_MW'], orientation='h')
    ])
    fig.update_layout(barmode='group')
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
    [Output('tx-graph', 'figure'),
    Output('sil', 'children')],
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
    tx_sil = df_graph['From_CA'].sum()

    df_graph['From_CA_perc'] = df_graph['From_CA'] / tx_sil
        

    fig = go.Figure(data=[
        go.Bar(name='From CA', x=df_graph.index , y=df_graph['From_CA_perc'])
    ])
    fig.layout.yaxis.tickformat = ',.0%'  
    return fig, 'SIL (MW): ' + str(tx_sil)


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
    if baa == None:
        raise PreventUpdate
    dict_df = json.loads(jsonfile)
    df = pd.read_json(dict_df['hhi'], orient='split')
    df_filter = df[df['DM'] == baa][df['Period'] == period].sort_values(by='HHI', ascending = False)
    #df_filter = df_filter.tail(playernum)

    df_top = df_filter.sort_values(by='HHI', ascending = False).iloc[:playernum] 
    df_others = df_filter.sort_values(by='HHI', ascending = False).iloc[playernum:]
    df_others.loc['Total'] = df_others.sum(numeric_only = True, axis = 0)
    df_others.loc['Total', 'Utility'] = 'Other'
    df_top = df_top.sort_values(by='HHI', ascending = True)
    df_pie = df_top.append(df_others.loc['Total'])


    fig_bar = px.bar(df_top, y='Utility', x='HHI', orientation = 'h', title='Top Players - HHI', hover_data=['MW'])


    

    fig_pie = px.pie(df_pie, values='Share', names='Utility', title='Top Players - Market Share', hover_data=['MW'])
    return fig_bar, fig_pie


@app.callback(
    [Output('supply-graph', 'figure'),
    Output('marginal-table', 'children'),
    Output('eco-table', 'children'),
    Output('uneco-table', 'children')],
    [Input('baa-drop', 'value'),
    Input('period-drop', 'value'),
    Input('supply-owner-drop', 'value')],
    [State('store-df','children'),
    State('file-drop', 'value')]
)
def update_supply_tab(baa, period, utility, jsonfile, excelfilename):
    if (utility == None):
        raise PreventUpdate

    dict_df = json.loads(jsonfile)
 
    df_load = pd.read_json(dict_df['loads'], orient='split')
    df_load = df_load[(df_load['CA'] == baa) & (df_load['PERIOD'] == period) & (df_load['UTILITY'] == utility)]
    load_slice = df_load.loc[:,'LOAD']
    if len(load_slice) == 0:
        loadreq = 0
    else:
        loadreq = float(load_slice)

    df_supply = pd.read_json(dict_df['supply'], orient='split')
    df_filter = df_supply[(df_supply['BAA'] == baa) & (df_supply['Period'] == period) & (df_supply['Owner'] == utility)].sort_values(by=['MC'])
    df_filter['MC'] = df_filter['MC'].round(2)
    df_filter['cum_MW'] = df_filter['Capacity'].cumsum()

    
    df_mcp = pd.read_json(dict_df['mcp'], orient='split')
    df_mcp = df_mcp[(df_mcp['CA'] == baa) & (df_mcp['PERIOD'] == period)]
    df_mcp = df_mcp[['PERIOD', 'MCP']]
    if excelfilename.find('plus') != -1:
        df_mcp['MCP'] *= 1.1
    if excelfilename.find('minus') != -1:
        df_mcp['MCP'] *= 0.9
    df_mcp['MCP'] = df_mcp['MCP'].round(2)

    mcpval = df_mcp.iat[0, 1]
    df_loadserved = df_filter[df_filter['cum_MW'] > loadreq]
    df_loadserved = df_loadserved[['Generator', 'Capacity', 'MC']]

    # marginal unit - first unit where MC > MCP
    df_eco = df_loadserved[df_loadserved['MC'] <= mcpval]

    if len(df_eco) > 1:
        df_marginal = df_eco.iloc[0:1]
        marginal_table = dbc.Table.from_dataframe(df_marginal, bordered=True, hover=True)
        # economic units - units where MC > MCP excluding marginal unit
        df_eco = df_eco[1:]
        eco_table = dbc.Table.from_dataframe(df_eco, bordered=True, hover=True)
    elif len(df_eco) == 1:
        df_marginal = df_eco[0:1]
        marginal_table = dbc.Table.from_dataframe(df_marginal, bordered=True, hover=True)
        eco_table = html.H5('N/A')
    else:
        marginal_table = html.H5('N/A')
        eco_table = html.H5('N/A')

    #uneconomic units - units where MC <= MCP
    df_uneco = df_loadserved[df_loadserved['MC'] > mcpval]

    if len(df_uneco) != 0:
        uneco_table = dbc.Table.from_dataframe(df_uneco, bordered=True, hover=True)
    else:
        uneco_table = html.H5('N/A')

    # generate supply curve 
    fig = px.scatter(df_filter, x='cum_MW', y='MC', color ='Type', hover_name = 'Generator', hover_data=['Capacity'])
    fig.update_layout(shapes=[
        dict(
        type= 'line',
        yref= 'paper', y0= 0, y1= 1,
        xref= 'x', x0=loadreq, x1=loadreq
        ),
        dict(
        type= 'line',
        y0=mcpval*1.05, y1=mcpval*1.05,
        x0=0, x1=df_filter['cum_MW'].max()  
        )
    ])
    fig.update_xaxes(rangemode="tozero")
    fig.update_yaxes(rangemode="tozero")
    



    return fig, [marginal_table], [eco_table], [uneco_table]

@app.callback(
    [Output('phase-datatable', 'columns'),
    Output('phase-datatable', 'data')],
    [Input('baa-drop', 'value'),
    Input('period-drop', 'value')],
    [State('store-df', 'children')]
)
def update_phase_table(baa, period, jsonfile):
    dict_df = json.loads(jsonfile)
    df = pd.read_json(dict_df['phase'], orient='split')
    df_filter = df[(df['DM'] == baa) & (df['Period'] == period)]
    df_filter = df_filter[['Utility', 'CA', '3X', '4X']]
    columns = [{"name": i, "id": i, "deletable": True, "selectable": True} for i in df_filter.columns]
    data = df_filter.to_dict('records')
    return columns, data

@app.callback(
    [Output('phase-modal', 'is_open'),
    Output('phase-modal-body', 'children')],
    [Input('phase-modal-btn', 'n_clicks')],
    [State('phase-modal', 'is_open'),
    State('baa-drop', 'value'),
    State('store-df', 'children')]
)

def open_phase_modal(n_clicks, is_open, currentbaa, jsonfile):

    # Read in options from diagnostics file
    if jsonfile == None:
        raise PreventUpdate
    dict_df = json.loads(jsonfile)
    df = pd.read_json(dict_df['phase'], orient='split')
    lst_dm = df['DM'].unique().tolist()
    lst_utility = df['Utility'].unique().tolist()

    # Generate modal body

    body = html.Div(
        [
            html.Label('Utility - can select multiple'),
            dcc.Dropdown(
                id='phase-modal-utility-drop', multi=True, style={'marginBottom': 20},
                options=[{'label':i, 'value':i} for i in lst_utility]),
            html.Label('DM - can select multiple'),
            dcc.Dropdown(
                id='phase-modal-dm-drop', multi=True, style={'marginBottom': 20},
                value = currentbaa, options=[{'label':i, 'value':i} for i in lst_dm]),
            dcc.Input(id='phase-modal-textbox', value=dirname+'\\output\\', size = '100', style={'marginBottom': 20}),
            dbc.Button('Download', id='phase-modal-download-btn', color='primary', n_clicks=0),
            dbc.Toast(
                [html.P('File Saved and Exported')],
                id='phase-modal-toast',
                header='Done',
                is_open=False,
                dismissable=True,)
        ]
    )

    # Open/Close Modal and return

    if n_clicks:
        return not is_open, body
    return is_open, body


@app.callback(
    Output('phase-modal-toast', 'is_open'),
    [Input('phase-modal-download-btn', 'n_clicks')],
    [State('phase-modal-utility-drop', 'value'),
    State('phase-modal-dm-drop', 'value'),
    State('phase-modal-textbox', 'value'),
    State('file-drop', 'value'),
    State('store-df', 'children')]
)
def download_phase_modal(n_clicks, utility_lst, dm_lst, outputfolder, case, jsonfile):
    # Read in diagnostics file
    if (jsonfile == None) | (n_clicks == 0):
        raise PreventUpdate
    if type(dm_lst) is str:
        lst_dm = [dm_lst]
    else:
        lst_dm = dm_lst
    if type(utility_lst) is str:
        lst_utility = [utility_lst]
    else:
        lst_utility = utility_lst
    dict_df = json.loads(jsonfile)
    df = pd.read_json(dict_df['phase'], orient='split')
    dpt.phase3x4x_bydmbyperiod(case, df, outputfolder, lst_dm, lst_utility, lst_periods)
    return True



@app.callback( #necessary callback in order to filter
    Output('phase-datatable', 'style_data_conditional'),
    [Input('phase-datatable', 'selected_columns')]
)
def update_table_styles(selected_columns):
    if selected_columns == None:
        raise PreventUpdate
    return [{
        'if': { 'column_id': i },
        'background_color': '#D2F3FF'
    } for i in selected_columns]

### App callbacks for download page
@app.callback(
    Output('dl-diagnostic-inputs', 'children'),
    [Input('dl-case-dropdown', 'value'),
    Input('dl-diagnostic-dropdown', 'value')]
)

def update_diagnostic_input(inputfolder, diagnostic):
    if (diagnostic == None) | (inputfolder == None):
        raise PreventUpdate
    if diagnostic == 'Dashboard Input File':
        DASHBOARD_INPUT_FORM = html.Div(
            [
                dbc.Button('Generate Dashboard Input File', id='dl-generatedashboardinput-btn', color='primary', n_clicks=0), 
                dbc.Toast(
                    [html.P('File Saved and Exported', className="mb-0")],
                    id='dl-generatedashboardinput-toast',
                    header='Done',
                    is_open=False,
                    dismissable=True,)
            ]
        )
        return DASHBOARD_INPUT_FORM

    if diagnostic == 'Phase 3X & 4X Processor':
        # load dropdowns
        inputfolder = raw_results_dir+ '/' + inputfolder + '/'
        mmfile = inputfolder + [i for i in os.listdir(inputfolder) if os.path.isfile(os.path.join(inputfolder, i)) and 'mm' in i][0]
        df_ca = pd.read_excel(mmfile, sheet_name ='CA')
        df_utilities = pd.read_excel(mmfile, sheet_name='UTILITIES')
        lst_ca = df_ca['CA'].tolist()
        lst_utilities = df_utilities['UTILITY'].tolist()
        INPUT_PHASE_PROCESSOR = dbc.Form(
            [
                dbc.FormGroup(
                    [
                        dbc.Label('3X or 4X'),
                        dbc.RadioItems(id='dl-phase-radio', options = [{'label': '3X', 'value' : '3X'}, {'label': '4X', 'value' : '4X'},], value = '4X'),
                    ]
                ),
                dbc.FormGroup(
                    [
                        dbc.Label('Period'),
                        dcc.Dropdown(id='dl-period-dropdown', placeholder='Required', options = [{'label':i, 'value':i} for i in lst_periods]),
                    ]
                ),
                dbc.FormGroup(
                    [
                        dbc.Label('DM'),
                        dcc.Dropdown(id='dl-dm-dropdown', placeholder='Required', options = [{'label':i, 'value':i} for i in lst_ca]),
                    ]
                ),
                dbc.FormGroup(
                    [
                        dbc.Label('CA'),
                        dcc.Dropdown(id='dl-ca-dropdown', placeholder='Optional', options = [{'label':i, 'value':i} for i in lst_ca]),
                    ]
                ),
                dbc.FormGroup(
                    [
                        dbc.Label('Utility'),
                        dcc.Dropdown(id='dl-utility-dropdown', placeholder='Optional', options = [{'label':i, 'value':i} for i in lst_utilities]),
                    ]
                ),
                dbc.Button('Process Phase 3X4X', id = 'dl-generatephase-btn', color = 'primary', className = 'mr-1', n_clicks = 0),
                dbc.Toast(
                    [html.P('File Saved and Exported', className="mb-0")],
                    id='dl-processphase-toast',
                    header='Done',
                    is_open=False,
                    dismissable=True,
                ),
            ]
        )
        return INPUT_PHASE_PROCESSOR
    return html.H5('Error')

@app.callback(
    Output('dl-processphase-toast', 'is_open'),
    [Input('dl-generatephase-btn', 'n_clicks')],
    [State('dl-case-dropdown', 'value'),
    State('dl-output-textbox', 'value'),
    State('dl-phase-radio', 'value'),
    State('dl-period-dropdown', 'value'),
    State('dl-dm-dropdown', 'value'),
    State('dl-ca-dropdown', 'value'),
    State('dl-utility-dropdown', 'value')]
)    
def generate_process_phase3x4x(n_clicks, case, outputfolder, phase, period, dm, ca, utility):
    if n_clicks == 0:
        raise PreventUpdate
    lst_period = [period]
    lst_dm = [dm]
    if ca == None:
        lst_ca = []
    else:
        lst_ca = [ca]
    if utility == None:
        lst_utility = []
    else:
        lst_utility = [utility]

    inputfolder = raw_results_dir+ '/' + case + '/'
    inputfile = inputfolder + [i for i in os.listdir(inputfolder) if os.path.isfile(os.path.join(inputfolder, i)) and phase in i][0]
    outputfile = outputfolder + phase + '_processed_' + case + '.xlsx'
    dpt.process_phase3x4x(inputfile, outputfile, lst_period, lst_dm, lst_ca, lst_utility)
    return True

@app.callback(
    Output('dl-generatedashboardinput-toast', 'is_open'),
    [Input('dl-generatedashboardinput-btn', 'n_clicks')],
    [State('dl-case-dropdown', 'value'),
    State('dl-output-textbox', 'value'),]
)

def generate_dashboardinput(n_clicks, case, outputfolder):
    if n_clicks == 0:
        raise PreventUpdate
    dpt.dashboard_input(raw_results_dir, case, outputfolder)
    return True



app.title = 'DPT Diagnostics'
app.layout = html.Div(
    [
        dcc.Location(id='url'),
        html.Div(id='page-content') #, children=[NAVBAR, BODY])
    ]
)



if __name__ == '__main__':
    app.run_server(host='127.0.0.1', port='8050', debug=True, dev_tools_ui=True)