#G03 Supply Curve Tail - Identify Marginal unit, AEC units, and Non-Economic units for each period 
#MW Sensitivity: compare changes in available AEC from MCP changes
#v2: add wheeling rates
#Author: Tdu

import numpy as np
import pandas as pd
import os as os
import datetime
from xlsxwriter.utility import xl_range


### User Inputs ### 

os.chdir('F:\\Energy&Environ\\EMacan26602.00-Project Alice\\Analysis - Jagali\\Diagnostics\\G03 - Supply curve tail')
case = 'jli_v13_GF_ali135_bul_mit250Mc75L200R75P100J_plus'
inputfolder = 'F:\\Energy&Environ\\EMacan26602.00-Project Alice\\Analysis - Jagali\\Results\\Raw results\\' + case +  '\\'

mcpfile = inputfolder + 'MCP.csv'
mmfile = inputfolder + [i for i in os.listdir(inputfolder) if os.path.isfile(os.path.join(inputfolder, i)) and 'mm_jli' in i][0]
xfile = inputfolder + [i for i in os.listdir(inputfolder) if os.path.isfile(os.path.join(inputfolder, i)) and 'x - data' in i][0]


owners_lst = ['p3', 'p32', 'p4', 'p5', 'p6', 'NextEra Energy Inc']
baa = 'SC'
#periods_lst = ['S_SP1', 'S_SP2', 'S_P', 'S_OP', 'W_SP', 'W_P', 'W_OP', 'H_SP', 'H_P', 'H_OP']
periods_lst = ['S_OP', 'H_OP']
mcp_DM = baa
mcp_case = 'cp_plus' #'cp_base' 'cp_plus' 'cp_minus'


outputfile = 'Output\\MCP_sens_' + case + '_' + baa + '_MCP_' + mcp_DM + mcp_case[3:] + '_' + (datetime.datetime.now().strftime("%Y%m%d-%H%M")) + '_output.xlsx'


### Sensitivity Inputs ###
deviations_count = 6 #how many deviations in one direction
deviations_amount = 0.5


### Formatting ###
writer = pd.ExcelWriter(outputfile, engine = 'xlsxwriter')
workbook = writer.book
format_perc = workbook.add_format({'num_format': '0%'})
format_int = workbook.add_format({'num_format': '#,##0'})
format_dollar = workbook.add_format({'num_format': '$#,##0.00'})


### Add wheeling rates if necessary ###
case_lst = ['cp_base', 'cp_plus', 'cp_minus']
#case_lst = ['cp_plus']
mcp_df = pd.read_csv(mcpfile)
mcp_df = mcp_df[mcp_df['DM'] == mcp_DM]
mcp_df = mcp_df.set_index('PERIOD')[case_lst] * 1.05
if baa != mcp_DM:
    wheeling_df = pd.read_excel(mmfile, sheet_name = 'line_wheel')
    new_wheeling_df = wheeling_df[wheeling_df['From_CA'] == baa][wheeling_df['To_CA'] == mcp_DM].set_index('Period')
    for case in case_lst:
        mcp_df[case] -= new_wheeling_df['Line_Wheel']
    
### Output ###

