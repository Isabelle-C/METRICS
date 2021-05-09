#----- Importing Packages -----####
from ABM import load_json
from abm_parse import load as ABM_load
from abm_parse import get_radius
import pickle
import glob
import ABM

import pandas as pd
import os
import numpy as np
import itertools
import argparse
from argparse import ArgumentParser

__author__ = "Isabelle Chen"
__email__ = "isabellechen2023@u.northwestern.edu"

#-- Variable Declaration ####
pkllist = []
parameter_list = ['NECRO_FRAC','SENES_FRAC','E_THRES','MAX_HEIGHT','ACCURACY','AFFINITY','DEATH_AGE_AVG','DIVISION_POTENTIAL','META_PREF','MIGRA_THRESHOLD']

#-- Setup argument parser ####
parser = ArgumentParser(description="Collect evolution data into a pkl file.")
parser.add_argument(dest="read_path",help="Raw PKL directory.")
parser.add_argument(dest="param_path",help="JSON directory.")
parser.add_argument(dest="save_collect",help="Save pkl directory.")

args = parser.parse_args()

#----- Function Definitions -----####

#-- Initialization ####
def initialize_cont_parameter_dict(pop_list,parameter_list):
    """Initialize the continuous property information in a dictionary:
    1. NECRO_FRAC
    2. SENES_FRAC
    3. E_THRES
    4. MAX_HEIGHT
    5. ACCURACY
    6. AFFINITY
    7. DEATH_AGE_AVG
    8. DIVISION_POTENTIAL
    9. META_PREF
    10. MIGRA_THRESHOLD
    """
    parameter_dict = {}
    parameter_dict['seed']=[]
    parameter_dict['timepoint'] = []
    parameter_dict['T_HET'] = []
    parameter_dict['C_HET'] = []
    parameter_dict['populations'] = []

#    for seed_select in seed_list:
#        for time_select in time_list:
    for pop_select in pop_list:
        type_out = get_population_name(pop_select)
        param_name1 = f"{type_out}_Cycle"
        param_name2 = f"{type_out}_Volume"
        #parameter_dict[param_name1] = []
        #parameter_dict[param_name2] = []
        for parameter_select in parameter_list:
            #param_name = f"{parameter_select}_S{seed_select}_{type_out}_T{str(time_select).replace('.', '_')}"
            param_name = f"{type_out}_{parameter_select}"
            parameter_dict[param_name] = []
    return parameter_dict

def initialize_pop_count_dict(pop_list,type_list):
    """Initialize the population counts information in a dictionary:
    """
    count_dict = {}
    count_dict['seed']=[]
    count_dict['timepoint'] = []
    count_dict['T_HET'] = []
    count_dict['C_HET'] = []
    count_dict['populations'] = []

#    for seed_select in seed_list:
#        for time_select in time_list:
    for pop_select in pop_list:
        type_out = get_population_name(pop_select)
        param_name1 = f"total_{type_out}"
        count_dict[param_name1] = []
        for type_select in type_list:
            #param_name = f"{parameter_select}_S{seed_select}_{type_out}_T{str(time_select).replace('.', '_')}"
            type_name= get_type_name(type_select)
            param_name = f"{type_out}_{type_name}"
            count_dict[param_name] = []
    return count_dict

#-- Print out information of the population, type, timepoints, and seed information of pickle files ####
def pull_standard_lists(D_in, N_in):
    '''
    Print out information of the population, type, timepoints, and seed information of pickle files
    '''
    pop_list = D_in['setup']['pops']  # -- Output is [0,1]
    type_list = D_in['setup']['types']
    time_list = D_in['setup']['time']
    seed_list = []
    for seed_ii in range(0, N_in):
        seed_list.append(seed_ii)

    return pop_list, type_list, time_list, seed_list

#-- Define the numbers in population, type, and properties lists from pull_standard_lists function ####
def get_population_name(t_in):
    '''
    Return the population name.
    '''
    if t_in== 0:
        type_out = 'X'
    elif t_in== 1:
        type_out = 'A'
    elif t_in== 2:
        type_out = 'B'
    elif t_in== 3:
        type_out = 'C'
    elif t_in== 4:
        type_out = 'H'
    return type_out

