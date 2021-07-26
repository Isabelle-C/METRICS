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

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.axes as ax

#-- Set viewing settings
pd.set_option('display.max_rows', 30)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)

def path_create(path_needed):
    if not os.path.exists(path_needed):
        os.mkdir(path_needed)

read_path = '/Users/cheni/Documents/LL/Data-Collect/'
save_path = '/Users/cheni/Documents/LL/Data-Collect2/'
save_path2 = '/Users/cheni/Documents/LL/Data-Collect3/'
save_path3 = '/Users/cheni/Documents/LL/Data-Collect3-cont/'
# save_path4 is defined in barplot saving
savepath5 = '/Users/cheni/Documents/LL/FIGS/TOTAL_COUNTS_CSV/'
savepath6 = '/Users/cheni/Documents/LL/FIGS/LINEPLOTS/'
savepath7 = '/Users/cheni/Documents/LL/FIGS/LINEPLOTS_CHET/'
savepath8 = '/Users/cheni/Documents/LL/FIGS/CONT_PROPERTIES/'
savepath10 = '/Users/cheni/Documents/LL/FIGS/LINEPLOTS2_TM/'


all_v = ['X_Cycle','A_Cycle','B_Cycle','C_Cycle','H_Cycle','X_Volume','A_Volume','B_Volume','C_Volume','H_Volume',
 'X_NECRO_FRAC','X_SENES_FRAC','X_ENERGY_THRESHOLD','X_MAX_HEIGHT','X_ACCURACY','X_AFFINITY','X_DEATH_AGE_AVG',
 'X_DIVISION_POTENTIAL','X_META_PREF','X_MIGRA_THRESHOLD','A_NECRO_FRAC','A_SENES_FRAC','A_ENERGY_THRESHOLD',
 'A_MAX_HEIGHT','A_ACCURACY','A_AFFINITY','A_DEATH_AGE_AVG','A_DIVISION_POTENTIAL','A_META_PREF',
 'A_MIGRA_THRESHOLD','B_NECRO_FRAC','B_SENES_FRAC','B_ENERGY_THRESHOLD','B_MAX_HEIGHT','B_ACCURACY',
 'B_AFFINITY','B_DEATH_AGE_AVG','B_DIVISION_POTENTIAL','B_META_PREF','B_MIGRA_THRESHOLD','C_NECRO_FRAC',
 'C_SENES_FRAC','C_ENERGY_THRESHOLD','C_MAX_HEIGHT','C_ACCURACY','C_AFFINITY','C_DEATH_AGE_AVG',
 'C_DIVISION_POTENTIAL','C_META_PREF','C_MIGRA_THRESHOLD','H_NECRO_FRAC','H_SENES_FRAC','H_ENERGY_THRESHOLD',
 'H_MAX_HEIGHT','H_ACCURACY','H_AFFINITY','H_DEATH_AGE_AVG','H_DIVISION_POTENTIAL','H_META_PREF',
 'H_MIGRA_THRESHOLD']
list_in = ['A','B','C','X','AB','AC','BC','XA','XB','XC','ABC','XAB','XAC','XBC','XABC']

all_v_updated = []
for v in all_v:
    if 'Volume' in v:
        all_v_updated.append(v)
    elif 'Cycle' in v:
        all_v_updated.append(v)
    elif 'META_PREF' in v:
        all_v_updated.append(v)
    elif 'MAX_HEIGHT' in v:
        all_v_updated.append(v)
    elif 'MIGRA_THRESHOLD'in v:
        all_v_updated.append(v)
    else:
        print('Eliminating '+v+' ...')

# -- Reading all the file in read path
pkl_list = []
os.chdir(save_path3)
x = 0
for file in glob.glob("*.pkl"):
    object_i = glob.glob("*.pkl")[x]
    pkl_list.append(object_i)
    x += 1

STORE = pd.DataFrame()
for pkl_i in pkl_list:
    FILENAME_save = os.path.join(save_path3, pkl_i)
    with open(FILENAME_save, 'rb') as d:
        cont_pkl = pickle.load(d)

    if STORE.empty == True:
        print('Adding first table')
        STORE = cont_pkl
        #print(STORE.head())
        print(len(STORE))
    else:
        print('Adding...')
        STORE = STORE.append(cont_pkl,ignore_index=True)
        #print(STORE.head())
        print(len(STORE))

CONT_DATA_MAX = []
CONT_DATA_MIN = []
POP_FIN = []
SEED_FIN = []
T_HET_FIN = []
C_HET_FIN = []
TYPE_LIST = []


for cont_v in all_v_updated:
    a = STORE[[cont_v, 'populations', 'seed',
                                    'T_HET', 'C_HET']]
    for i in range(len(a[cont_v])):
        if len(a[cont_v][i]) == 0:
            CONT_DATA_MAX.append(0)
            CONT_DATA_MIN.append(0)
            TYPE_LIST.append(cont_v)
            POP_FIN.append(a['populations'][i])
            SEED_FIN.append(int(a['seed'][i]))
            T_HET_FIN.append(a['T_HET'][i])
            C_HET_FIN.append(a['C_HET'][i])
        else:
            CONT_DATA_MAX.append(float(max(a[cont_v][i])))
            CONT_DATA_MIN.append(float(min(a[cont_v][i])))
            TYPE_LIST.append(cont_v)
            POP_FIN.append(a['populations'][i])
            SEED_FIN.append(int(a['seed'][i]))
            T_HET_FIN.append(a['T_HET'][i])
            C_HET_FIN.append(a['C_HET'][i])


