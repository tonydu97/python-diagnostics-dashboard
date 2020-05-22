### DPT Diagnostics Library - for Import
import numpy as np 
import pandas as pd 

def process_phase3x4x(inputfile, outputfile, period=[], measure=['AEC'], dm=[], ca=[], utility=[], unit=[], groupby=['Unit'], sum_across=[]):
    ''' 
    Process Phase 3x or 4x file
    Inputs:
        inputfile - .csv file as string
        outputfile - .xlsx file as string
        period - list
        dm - list
        ca - list
        utility - list
        unit - list
        groupby- list
        sum_across - list

    Source: Phase3x & 4X Data Processor.py
    '''
    if inputfile.find('4X') != -1:
        phase = '4X'
        rounds = []
    else:
        phase = '3X'
        rounds = [1]
    
    
    
    #Read data 
    all_data = pd.read_table(inputfile, delimiter=',', encoding='latin-1')
    all_data = all_data[all_data['Unit'] != 'DummyGen']

    ### Disaggregated (i.e. generator/unit-level)
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
    filters=pd.DataFrame(data=[inputfile,
                            period,measure,dm,ca,rounds,utility,unit,groupby,sum_across],
                                index=['Input File:','Period:','Measure:','DM:','CA:','Rounds:','Utility:','Unit:','Group by:','Sum across:']) 

    ### Export filtered dataframe ###
    #print '\nWriting output file...'
    writer=pd.ExcelWriter(outputfile ,engine = 'openpyxl')
    filters.to_excel(writer,startrow=1,index=True,header=False)
    out_df.to_excel(writer,startrow=12,index=False)
    writer.save()



