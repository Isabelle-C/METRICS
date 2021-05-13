# ----- Importing Packages -----####
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

# -- Variable Declaration ####
pkllist = []
parameter_list = ['NECRO_FRAC', 'SENES_FRAC', 'E_THRES', 'MAX_HEIGHT', 'ACCURACY', 'AFFINITY', 'DEATH_AGE_AVG',
                  'DIVISION_POTENTIAL', 'META_PREF', 'MIGRA_THRESHOLD']

# -- Setup argument parser ####
parser = ArgumentParser(description="Collect evolution data into a pkl file.")
parser.add_argument(dest="read_path", help="Raw PKL directory.")
parser.add_argument(dest="param_path", help="JSON directory.")
parser.add_argument(dest="save_collect", help="Save pkl directory.")
parser.add_argument(dest="validation_path", help="Store the validation csv files.")
args = parser.parse_args()

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
def get_population_name(t_in):
    '''
    Return the population name.
    '''
    if t_in == 0:
        type_out = 'X'
    elif t_in == 1:
        type_out = 'A'
    elif t_in == 2:
        type_out = 'B'
    elif t_in == 3:
        type_out = 'C'
    elif t_in == 4:
        type_out = 'H'
    return type_out


# -- Reading all the file in read path
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
    print('POP:' + POP_NAME)

    D, d, R, H, T, N, C, POPS, TYPES = ABM_load(pkl_i)
    pop_list, type_list, time_list, seed_list = pull_standard_lists(D_in=D, N_in=N)

    print('Reading previously processed file...')
    FILENAME_i = 'VIVO_HET_GRAPH_' + C_HET + '_' + T_HET + '_' + POP_NAME + '_cont_collected'
    FILENAME = os.path.join(args.save_collect, FILENAME_i)

    FILENAME_i2 = 'VIVO_HET_GRAPH_' + C_HET + '_' + T_HET + '_' + POP_NAME + '_collected'
    FILENAME2 = os.path.join(args.save_collect, FILENAME_i2)



    with open(FILENAME2 + '.pkl', 'rb') as d:
        count_pkl = pickle.load(d)

    with open(FILENAME + '.pkl', 'rb') as f:
        cont_param = pd.read_pickle(f, compression=None)



    TIME_VALID = []
    SEED_VALID = []
    COUNTS_VALID = []
    POP_VALID = []
    #-- Validations
    for time_given in time_list:
        t22 = cont_param[cont_param['timepoint']==time_given]
        for pop_select in pop_list:
            type_out = get_population_name(pop_select)
            param = type_out+'_MIGRA_THRESHOLD'
            short = t22[[param,'seed']]
            for i in range(0,len(short)): #-- looping over seeds
                TIME_VALID.append(time_given)
                SEED_VALID.append(i)
                COUNTS_VALID.append(len(short[short['seed']==i][param].values[0]))
                POP_VALID.append(type_out)
    VALIDATION = {}
    VALIDATION['time'] = TIME_VALID
    VALIDATION['seed'] = SEED_VALID
    VALIDATION['counts'] = COUNTS_VALID
    VALIDATION['POP'] = POP_VALID

    #-- Producing the final tables for validation
    PARAM_COUNT = pd.DataFrame(VALIDATION)
    PKL_COUNT = count_pkl[['total_X','total_A','total_B','total_C','total_H','seed','timepoint']]

    p_name = 'param_count_'+C_HET+'_'+T_HET+'.csv'
    pkl_name = 'pkl_count_'+C_HET+'_'+T_HET+'.csv'

    pfname = os.path.join(args.validation_path, p_name)
    pklfname = os.path.join(args.validation_path, pkl_name)

    PARAM_COUNT.to_csv(pfname)
    PKL_COUNT.to_csv(pklfname)

    ERROR_TABLE = {}
    ERROR_TABLE['time'] = []
    ERROR_TABLE['seed'] = []
    ERROR_TABLE['population'] = []
    ERROR_TABLE['PKL'] = []
    ERROR_TABLE['PARAM'] = []
    for time_given in time_list:
        PKL_T = PKL_COUNT[PKL_COUNT['timepoint'] == time_given]
        PARAM_T = PARAM_COUNT[PARAM_COUNT['time'] == time_given]
        for seed_select in seed_list:
            PKL_TS = PKL_T[PKL_T['seed'] == seed_select]
            PARAM_TS = PARAM_T[PARAM_T['seed'] == seed_select]
            for pop_select in pop_list:
                type_out = get_population_name(pop_select)
                PARAM_ROW = PARAM_TS[PARAM_TS['POP'] == type_out]
                PARAM_VALUE = PARAM_ROW['counts'].values[0]
                PKL_VALUE = PKL_TS[f"total_{type_out}"].values[0]

                if PARAM_VALUE != int(PKL_VALUE):
                    ERROR_TABLE['time'].append(time_given)
                    ERROR_TABLE['seed'].append(seed_select)
                    ERROR_TABLE['population'].append(type_out)
                    ERROR_TABLE['PKL'].append(PKL_VALUE)
                    ERROR_TABLE['PARAM'].append(PARAM_VALUE)

    ERROR_TABLE2 = pd.DataFrame(ERROR_TABLE)
    error_save_i = 'Error_'+C_HET+'_'+T_HET+'.csv'
    error_save = os.path.join(args.validation_path, error_save_i)

    ERROR_TABLE2.to_csv(error_save)


