'''
4/25/20
Tony Du

Diagnostics suite for M&A DPT Analysis
Processes raw results folder 
Creates input xlsx file to be used for dashboard visualization and analysis


'''
import pandas as pd
import numpy as np
import os 


folder = 'C:/Users/tdu/python/Raw results/' 
case = 'jli_v21_FG_5SILs_pjm_origMCP_pre_plus'
inputfolder = folder + case + '/'
output = 'diagnostics/diagnostics_'+ case + '.xlsx'

file_x = inputfolder + [i for i in os.listdir(inputfolder) if os.path.isfile(os.path.join(inputfolder, i)) and 'x - data' in i][0]
file_3x = inputfolder + [i for i in os.listdir(inputfolder) if os.path.isfile(os.path.join(inputfolder, i)) and 'Phase3X' in i][0]
file_4x = inputfolder + [i for i in os.listdir(inputfolder) if os.path.isfile(os.path.join(inputfolder, i)) and 'Phase4X' in i][0]
file_mm = inputfolder + [i for i in os.listdir(inputfolder) if os.path.isfile(os.path.join(inputfolder, i)) and 'mm_' in i][0]
file_hhi = inputfolder + [i for i in os.listdir(inputfolder) if os.path.isfile(os.path.join(inputfolder, i)) and 'HHI' in i][0]

lst_periods = ['S_SP1','S_SP2','S_P','S_OP','W_SP','W_P','W_OP','H_SP','H_P','H_OP']
writer = pd.ExcelWriter(output, engine='xlsxwriter')



def mm_summary():
    df_map_mm = pd.read_excel(file_mm, sheet_name=None)
    df_map_mm.keys()

    # no changes
    df_BAA = df_map_mm['CA']
    df_mcp = df_map_mm['mcp']
    df_loads = df_map_mm['loads']
    df_loss = df_map_mm['loss']

    df_gen_cap = df_map_mm['unit_tcap']
    df_gen_avl = df_map_mm['unit_avail']
    df_tx_cap = df_map_mm['line_cap']
    df_tx_avl = df_map_mm['line_avail']
    df_wheel = df_map_mm['line_wheel']

    # shorten column names and make them consistent
    df_mcp.rename(columns={'DM': 'CA','CP': 'MCP'}, inplace=True)
    df_gen_cap.rename(columns={'Control area': 'CA', 'Utility':'UTILITY', 'Unit':'UNIT', 'Capacity (MW)':'Cap_MW'}, inplace=True)
    df_gen_avl.rename(columns={'unit_avail': 'Avl_MW'}, inplace=True)
    df_wheel.rename(columns={'Line_Wheel': 'wheel'}, inplace=True)


    # generation
    df_gen_out = df_gen_avl.set_index(['CA', 'UTILITY', 'UNIT'])
    df_gen_out = df_gen_out.reset_index().merge(df_gen_cap.reset_index(), on=['CA', 'UTILITY', 'UNIT'], how='left')
    df_gen_out['gen_MW'] = df_gen_out['Cap_MW'] * df_gen_out['Avl_MW']

    df_gen_out = df_gen_out.groupby(['CA', 'UTILITY', 'PERIOD'])['gen_MW'].sum().reset_index().round(0)

    # transmission 
    df_tx_out = df_tx_avl.set_index(['From_CA', 'To_CA'])
    df_tx_out = df_tx_out.join(df_tx_cap.set_index(['From_CA', 'To_CA']), how = 'left')
    df_tx_out['tx_line_MW'] = df_tx_out['line_avail'] * df_tx_out['Line_Cap'] 
    df_tx_out = df_tx_out.groupby(['From_CA', 'To_CA', 'PERIOD'])['tx_line_MW'].sum().reset_index().round(0)

    # wheeling
    df_wheel_out = df_wheel.drop(['From_CA'], axis=1).groupby(['To_CA', 'Period']).mean().reset_index()

    # export to excel
    df_BAA.to_excel(writer, index=False, sheet_name ='baa')
    df_mcp.to_excel(writer, index=False, sheet_name='mcp')
    df_loads.to_excel(writer, index=False, sheet_name='loads')
    df_loss.to_excel(writer, index=False, sheet_name='lineloss')
    df_gen_out.to_excel(writer, index=False, sheet_name='gen')
    df_tx_out.to_excel(writer, index=False, sheet_name='tx')
    df_wheel_out.to_excel(writer, index=False, sheet_name='wheel')

    print('mm summary complete')

def phase():
    pass

def top_players():
    pass

def supply_curve():
    pass

mm_summary()
writer.save()
