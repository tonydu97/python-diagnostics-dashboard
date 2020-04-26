#G01 Top Players: Identify utilities in DMs with greatest marketshare in each period
#Author: Tdu
#Updated 11/16/19

import numpy as np
import pandas as pd
import os as os
import datetime 
### User Inputs ### 

os.chdir('F:\\Energy&Environ\\EMacan26602.00-Project Alice\\Analysis - Jagali\\Diagnostics\\G01 - Top players')
# dm_lst = ['ALGAMS', 'GF', 'FPL', 'SC', 'SCEG', 'CPLE', 'DUK', 'AEC', 'GVL', 'TAL']
dm_lst = ['ALGAMS', 'FG', 'SC', 'SCEG', 'CPLE', 'DUK', 'AEC', 'FPC', 'JEA', 'MISO', 'TAL', 'TVA']
#dm_lst = ['SOCO', 'FPL', 'SC', 'SCEG', 'CPLE', 'DUK', 'AEC', 'GVL', 'TAL']
#dm_lst = ['GVL']
measure = 'AEC'
#periods_lst = ['W_OP']
periods_lst = ['S_SP1', 'S_SP2', 'S_P', 'S_OP', 'W_SP', 'W_P', 'W_OP', 'H_SP', 'H_P', 'H_OP']
combine_sheets = True # True if all periods on one sheet, False if each period has its own sheet

 
case = 'jli_v15_FG_5SILs_naPV_SchSou_m10affL_origMCP_p20M_ali135_plus'
inputfile = 'F:\\Energy&Environ\\EMacan26602.00-Project Alice\\Analysis - Jagali\\Results\\Raw results\\' + case +  '\\' + case + '_HHI_By_Utility.csv'

dm_str = '' #'_post.join(dm_lst)



outputfile = 'Output\\topplayers_' + case + '_' + dm_str + '_' + (datetime.datetime.now().strftime("%Y%m%d-%H%M")) + '_output.xlsx'



### Formatting ###
writer = pd.ExcelWriter(outputfile, engine = 'xlsxwriter')
workbook = writer.book
format_perc = workbook.add_format({'num_format': '0.00%'})
format_int = workbook.add_format({'num_format': '#,##0'})




### Output ###
orig_df = pd.read_csv(inputfile, encoding = "ISO-8859-1")
for dm in dm_lst:
    col_index = 0
    row_index = 0
    current_season = 'S'
    for period in periods_lst:
        dm_period_df = orig_df.loc[orig_df['Period'] == period][orig_df['Measure'] == measure][orig_df['DM'] == dm]
        dm_period_df = dm_period_df.sort_values(by=['Share_with_LSF(%)'], ascending = False)
        over_threshold = len(dm_period_df[dm_period_df['Share_with_LSF(%)'] > 0.03])
        # if over_threshold >= 10:
        #     dm_period_df = dm_period_df.iloc[:over_threshold]
        # else:
        #     dm_period_df = dm_period_df.iloc[:10]
        dm_period_df = dm_period_df.iloc[:max(10, over_threshold)]
        if combine_sheets:       
            if period[:1] != current_season:
                current_season = period[:1]
                col_index += 9
                row_index = 0
                dm_period_df.to_excel(writer, sheet_name = dm, startcol = col_index, startrow = row_index, index = False)
                row_index += (max(10, over_threshold) + 2)  
            else:
                dm_period_df.to_excel(writer, sheet_name = dm, startcol = col_index, startrow = row_index, index = False)
                row_index += (max(10, over_threshold) + 2)  
            worksheet = writer.sheets[dm]
            worksheet.set_column(4 + col_index, 4 + col_index, None, format_int)
            worksheet.set_column(5 + col_index, 5 + col_index, None, format_int)
            worksheet.set_column(6 + col_index, 6 + col_index, None, format_perc)
            worksheet.set_column(7 + col_index, 7 + col_index, None, format_int)            
    
        else:
            dm_period_df.to_excel(writer, sheet_name = dm + ' ' + period, index = False)
            worksheet = writer.sheets[dm + ' ' + period]
            worksheet.set_column('E:E', None, format_int)
            worksheet.set_column('F:F', None, format_int)
            worksheet.set_column('G:G', None, format_perc)
            worksheet.set_column('H:H', None, format_int)

writer.save()
print('Done')