for owner in owners_lst:
    print(owner)
    orig_df = pd.read_excel(xfile, sheet_name='DPT_supply_curve')
    sheetname = owner[:10] + ' ' + baa + ' ' + mcp_DM + mcp_case[3:]

    row_index = 1

    #Marginal Units Analysis
    for period in periods_lst:

        ###
        #Find load served then filter on MCP 
        col_index = 1
        orig_df.rename(columns = {'serving load?' : 'MW'}, inplace = True)
        avail_df = orig_df[orig_df['Period'] == period][orig_df['BAA'] == baa][orig_df['Owner'] == owner][orig_df['MW'] > 0]
        mcp_val = float(mcp_df.loc[period][mcp_case]) 
        aec_units_df = avail_df.loc[avail_df['Marginal cost'] <= mcp_val]
        marginal_unit_df = aec_units_df.loc[aec_units_df['Capacity (MW)'] != aec_units_df['MW']].iloc[0:1]
        if len(marginal_unit_df) == 1:
            aec_units_df = aec_units_df.iloc[1:]
        noneco_units_df = avail_df.loc[avail_df['Marginal cost'] > mcp_val]

        #Select specific columns to output
        marginal_unit_df = marginal_unit_df[['Generator', 'Marginal cost', 'MW']]
        aec_units_df = aec_units_df[['Generator', 'Marginal cost', 'MW']]
        noneco_units_df = noneco_units_df[['Generator', 'Marginal cost', 'MW']]

        #Save to Excel
        marginal_header = pd.DataFrame(columns = ['Marginal Unit'])
        aec_header = pd.DataFrame(columns = ['AEC Units'])
        noneco_header = pd.DataFrame(columns = ['Non-Economic Units'])
        period_col = pd.DataFrame(columns = [period])

        period_col.to_excel(writer, index = False, sheet_name = sheetname, startcol = 0, startrow = row_index)
        worksheet = writer.sheets[sheetname]
        worksheet.write_number(row_index -1, 0, mcp_val)
        marginal_header.to_excel(writer, index = False, sheet_name = sheetname, startcol = col_index)
        marginal_unit_df.to_excel(writer, index = False, sheet_name = sheetname, startcol = col_index, startrow = row_index)
        col_index += 4
        aec_header.to_excel(writer, index = False, sheet_name = sheetname, startcol = col_index)
        aec_units_df.to_excel(writer, index = False, sheet_name = sheetname, startcol = col_index, startrow = row_index)
        col_index += 4
        noneco_header.to_excel(writer, index = False, sheet_name = sheetname, startcol = col_index)
        noneco_units_df.to_excel(writer, index = False, sheet_name = sheetname, startcol = col_index, startrow = row_index)
        row_index += (max(len(marginal_unit_df.index), len(aec_units_df.index), len(noneco_units_df.index)) + 3)

    #MCP Sensitivity Analysis

    load_df = pd.read_excel(mmfile, sheet_name='loads')
    filter_load_df = load_df[load_df['CA'] == baa][load_df['UTILITY'] == owner]
    filter_load_df.set_index('PERIOD', inplace = True)

    row_index = 0
    for case in case_lst:
        sens_df = mcp_df.loc[mcp_df.index.isin(periods_lst)][[case]]

        #create table
        for period in sens_df.index:
            mcp_val = float(sens_df.loc[period, case])
            if len(filter_load_df) == 0:
                load_val = 0
            else:
                load_val = float(filter_load_df.loc[period, 'LOAD'])

            #subtract from MCP
            for i in range(-deviations_count, 0):
                sens_df.loc[period, '-$'+ str(-i*deviations_amount)] = max(0, float(orig_df[['Capacity (MW)']][orig_df['Marginal cost'] <= mcp_val + i*deviations_amount ][orig_df['Period'] == period][orig_df['Owner'] == owner][orig_df['BAA'] == baa].sum()) - load_val)

            #MCP AEC
            sens_df.loc[period, 'MCP'] = max(0, float(orig_df[['Capacity (MW)']][orig_df['Marginal cost'] <= mcp_val][orig_df['Period'] == period][orig_df['Owner'] == owner][orig_df['BAA'] == baa].sum()) - load_val)

            #add to MCP
            for i in range(1, deviations_count + 1):
                sens_df.loc[period, '+$'+ str(i*deviations_amount)] = max(0, float(orig_df[['Capacity (MW)']][orig_df['Marginal cost'] <= mcp_val + i*deviations_amount ][orig_df['Period'] == period][orig_df['Owner'] == owner][orig_df['BAA'] == baa].sum()) - load_val)

        sens_df = sens_df.rename(columns = {case: '105% of MCP'})
        sens_df.to_excel(writer, sheet_name = owner+ ' Sens', startrow = row_index + 1)
        sensworksheet = writer.sheets[owner + ' Sens']
        sensworksheet.write(row_index, 0, case[3:] + ' case')
        
        #conditional format table
        for i in range(len(sens_df.index) + 1):
            conditionalformat_range = xl_range(row_index + 1 + i, 2, row_index+ 1 + i, 2 + deviations_count*2 + 2)
            sensworksheet.conditional_format(conditionalformat_range, {'type' : 
            '3_color_scale',
            'min_color': '#5A8AC6',
            'max_color': '#F8696B',
            'mid_color' : 'white'})
        row_index += 13

    worksheet.set_column('A:A', 15, format_dollar)
    worksheet.set_column('B:ZZ', 15, format_int )
    worksheet.set_column('C:C', 15, format_dollar)
    worksheet.set_column('G:G', 15, format_dollar)
    worksheet.set_column('K:K', 15, format_dollar)
    # sensworksheet = writer.sheets['MCP Sensitivity']
    # sensworksheet.set_column('A:ZZ', 15, format_int)
    # sensworksheet.set_column('B:B', 15, format_dollar)
writer.save()    
print('Done')

