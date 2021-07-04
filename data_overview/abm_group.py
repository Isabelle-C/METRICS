#-- Importing Packages ####
import ABM
from ABM import load_json
from abm_parse import load as ABM_load
from abm_parse import get_radius
import pickle
import argparse
from argparse import ArgumentParser

import pandas as pd
import os
import os.path
from os import path

import glob
import numpy as np
import itertools
import seaborn as sns

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.axes as ax

#-- Set viewing settings
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)



# -- Setup argument parser ####
parser = ArgumentParser(description="Collect evolution data into a pkl file.")
parser.add_argument(dest="read_path", help="Processed files directory.")
parser.add_argument(dest="save_path", help="Saving grouped files directory.")

args = parser.parse_args()


#-- Define variables
pkl_list=[]
list_het = ['000', '010', '020', '030', '040']
seed_list = [0,1,2,3,4,5,6,7,8,9]
recomb = ['A', 'B', 'C', 'X', 'AB', 'AC', 'BC', 'XA', 'XB', 'XC', 'ABC', 'XAB', 'XAC', 'XBC', 'XABC']
pop_list = [0, 1, 2, 3, 4]
type_list = [0, 1, 2, 3, 4, 5, 6]
time_list = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0,
             8.5, 9.0, 9.5, 10.0, 10.5, 11.0, 11.5, 12.0, 12.5, 13.0, 13.5, 14.0, 14.5, 15.0, 15.5,
             16.0, 16.5, 17.0, 17.5, 18.0, 18.5, 19.0, 19.5, 20.0, 20.5, 21.0, 21.5, 22.0]

def select_files_toread(recomb,pkl_list):
    '''
    Returns dictionary that contains the file name to load for each population recombination
    '''
    select_count_dict = {}
    select_cont_count_dict = {}
    for rec in recomb:
        select_count_dict[rec] = []
        select_cont_count_dict[rec] = []
    for pkl_i in pkl_list:
        for rec in recomb:
            if pkl_i[23:]==rec+'_collected.pkl':
                select_count_dict[rec].append(pkl_i)
            elif pkl_i[23:]==rec+'_cont_collected.pkl':
                select_cont_count_dict[rec].append(pkl_i)
    return select_count_dict, select_cont_count_dict

# -- Reading all the file in read path
os.chdir(args.read_path)
x = 0
for file in glob.glob("*.pkl"):
    object_i = glob.glob("*.pkl")[x]
    pkl_list.append(object_i)
    x += 1

select_dict, select_cont_count_dict = select_files_toread(recomb,pkl_list)

#-- Collecting the population counts information ####
for rec in recomb:
    print('--------------')
    print(rec)
    FILENAME_savei = rec + '_all'
    FILENAME_save = os.path.join(args.save_path, FILENAME_savei)
    if path.isfile(FILENAME_save + '.pkl') == True:
        print('File has been created in the previous run.')
    else:
        STORE = pd.DataFrame()
        for i in select_dict[rec]:
            FILENAME = os.path.join(args.read_path, i)
            with open(FILENAME, 'rb') as d:
                count_pkl = pickle.load(d)
            if STORE.empty == True:
                print('Adding first table')
                STORE = count_pkl
                print(STORE.head())
                print(len(STORE))
            else:
                print('Adding...')
                STORE = STORE.append(count_pkl,ignore_index=True)
                print(STORE.head())
                print(len(STORE))
        print('Saving PKL File...')

        with open(FILENAME + '.pkl', 'wb') as f:
            pickle.dump(STORE, f)

#-- Collecting the continuous properties information @ Specific Timepoint ####

for rec in recomb:
    print('--------------')
    print(rec)
    FILENAME_savei = rec + '_cont_14.0'
    FILENAME_save = os.path.join(save_path3, FILENAME_savei)
    if path.isfile(FILENAME_save + '.pkl') == True:
        print('File has been created in the previous run.')
    else:
        STORE = pd.DataFrame()
        for i in select_cont_count_dict[rec]:
            FILENAME = os.path.join(read_path, i)
            with open(FILENAME, 'rb') as d:
                cont_pkl = pickle.load(d)
                select_cont = cont_pkl.loc[cont_pkl["timepoint"].isin([14.0]), :]
                select_cont.reset_index(drop=True, inplace=True)
            if STORE.empty == True:
                print('Adding first table')
                STORE = select_cont
                #print(STORE.head())
                print(len(STORE))
            else:
                print('Adding...')
                STORE = STORE.append(select_cont,ignore_index=True)
                #print(STORE.head())
                print(len(STORE))
        print('Saving PKL File...')

        with open(FILENAME_save + '.pkl', 'wb') as f:
            pickle.dump(STORE, f)