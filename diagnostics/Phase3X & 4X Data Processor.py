# -*- coding: utf-8 -*-
"""
Created on Mon Apr 08 17:16:02 2019

@author: MKang
"""

import pandas as pd
import timeit
start = timeit.default_timer() 

##############################################################################
################################# To update ##################################
############################### READ COMMENTS ################################
############################# for instructions! ##############################
##############################################################################

### Choose input file name and Phase: 3X or 4X. ###
input_file = 'jli_v15_FG_ali135_bul_plus_Phase4X.csv'
phase = '4X'

### To see a full list of possible criteria, see file 'FileName_selections.xlsx'
### Choose criteria. If unfiltered, leave as blank []. ###
period = ['W_SP']
measure = ['AEC']
dm = ['ALGAMS']
ca = []
rounds = [1] #1 for 3x, empty for 4x
utility = []
unit = []

### Choose desired aggregation level (i.e. by Utility, CA, DM, or Unit).
###  If desired level is disaggregated, (i.e. generator-level), you must write 'Unit.'
groupby = ['Unit']#['Unit']#['Utility']#['CA']#['DM']

### Add attributes to sum across (i.e. sum across Rounds, Periods, and/or Measures).
### To see all rounds, periods, and measures separately, leave blank [].
sum_across = [] #['Round'] #,'Period','Measure'] #]

##############################################################################
################################# End update #################################
##############################################################################

########################### Input and output files ###########################
### Input ###
folder = 'F:\\Energy&Environ\\EMacan26602.00-Project Alice\\Analysis - Jagali\\Diagnostics\\T01 - Phase4X - gv\\Input\\'
input_folder = folder #+ 'Input\\'

### Output ###
output_folder = folder #+ 'Output\\'
output_file = input_file[0:input_file.find('.')]+'_p'+str(period)+ '_m'+str(measure)+'_dm'+str(dm)+'_r'+str(rounds)+'_u'+str(utility)
    
if groupby == []:
    output_file = output_file + '_by[Unit]'
else:
    output_file = output_file + '_by[Aggregated]'
if sum_across == []:
    output_file = output_file + '_across[none].xlsx'
else:
    output_file = output_file + '_across'+str(sum_across)+'.xlsx'

################################# Read data ##################################

### Read data ###
#print 'Reading input data... '
read_start = timeit.default_timer() 
all_data = pd.read_table(input_folder + input_file, delimiter=',', encoding='latin-1')
all_data = all_data[all_data['Unit'] != 'DummyGen']
read_time = (timeit.default_timer() - read_start)
#print 'Data read time: ', read_time, 'seconds'

# Option to see the available selections for Period, Measure, DM, Round, and Utility: 
u_period = pd.Series(all_data['Period'].unique()) 
u_measure = pd.Series(all_data['Measure'].unique()) 
u_dm = pd.Series(all_data['DM'].unique()) 
u_rounds = pd.Series(all_data['Round'].unique()) 
u_utility = pd.Series(all_data['Utility'].unique())

selections = pd.concat([u_period,u_measure,u_dm,u_rounds,u_utility],axis=1)
selections.columns = ['Period','Measure','DM','Round','Utility']

writer=pd.ExcelWriter(folder + input_file[0:input_file.find('.')]+'_selections.xlsx',engine = 'openpyxl')
selections.to_excel(writer,index=False)
writer.save()

################################ Filter data #################################
### Drop irrelevant rows and make new relevant dataframe for output... ###
#print '\nFiltering data based on criteria...'

### Disaggregated (i.e. generator/unit-level)
for data in all_data:
    if period == []:
        out_df = all_data
    elif period != []:
        out_df = (all_data[(all_data['Period'].isin(period))])
    if measure != []:
        out_df = (out_df[(out_df['Measure'].isin(measure))])
    if dm != []:
        out_df = (out_df[(out_df['DM'].isin(dm))])
    if ca != []:
        out_df = (out_df[(out_df['CA'].isin(ca))])
    if rounds != []:
        out_df = (out_df[(out_df['Round'].isin(rounds))])
    if utility != []:
        out_df = (out_df[(out_df['Utility'].isin(utility))])
    if unit != []:
        out_df = (out_df[(out_df['Unit'].isin(unit))])
    
### Aggregated (other level) ###
if groupby != []:
    for g in groupby:
        if g == 'Unit':
            groupby_all = ['Unit','Utility','CA','DM']
        elif g == 'Utility':
            groupby_all = ['Utility','CA','DM']
        else:
            groupby_all = ['CA','DM']
sum_across_list = ['Period','Measure','Round']
if sum_across != []:
    for g in sum_across_list:
        if g not in sum_across:
            groupby_all.append(g)

if groupby != []:
    if phase == '4X':
        out_df = out_df.groupby(groupby_all)['Gen','CapLeft'].sum().reset_index()
    elif phase == '3X':
        out_df = out_df.groupby(groupby_all)['Gen','AvailCap'].sum().reset_index()

################################ Output file #################################
### Write informational header ###
filters=pd.DataFrame(data=[input_folder+input_file,
                           period,measure,dm,ca,rounds,utility,unit,groupby,sum_across],
                            index=['Input File:','Period:','Measure:','DM:','CA:','Rounds:','Utility:','Unit:','Group by:','Sum across:']) 

### Export filtered dataframe ###
#print '\nWriting output file...'
writer=pd.ExcelWriter(output_folder + output_file,engine = 'openpyxl')
filters.to_excel(writer,startrow=1,index=True,header=False)
out_df.to_excel(writer,startrow=12,index=False)
writer.save()

print ('Saved.')

total_time = (timeit.default_timer() - start)
#print '\nRuntime: ', total_time, 'seconds'