def get_type_name(type_select):
    '''
    Return the type name.
    '''
    if type_select == 0:
        type_name = 'NEU'
    elif type_select == 1:
        type_name = 'APO'
    elif type_select == 2:
        type_name = 'QUI'
    elif type_select == 3:
        type_name = 'MIG'
    elif type_select == 4:
        type_name = 'PRO'
    elif type_select == 5:
        type_name = 'SEN'
    elif type_select == 6:
        type_name = 'NEC'

    return type_name

def get_property_name(j):
    '''
    Return the continuous property names.
    '''
    if j == 0:
        property_name = 'NECRO_FRAC'
    elif j == 1:
        property_name = 'SENES_FRAC'
    elif j == 2:
        property_name = 'E_THRES'
    elif j == 3:
        property_name = 'MAX_HEIGHT'
    elif j == 4:
        property_name = 'ACCURACY'
    elif j == 5:
        property_name = 'AFFINITY'
    elif j == 6:
        property_name = 'DEATH_AGE_AVG'
    elif j == 7:
        property_name = 'DIVISION_POTENTIAL'
    elif j == 8:
        property_name = 'META_PREF'
    elif j == 9:
        property_name = 'MIGRA_THRESHOLD'

    return property_name

#-- Collect population count information and continuous properties information
def count_population(D_in,N_in,H_in,C_in,time_list):
    '''
    Produce the dictionary containing the following information with counts:
    'seed','timepoint','T_HET','C_HET','populations',
    'total_X','total_A','total_B','total_C','total_H',
    'X_NEU', 'X_APO', 'X_QUI', 'X_MIG', 'X_PRO', 'X_SEN', 'X_NEC',
    'A_NEU', 'A_APO', 'A_QUI', 'A_MIG', 'A_PRO', 'A_SEN', 'A_NEC',
    'B_NEU', 'B_APO', 'B_QUI', 'B_MIG', 'B_PRO', 'B_SEN', 'B_NEC',
    'C_NEU', 'C_APO', 'C_QUI', 'C_MIG', 'C_PRO', 'C_SEN', 'C_NEC',
    'H_NEU', 'H_APO', 'H_QUI', 'H_MIG', 'H_PRO', 'H_SEN', 'H_NEC'
    '''
    for seed in range(0, N_in):
        for time_given in time_list:
            time = int(time_given) * 2
            matrix_pop_type = np.zeros((5, 7))  # -- amount of cells per population/type
            matrix_pop_type.astype(int)
            for height in range(0, H_in):
                for location in range(0, len(C_in)):
                    for position in range(0, 6):
                        # -- Selecting all population @ certain timepoint, seed, output will contain all the population (A,B,C, etc.)
                        if D_in['agents'][seed][time][height][location]['pop'][position] != -1:
                            yy = D_in['agents'][seed][time][height][location]['pop'][position]
                            jj = D_in['agents'][seed][time][height][location]['type'][position]
                            matrix_pop_type[yy][jj] += 1
            count_dict['seed'].append(seed)
            count_dict['timepoint'].append(time_given)
            count_dict['T_HET'].append(T_HET)
            count_dict['C_HET'].append(C_HET)
            count_dict['populations'].append(POP_NAME)
            for pop_select in pop_list:
                pop_out = get_population_name(pop_select)
                count_dict[f"total_{pop_out}"].append(sum(matrix_pop_type[pop_select]))
                for type_select in type_list:
                    type_name = get_type_name(type_select)
                    count_dict[f"{pop_out}_{type_name}"].append(matrix_pop_type[pop_select][type_select])
    return count_dict
        # param_name = f"{parameter_select}_S{seed_select}_{type_out}_T{str(time_select).replace('.', '_')}

