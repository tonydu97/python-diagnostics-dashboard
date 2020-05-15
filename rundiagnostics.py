'''

Diagnostics for M&A DPT Analysis
Processes raw results 
Creates input xlsx file to be used for dashboard visualization and analysis

Tony Du
Last updated 4/26/20


'''
import pandas as pd
import numpy as np
import os 


folder = 'C:/Users/tdu/python/Raw results/' 
case = 'jli_v21_FG_5SILs_pjm_origMCP_pre_plus'

# TODO use __file__
inputfolder = folder + case + '/'
output = 'diagnostics/d_'+ case + '.xlsx'

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


    df_BAA = df_map_mm['CA']
    df_BAA = df_BAA.drop(columns=['CA']).dropna()
    df_mcp = df_map_mm['mcp'].round(2)
    df_loads = df_map_mm['loads'].round(0)
    df_loss = df_map_mm['loss'].round(3)

    df_gen_cap = df_map_mm['unit_tcap']
    df_gen_avl = df_map_mm['unit_avail']
    df_tx_cap = df_map_mm['line_cap']
    df_tx_avl = df_map_mm['line_avail']
    df_wheel = df_map_mm['line_wheel'].round(2)

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
    df_gen_out = df_gen_out[df_gen_out['gen_MW'] > 0]

    # transmission 
    df_tx_out = df_tx_avl.set_index(['From_CA', 'To_CA'])
    df_tx_out = df_tx_out.join(df_tx_cap.set_index(['From_CA', 'To_CA']), how = 'left')
    df_tx_out['tx_line_MW'] = df_tx_out['line_avail'] * df_tx_out['Line_Cap'] 
    df_tx_out = df_tx_out.groupby(['From_CA', 'To_CA', 'PERIOD'])['tx_line_MW'].sum().reset_index().round(0)

    # wheeling
    df_wheel['Unique'] = df_wheel['From_CA'] + df_wheel['To_CA']
    df_wheel_on = df_wheel[(df_wheel['Period'] == 'S_SP1')].set_index('Unique')
    df_wheel_off = df_wheel[(df_wheel['Period'] == 'S_OP')].set_index('Unique')

    df_wheel_out = df_wheel_on.rename(columns={'wheel' : 'On-Peak'})
    df_wheel_out['Off-Peak'] = df_wheel_off['wheel']
    df_wheel_out = df_wheel_out[['From_CA', 'To_CA', 'On-Peak', 'Off-Peak']]

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
    df_4x = pd.read_csv(file_4x, delimiter = ',', encoding = 'latin-1')
    df_4x = df_4x[(df_4x['Unit'] != 'DummyGen')]
    df_4x.rename(columns = {'Gen' : '4X'}, inplace = True)

    df_3x = pd.read_csv(file_3x, delimiter = ',', encoding = 'latin-1')
    df_3x = df_3x[(df_3x['Unit'] != 'DummyGen') & (df_3x['Round'] == 1)]
    df_3x.rename(columns = {'Gen' : '3X'}, inplace = True)


    df_group_4x = df_4x.groupby(['Utility', 'DM', 'CA', 'Period'])[['4X']].sum().round(0)
    df_group_3x = df_3x.groupby(['Utility', 'DM', 'CA', 'Period'])[['3X']].sum().round(0)


    df_out = pd.concat([df_group_3x, df_group_4x], axis=1).reset_index()
    df_out = df_out[(df_out['3X'] > 0) & (df_out['4X'] > 0) ]

    df_out.to_excel(writer, index=False, sheet_name='phase')
        
    print ('phase3x4x complete')

def top_players():
    df_hhi = pd.read_csv(file_hhi, encoding='ISO-8859-1')
    df_hhi = df_hhi[df_hhi['Measure'] == 'AEC']

    # export to excel
    df_hhi.rename(columns={'MW_with_LSF': 'MW', 'Share_with_LSF(%)':'Share', 'HHI_with_LSF' : 'HHI' }, inplace=True)
    df_hhi = df_hhi[['Period', 'DM', 'Utility', 'MW', 'Share', 'HHI']]
    df_hhi = df_hhi[df_hhi['HHI'] != 0]
    df_hhi['MW'] = df_hhi['MW'].round(0)
    df_hhi['HHI'] = df_hhi['HHI'].round(0)
    df_hhi.to_excel(writer, index=False, sheet_name='hhi')
    print('top players complete')


def supply_curve():
    df_supply = pd.read_excel(file_x, sheet_name='DPT_supply_curve')
    df_supply.rename(columns={'Prime mover' : 'Type', 'Marginal cost' : 'MC', 'Capacity (MW)' :'Capacity'}, inplace=True)
    df_supply = df_supply[['Period', 'BAA', 'Generator', 'Owner', 'Type', 'MC', 'Capacity']]
    df_supply['MC'] = df_supply['MC'].round(2)
    df_supply['Capacity'] = df_supply['Capacity'].round(0)
    df_supply.to_excel(writer, index=False, sheet_name='supply')
    print('supply curve complete')




#supply curve tests
# df_supply = pd.read_excel(file_x, sheet_name='DPT_supply_curve')
# df_supply.rename(columns={'Prime mover' : 'Type', 'Marginal cost' : 'MC', 'Capacity (MW)' :'Capacity'}, inplace=True)
# df_supply = df_supply[['Period', 'BAA', 'Generator', 'Owner', 'Type', 'MC', 'Capacity']]
# df_supply['MC'] = df_supply['MC'].round(2)
# df_supply['Capacity'] = df_supply['Capacity'].round(0)
# print('supply curve complete')
# df_load = pd.read_excel(file_mm, sheet_name='loads')

# df_wheel = pd.read_excel(file_mm, sheet_name='line_wheel')
# # df_wheel['Unique'] = df_wheel['From_CA'] + df_wheel['To_CA']
# # df_wheel_on = df_wheel[(df_wheel['Period'] == 'S_SP1')].set_index('Unique')
# # df_wheel_off = df_wheel[(df_wheel['Period'] == 'S_OP')].set_index('Unique')

# # df_wheel_out = df_wheel_on.rename({'Line_Wheel' : 'On-Peak'})
# # df_wheel_out['Off-Peak'] = df_wheel_off['Line_Wheel']

# # def f(row):
# #     if row['Period'] == 'S_SP1':
# #         val = 'On-Peak'
# #     else:
# #         val = 'Off-Peak'
# #     return val

# # df_wheel_out['Peak'] = df_wheel_out.apply(f, axis=1)

# # df_wheel_out

# df_wheel['Unique'] = df_wheel['From_CA'] + df_wheel['To_CA']
# df_wheel_on = df_wheel[(df_wheel['Period'] == 'S_SP1')].set_index('Unique')
# df_wheel_off = df_wheel[(df_wheel['Period'] == 'S_OP')].set_index('Unique')

# df_wheel_out = df_wheel_on.rename(columns={'Line_Wheel' : 'On-Peak'})
# df_wheel_out['Off-Peak'] = df_wheel_off['Line_Wheel']
# df_wheel_out = df_wheel_out[['From_CA', 'To_CA', 'On-Peak', 'Off-Peak']]

mm_summary()
top_players()
supply_curve()
phase()
print('Saving to excel')
writer.save()
print('Done')