print('Assemble the table')
final_df = {
    'Type': TYPE_LIST,
    'Max': CONT_DATA_MAX,
    'Min': CONT_DATA_MIN,
    'populations': POP_FIN,
    'seed': SEED_FIN,
    'THET': T_HET_FIN,
    'CHET': C_HET_FIN}
# for x in final_df:
#    print(str(x)+':'+str(len(final_df[x])))

ALL = pd.DataFrame(final_df, columns=['Type', 'Max', 'Min', 'populations', 'seed', 'THET', 'CHET'])

TYPE2 = []
FIN_MAX = []
FIN_MIN = []

for cont_v in all_v_updated:
    TYPE2.append(cont_v)
    new_ALL = ALL.loc[ALL['Type'] == cont_v, :]
    MAX_list = list(new_ALL['Max'])
    MIN_list = list(new_ALL['Min'])
    FIN_MAX.append(float(max(MAX_list)))
    FIN_MIN.append(float(min(MIN_list)))

final_df_ALL = {
'Type':TYPE2,
'Max': FIN_MAX,
'Min': FIN_MIN}

ALL2 = pd.DataFrame(final_df_ALL,columns = ['Type','Max','Min'])
#ALL2 = pd.read_csv('/Users/cheni/Desktop/ALL2.csv')

from matplotlib import transforms
from matplotlib.transforms import Bbox

xx = 73
# mpl.rcParams['font.size']=50

for rec in recomb:
    FILENAME_savei = rec + '_cont_14.0.pkl'
    FILENAME_save = os.path.join(save_path3, FILENAME_savei)

    with open(FILENAME_save, 'rb') as d:
        a = pickle.load(d)

    for cont_v in all_v_updated:
        for i in range(len(rec + 'H')):
            new = rec + 'H'
            if new[i] + '_' == cont_v[:2]:
                keep = ALL2.loc[ALL2['Type'] == cont_v, :]
                yupper_bound = list(keep['Max'])[0] * 1.5
                ylower_bound = list(keep['Min'])[0] * 0.5

                if ylower_bound == 0 and 'Volume' in cont_v:
                    ylower_bound = -3
                elif 'Cycle' in cont_v:
                    ylower_bound = -3
                elif 'MAX_HEIGHT' in cont_v and cont_v != 'H_MAX_HEIGHT':
                    ylower_bound = -65
                elif 'META_PREF' in cont_v:
                    yupper_bound = list(keep['Max'])[0] * 1.7
                    ylower_bound = -1
                elif 'H_MAX_HEIGHT' in cont_v:
                    ylower_bound = 0
                elif 'MIGRA_THRESHOLD' in cont_v:
                    yupper_bound = list(keep['Max'])[0] * 1.5
                    ylower_bound = -11

                CONT_DATA = []
                POP_FIN = []
                SEED_FIN = []
                T_HET_FIN = []
                C_HET_FIN = []
                for i in range(len(a[cont_v])):
                    if len(a[cont_v][i]) == 0:
                        CONT_DATA.append(0)
                        POP_FIN.append(a['populations'][i])
                        SEED_FIN.append(int(a['seed'][i]))
                        T_HET_FIN.append(a['T_HET'][i])
                        C_HET_FIN.append(a['C_HET'][i])
                    else:
                        for ii in range(len(a[cont_v][i])):
                            CONT_DATA.append(float(a[cont_v][i][ii]))
                            POP_FIN.append(a['populations'][i])
                            SEED_FIN.append(int(a['seed'][i]))
                            T_HET_FIN.append(a['T_HET'][i])
                            C_HET_FIN.append(a['C_HET'][i])

                print('Assemble the table')
                final_df = {cont_v: CONT_DATA,
                            'populations': POP_FIN,
                            'seed': SEED_FIN,
                            'THET': T_HET_FIN,
                            'CHET': C_HET_FIN}

                TOT = pd.DataFrame(final_df, columns=[cont_v, 'populations', 'seed', 'THET', 'CHET'])
                print('Making the figure of ' + cont_v)

                for T_HET_i in list_het:
                    fin_path = savepath8 + T_HET_i + '_' + cont_v + '_' + rec + '.pdf'

                    if path.isfile(fin_path) == True:
                        print('File has been created in the previous run.')
                    else:
                        TOT_new = TOT.loc[TOT['THET'] == T_HET_i]
                        # matplotlib.style.use('default')
                        # rcParams['figure.figsize'] = (,)
                        figBinding = plt.figure(figsize=(80, 5))
                        ax = figBinding.add_subplot(1, 1, 1)

                        ax = sns.violinplot(x="CHET", y=cont_v, data=TOT_new, hue='seed',
                                            order=list_het, hue_order=seed_list)
                        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10, prop='Arial')
                        plt.title(cont_v + '- THET:' + T_HET_i + ', Simulation' + rec, fontsize=35, fontname='Arial',
                                  fontweight='bold')
                        plt.ylabel(cont_v, fontname='Arial', fontweight='bold', fontsize=25, labelpad=5)
                        plt.xlabel("CHET", fontname='Arial', fontweight='bold', fontsize=25, labelpad=5)
                        plt.ylim(top=yupper_bound)
                        plt.ylim(bottom=ylower_bound)
                        plt.savefig(savepath8 + T_HET_i + '_' + cont_v + '_' + rec + '.pdf',
                                    bbox_inches=Bbox([[8, 0], [xx, 5]]))

                        print('Resetting...')
                        plt.clf()