def collect_cont_properties(time_list,N_in,H_in,C_in,D_in):
    '''
    Produce the dictionary containing the following information
    'seed','timepoint','T_HET','C_HET','populations',
    'X_Cycle','A_Cycle','B_Cycle','C_Cycle','H_Cycle',
    'X_Volume','A_Volume','B_Volume','C_Volume','H_Volume',
    'X_NECRO_FRAC', 'X_SENES_FRAC', 'X_ENERGY_THRESHOLD', 'X_MAX_HEIGHT', 'X_ACCURACY', 'X_AFFINITY', 'X_DEATH_AGE_AVG', 'X_DIVISION_POTENTIAL', 'X_META_PREF', 'X_MIGRA_THRESHOLD',
    'A_NECRO_FRAC', 'A_SENES_FRAC', 'A_ENERGY_THRESHOLD', 'A_MAX_HEIGHT', 'A_ACCURACY', 'A_AFFINITY', 'A_DEATH_AGE_AVG', 'A_DIVISION_POTENTIAL', 'A_META_PREF', 'A_MIGRA_THRESHOLD',
    'B_NECRO_FRAC', 'B_SENES_FRAC', 'B_ENERGY_THRESHOLD', 'B_MAX_HEIGHT', 'B_ACCURACY', 'B_AFFINITY', 'B_DEATH_AGE_AVG', 'B_DIVISION_POTENTIAL', 'B_META_PREF', 'B_MIGRA_THRESHOLD',
    'C_NECRO_FRAC', 'C_SENES_FRAC', 'C_ENERGY_THRESHOLD', 'C_MAX_HEIGHT', 'C_ACCURACY', 'C_AFFINITY', 'C_DEATH_AGE_AVG', 'C_DIVISION_POTENTIAL', 'C_META_PREF', 'C_MIGRA_THRESHOLD',
    'H_NECRO_FRAC', 'H_SENES_FRAC', 'H_ENERGY_THRESHOLD', 'H_MAX_HEIGHT', 'H_ACCURACY', 'H_AFFINITY', 'H_DEATH_AGE_AVG', 'H_DIVISION_POTENTIAL', 'H_META_PREF', 'H_MIGRA_THRESHOLD'
    '''
    for seed_select in seed_list:
        json_file_name = os.path.join(args.param_path + 'VIVO_HET_GRAPH_' + C_HET + '_' + T_HET + '_' + POP_NAME + '_0' + str(seed_select) + '.PARAM.json')
        print('Loading '+ json_file_name)
        JSON_IN = load_json(json_file_name)
        for time_select in time_list:
            time = int(time_select*2)
            for location in range(0, len(JSON_IN['timepoints'][time]['cells'])):
                for cells in range(0,len(JSON_IN['timepoints'][time]['cells'][location][1])):
                    #-- Extract which cell population the cell belongs to
                    t_info = JSON_IN['timepoints'][time]['cells'][location][1][cells][1]
                    type_out = get_population_name(t_in=t_info)
                    HOLD = []
                    HOLD.append(t_info)
                    # -- Add the informaiton into parameter dictionary
                    cont_param_dict['seed'].append(seed_select)
                    cont_param_dict['timepoint'].append(time_select)
                    cont_param_dict['T_HET'].append(T_HET)
                    cont_param_dict['C_HET'].append(C_HET)
                    cont_param_dict['populations'].append(POP_NAME)
                    #-- Add the continuous properties into the dictionary
                    for j in range(0, len(JSON_IN['timepoints'][time]['cells'][location][1][cells][4])):
                        parameter_select = get_property_name(j)
                        cont_info = str(JSON_IN['timepoints'][time]['cells'][location][1][cells][4][j])
                        cont_param_dict[f"{type_out}_{parameter_select}"].append(cont_info)
                    for pop_select in pop_list:
                       if pop_select not in HOLD:
                           type_out = get_population_name(t_in=pop_select)
                           for j in range(0, 10):
                               parameter_select = get_property_name(j)
                               cont_param_dict[f"{type_out}_{parameter_select}"].append('0')
    return cont_param_dict
