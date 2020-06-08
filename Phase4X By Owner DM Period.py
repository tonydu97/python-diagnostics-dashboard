#Phase3X & 4x Summary and graphics - Identify imports coming in to DM, graphics for Top 10 players in each period 
#Author: Tdu

import numpy as numpy
import pandas as pd
import os as os
import datetime

os.chdir('F:\\Energy&Environ\\EMacan26602.00-Project Alice\\Analysis - Jagali\\Diagnostics\\T01 - Phase4X - gv\\')
case = 'jli_v22_FG_consAG3_bul_mit4ALGAMS_base'
inputfolder = 'F:\\Energy&Environ\\EMacan26602.00-Project Alice\\Analysis - Jagali\\Results\\Raw results\\' + case +  '\\'

xfile = inputfolder + [i for i in os.listdir(inputfolder) if os.path.isfile(os.path.join(inputfolder, i)) and 'x - data' in i][0]

phase3xfile = inputfolder + [i for i in os.listdir(inputfolder) if os.path.isfile(os.path.join(inputfolder, i)) and 'Phase3X' in i][0]
phase4xfile = inputfolder + [i for i in os.listdir(inputfolder) if os.path.isfile(os.path.join(inputfolder, i)) and 'Phase4X' in i][0]

### User Inputs ###
include3x = True
periods_lst = ['S_SP1', 'S_SP2', 'S_P', 'S_OP', 'W_SP', 'W_P', 'W_OP', 'H_SP', 'H_P', 'H_OP']
utility_lst = ['NextEra Energy Inc', 'Southern Co']
#dm_lst = ['SC', 'SCEG', 'ALGAMS', 'FG', 'CPLE', 'DUK', 'AEC', 'GVL', 'TAL']
dm_lst = ['SC', 'SCEG', 'ALGAMS', 'FG','CPLE', 'DUK', 'AEC', 'FMPP', 'FPC', 'GVL','JEA','MISO', 'SEC', 'TAL', 'TEC', 'TVA'] 
#dm_lst = ['FG']
# dm_lst = ['SOCO', 'SC', 'SCEG',  'CPLE', 'DUK', 'JEA', 'TAL']
#dm_lst = ['ALGAMS', 'GF', 'FPL', 'DUK', 'SC', 'SCEG', 'CPLE', 'JEA', 'TAL']
#dm_lst = ['ALGAMS', 'GF', 'FPL', 'SC', 'SCEG', 'DUK', 'CPLE', 'AEC', 'GVL', 'TAL'] 
outputfile = 'Phase4X By Owner DM Period\\3xand4x_ByUtility_' + case + '_output_' + (datetime.datetime.now().strftime("%Y%m%d-%H%M")) +'.xlsx'

### Formatting ###
writer = pd.ExcelWriter(outputfile, engine = 'xlsxwriter')
workbook = writer.book
format_perc = workbook.add_format({'num_format': '0%'})
format_int = workbook.add_format({'num_format': '#,##0'})
format_float = workbook.add_format({'num_format': '#,##0.00'})


### Output ###
print('Reading in Phase4X')
phase4x_df = pd.read_csv(phase4xfile, delimiter = ',', encoding = 'latin-1')
phase4x_df = phase4x_df[phase4x_df['Unit'] != 'DummyGen']
# xfile_df = pd.read_excel(xfile, sheet_name = 'DPT_generator_list', skiprows = [0])[['Generator ID', 'Unit name']] 
# print('Merging with xfile for unit names')
# phase4x_df = phase4x_df.merge(xfile_df, left_on ='Unit', right_on = 'Generator ID')

if include3x:
    print('Reading in Phase3X')
    phase3x_df = pd.read_csv(phase3xfile, delimiter = ',', encoding = 'latin-1')
    phase3x_df = phase3x_df[phase3x_df['Unit'] != 'DummyGen']

noneheader = pd.DataFrame(columns = ['NA'])
for dm in dm_lst:
    print(dm)
    col = 0
    for utility in utility_lst:
        row = 1
        for period in periods_lst:
            if include3x:
                filter_phase3x_df = phase3x_df.loc[phase3x_df['Gen'] > 0][phase3x_df['Round'] == 1][phase3x_df['Utility'] == utility][phase3x_df['DM'] == dm][phase3x_df['Period'] == period][['Unit', 'Utility', 'CA', 'Gen']]
                filter_phase3x_df.rename(columns = {'Gen' : 'Gen_3X'}, inplace = True)
                filter_phase4x_df = phase4x_df.loc[phase4x_df['Gen'] > 0][phase4x_df['Utility'] == utility][phase4x_df['DM'] == dm][phase4x_df['Period'] == period][['Unit', 'Utility', 'CA', 'Gen']]
                groupby3x_df = filter_phase3x_df.groupby(['Utility', 'CA'])[['Gen_3X']].sum()
                groupby4x_df = filter_phase4x_df.groupby(['Utility', 'CA'])[['Gen']].sum()
                out_df = pd.concat([groupby4x_df, groupby3x_df], axis =1 )
            else:
                filter_df = phase4x_df.loc[phase4x_df['Utility'] == utility][phase4x_df['Gen'] > 0 ][phase4x_df['DM'] == dm][phase4x_df['Period'] == period][['Unit name', 'Generator ID', 'Utility', 'CA', 'Gen']]
                out_df = filter_df.groupby(['Utility', 'CA'])[['Gen']].sum()
            if len(out_df) != 0:
                out_df.to_excel(writer, sheet_name = dm, startrow = row, startcol = col)
            else:
                noneheader.to_excel(writer, sheet_name = dm, startrow = row, startcol = col)
            worksheet = writer.sheets[dm]
            worksheet.write(row - 1, col, period + ' ' + utility)        
            row += (len(out_df) + 3)

        col += 6 
    print('Writing to Excel')

    
    worksheet.set_column('A:ZZ', 18, format_int)

writer.save()    
print('Done')