'''
    for seed in range(0, N_in):
        for time_given in time_list:
            time = int(time_given) * 2
            for height in range(0, H_in):
                for location in range(0, len(C_in)):
                    for position in range(0, 6):
                        if D_in['agents'][seed][time][height][location]['pop'][position] != -1:
                            t_hold = D_in['agents'][seed][time][height][location]['pop'][position]
                            HOLD2 = []
                            HOLD2.append(t_hold)
                            type_out = get_population_name(t_in=t_hold)

                            volume_info= D_in['agents'][seed][time][height][location]['volume'][position]
                            cont_param_dict[f"{type_out}_Volume"].append(volume_info)

                            if D_in['agents'][seed][time][height][location]['cycle'][position] != -1:
                                cycle_info = D_in['agents'][seed][time][height][location]['cycle'][position]
                                cont_param_dict[f"{type_out}_Cycle"].append(cycle_info)
                            else:
                                cont_param_dict[f"{type_out}_Cycle"].append(0)

                            for pop_select in pop_list:
                                if pop_select not in HOLD2:
                                    type_out = get_population_name(t_in=pop_select)
                                    cont_param_dict[f"{type_out}_Cycle"].append(0)
                                    cont_param_dict[f"{type_out}_Volume"].append(0)

    return cont_param_dict
'''

#-- Reading all the file in read path
os.chdir(args.read_path)
x = 0
for file in glob.glob("*.pkl"):
    object_i = glob.glob("*.pkl")[x]
    pkllist.append(object_i)

    x += 1

for pkl_i in pkllist:
    print('----')
    print('Loading PKL file...')
    T_HET = pkl_i[(len('VIVO_HET_GRAPH_') + 4):(len('VIVO_HET_GRAPH_') + 7)]

    C_HET = pkl_i[len('VIVO_HET_GRAPH_'):(len('VIVO_HET_GRAPH_') + 3)]

    POP_NAME = pkl_i[(len('VIVO_HET_GRAPH_') + 8):(len(pkl_i) - 4)]
    
    print('T_HET:' + T_HET)
    print('C_HET:' + C_HET)
    print('POP:'+ POP_NAME)
    
    D, d, R, H, T, N, C, POPS, TYPES = ABM_load(pkl_i)
    
    pop_list, type_list, time_list, seed_list = pull_standard_lists(D_in=D, N_in=N)

    print('Counting population...')
    count_dict = initialize_pop_count_dict(pop_list,type_list)
    count_dict = count_population(D,N,H,C,time_list)
    count = pd.DataFrame(count_dict)

    print('Saving PKL File...')
    FILENAME_i = 'VIVO_HET_GRAPH_' + C_HET + '_' + T_HET + '_' + POP_NAME + '_collected'
    FILENAME = os.path.join(args.save_collect, FILENAME_i)
    
    with open(FILENAME + '.pkl', 'wb') as f:
        pickle.dump(count, f)

    print('Collecting continuous property information...')
    cont_param_dict = initialize_cont_parameter_dict(pop_list,parameter_list)
    cont_param_dict = collect_cont_properties(time_list,N,H,C,D)

    for x in cont_param_dict:
        print(str(x)+':'+str(len(cont_param_dict[x])))

    cont_param = pd.DataFrame(cont_param_dict)

    print('Saving PKL File...')
    FILENAME_i = 'VIVO_HET_GRAPH_' + C_HET + '_' + T_HET + '_' + POP_NAME + '_cont_collected'
    FILENAME = os.path.join(args.save_collect, FILENAME_i)
    
    with open(FILENAME + '.pkl', 'wb') as f:
        pickle.dump(cont_param, f)


'''
# VIVO_HET_GRAPH_140_110_X_00.PARAM
param_name = os.path.join('/Users/cheni/Desktop/FAKE_DATA/TEST_FAKE_JSON_00.PARAM.json')
# print(param_path+'VIVO_HET_GRAPH_'+C_HET+'_'+T_HET+'_'+POP_list+'_0'+str(seed)+'.PARAM')
a= load_json(param_name)

D, d, R, H, T, N, C, POPS, TYPES = ABM_load('/Users/cheni/Desktop/FAKE_DATA/TEST_FAKE_JSON.pkl')FAKE_DATA_TEST
'''