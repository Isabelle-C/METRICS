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
pd.set_option('display.max_rows', 5)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)

read_path = '/Users/cheni/Documents/LL/Data-Collect/'
save_path = '/Users/cheni/Documents/LL/Data-Collect2/'
save_path2 = '/Users/cheni/Documents/LL/Data-Collect3/'
save_path3 = '/Users/cheni/Documents/LL/Data-Collect3-cont/'
# save_path4 is defined in barplot saving
savepath5 = '/Users/cheni/Documents/LL/FIGS/TOTAL_COUNTS_CSV/'
savepath6 = '/Users/cheni/Documents/LL/FIGS/LINEPLOTS/'
savepath7 = '/Users/cheni/Documents/LL/FIGS/LINEPLOTS_CHET/'
savepath10 = '/Users/cheni/Documents/LL/FIGS/LINEPLOTS2_TM/'

#-- Define variables
pkl_list=[]
list_het = ['000', '010', '020', '030', '040']
seed_list = [0,1,2,3,4,5,6,7,8,9]
recomb = ['A', 'B', 'C', 'X', 'AB', 'AC', 'BC', 'XA', 'XB', 'XC', 'ABC', 'XAB', 'XAC', 'XBC', 'XABC']
list_in = ['A','B','C','X','AB','AC','BC','XA','XB','XC','ABC','XAB','XAC','XBC','XABC']
pop_list = [0, 1, 2, 3, 4]
type_list = [0, 1, 2, 3, 4, 5, 6]
time_list = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0,
             8.5, 9.0, 9.5, 10.0, 10.5, 11.0, 11.5, 12.0, 12.5, 13.0, 13.5, 14.0, 14.5, 15.0, 15.5,
             16.0, 16.5, 17.0, 17.5, 18.0, 18.5, 19.0, 19.5, 20.0, 20.5, 21.0, 21.5, 22.0]
count_type = ['total_A', 'total_B', 'total_C', 'total_X']
time_pick = [14.0]

#-- Forming pkl files for barplots
def dataframe_count(pkl_in, type_in, time_pick):
    select = pkl_in[[type_in, 'seed', 'C_HET', 'T_HET', 'populations','timepoint']]
    select2 = select.loc[select["timepoint"].isin(time_pick), :]
    select2.reset_index(drop=True, inplace=True)

    return select2

for type_in in count_type:
    for pop_selected in recomb:
        open_this = os.path.join(save_path, pop_selected + '_all.pkl')
        with open(open_this, 'rb') as d:
            count_pkl = pickle.load(d)

        select2 = dataframe_count(count_pkl, type_in, time_pick)
        print('Saving PKL File...')
        FILENAME_i = type_in + '_' + pop_selected
        FILENAME = os.path.join(save_path2, FILENAME_i)

        with open(FILENAME + '.pkl', 'wb') as f:
            pickle.dump(select2, f)

#-- Barplot with CHET on X-Axis ####
for type_in in count_type:
    if type_in == 'total_B':
        col_sec = '#d96777'
        list_in = ['B', 'AB', 'BC', 'XB', 'ABC', 'XAB', 'XBC', 'XABC']
    elif type_in == 'total_A':
        col_sec = '#78cfaa'
        list_in = ['A', 'AB', 'AC', 'XA', 'ABC', 'XAB', 'XAC', 'XABC']
    elif type_in == 'total_C':
        col_sec = '#b7d6e8'
        list_in = ['C', 'AC', 'BC', 'XC', 'ABC', 'XAC', 'XBC', 'XABC']
    elif type_in == 'total_X':
        col_sec = '#c1b9ae'
        list_in = ['X', 'XA', 'XB', 'XC', 'XAB', 'XAC', 'XBC', 'XABC']

    hold = type_in[6:]
    save_path4 = '/Users/cheni/Documents/LL/FIGS/' + type_in + '/'
    if not os.path.exists(save_path4):
        os.mkdir(save_path4)

    for pop_selected in list_in:
        print(pop_selected)
        FILENAME_i = type_in + '_' + pop_selected
        FILENAME = os.path.join(save_path2, FILENAME_i)
        select2 = pickle.load(open(FILENAME + '.pkl', 'rb'))

        from matplotlib import rcParams

        matplotlib.style.use('default')
        rcParams['figure.figsize'] = (14, 3)

        p = sns.barplot(data=select2,
                        x="C_HET", y=type_in, hue="T_HET",
                        ci="sd", palette=[col_sec])  # hue_order=order, , alpha=.6 kind = 'bar',
        print(len(p.patches))
        hatch = ['-'] * 5 + ['x'] * 5 + ['+'] * 5 + ['|'] * 5 + ['\\'] * 5  # ,
        for i, pa in enumerate(p.patches):
            pa.set_hatch(hatch[i])

        p = sns.swarmplot(x='C_HET', y=type_in, hue='T_HET',
                          data=select2, dodge=True, color='black')  # ,order=list_in
        p.legend_.remove()
        # p.legend(bbox_to_anchor=(1,0.8), fancybox=False, shadow=False, ncol=2, prop='Arial')
        p.set_title(hold + ' Total Counts' + ' - Simulation: ' + pop_selected + ', Timepoint: 14.0', fontname='Arial',
                    fontweight='bold', fontsize=12)
        p.set_xlabel('CHET', fontname='Arial', fontweight='bold', fontsize=12, labelpad=5)
        p.set_ylabel('Count', fontname='Arial', fontweight='bold', fontsize=12, labelpad=5)
        p.set_ylim(top=500)
        p.set_ylim(bottom=-50)
        plt.savefig(save_path4 + str(time_pick[0]) + '_' + pop_selected + '.pdf', bbox_inches='tight')
        plt.show
        print('Resetting...')
        plt.clf()

#-- Barplot with THET on X-Axis ####
for type_in in count_type:
    if type_in == 'total_B':
        col_sec = '#d96777'
        list_in = ['B', 'AB', 'BC', 'XB', 'ABC', 'XAB', 'XBC', 'XABC']
    elif type_in == 'total_A':
        col_sec = '#78cfaa'
        list_in = ['A', 'AB', 'AC', 'XA', 'ABC', 'XAB', 'XAC', 'XABC']
    elif type_in == 'total_C':
        col_sec = '#b7d6e8'
        list_in = ['C', 'AC', 'BC', 'XC', 'ABC', 'XAC', 'XBC', 'XABC']
    elif type_in == 'total_X':
        col_sec = '#c1b9ae'
        list_in = ['X', 'XA', 'XB', 'XC', 'XAB', 'XAC', 'XBC', 'XABC']

    hold = type_in[6:]

    save_path4 = '/Users/cheni/Documents/LL/FIGS/' + type_in + '_THETversion/'
    if not os.path.exists(save_path4):
        os.mkdir(save_path4)

    for pop_selected in list_in:
        print(pop_selected)
        FILENAME_i = type_in + '_' + pop_selected
        FILENAME = os.path.join(save_path2, FILENAME_i)
        select2 = pickle.load(open(FILENAME + '.pkl', 'rb'))

        from matplotlib import rcParams

        matplotlib.style.use('default')
        rcParams['figure.figsize'] = (14, 3)

        p = sns.barplot(data=select2,
                        x="T_HET", y=type_in, hue="C_HET",
                        ci="sd", palette=[col_sec])  # hue_order=order, , alpha=.6 kind = 'bar',
        print(len(p.patches))
        hatch = ['-'] * 5 + ['x'] * 5 + ['+'] * 5 + ['|'] * 5 + ['\\'] * 5  # ,
        for i, pa in enumerate(p.patches):
            pa.set_hatch(hatch[i])

        p = sns.swarmplot(x='T_HET', y=type_in, hue='C_HET',
                          data=select2, dodge=True, color='black')  # ,order=list_in
        p.legend_.remove()
        # p.legend(bbox_to_anchor=(1,0.8), fancybox=False, shadow=False, ncol=2, prop='Arial')
        p.set_title(hold + ' Total Counts' + ' - Simulation: ' + pop_selected + ', Timepoint: 14.0', fontname='Arial',
                    fontweight='bold', fontsize=12)
        p.set_xlabel('THET', fontname='Arial', fontweight='bold', fontsize=12, labelpad=5)
        p.set_ylabel('Count', fontname='Arial', fontweight='bold', fontsize=12, labelpad=5)
        p.set_ylim(top=500)
        p.set_ylim(bottom=-50)
        plt.savefig(save_path4 + str(time_pick[0]) + '_' + pop_selected + '.pdf', bbox_inches='tight')
        plt.show
        print('Resetting...')
        plt.clf()

#-- Average Lineplots ####
for pop_selected in recomb:
    open_this = os.path.join(save_path, pop_selected + '_all.pkl')
    with open(open_this, 'rb') as d:
        count_pkl = pickle.load(d)

    # -- Selecting the columns required
    select = count_pkl.loc[count_pkl["timepoint"].isin(time_pick), :]
    select2 = select[['total_A', 'total_B', 'total_C', 'total_X', 'seed', 'C_HET', 'T_HET', 'populations', 'timepoint']]

    POP_TABLE = []
    COUNT = []
    SEED_TABLE = []
    C_HET_TABLE = []
    T_HET_TABLE = []

    for T_HET_i in list_het:
        T = select2.loc[select['T_HET'] == T_HET_i, :]
        for C_HET_selected in list_het:
            TC = T.loc[T['C_HET'] == C_HET_selected, :]
            for seed_selected in seed_list:
                rows_of_interest = TC.loc[TC['seed'] == seed_selected, :]

                SUM = []
                for type_select in count_type:
                    SUM.append(rows_of_interest[type_select].values[0])
                sum_count = sum(SUM)

                POP_TABLE.append(pop_selected)
                COUNT.append(sum_count)
                SEED_TABLE.append(seed_selected)
                C_HET_TABLE.append(C_HET_selected)
                T_HET_TABLE.append(T_HET_i)

    final_df = {'populations': POP_TABLE, 'seed': SEED_TABLE, 'T_HET': T_HET_TABLE, 'C_HET': C_HET_TABLE,
                'total count': COUNT}
    # for x in final_df:
    #    print(str(x)+':'+str(len(final_df[x])))
    FIN_TOT = pd.DataFrame(final_df, columns=['populations', 'seed', 'T_HET', 'C_HET', 'total count'])

    # -- Obtaining the proportions
    POP_TABLE2 = []
    PROP = []
    SEED_TABLE2 = []
    C_HET_TABLE2 = []
    T_HET_TABLE2 = []
    TYPE = []

    for seed_selected in seed_list:
        # -- Selecting seed
        TOT_S = FIN_TOT.loc[FIN_TOT["seed"].isin([seed_selected]), :]
        select2_S = select2.loc[select2["seed"].isin([seed_selected]), :]
        for C_HET_selected in list_het:
            # -- Selecting CHET
            TOT_SC = TOT_S.loc[TOT_S["C_HET"].isin([C_HET_selected]), :]
            select2_SC = select2_S.loc[select2_S["C_HET"].isin([C_HET_selected]), :]
            for T_HET_i in list_het:
                # -- Selecting THET
                TOT_SCT = TOT_SC.loc[TOT_SC["T_HET"].isin([T_HET_i]), :]
                select2_SCT = select2_SC.loc[select2_SC["T_HET"].isin([T_HET_i]), :]

                for type_select in count_type:
                    prop = int(select2_SCT[type_select]) / int(TOT_SCT['total count'])
                    type_S = list(select2_SCT['populations'])[0]

                    POP_TABLE2.append(type_S)
                    PROP.append(prop)
                    SEED_TABLE2.append(seed_selected)
                    C_HET_TABLE2.append(C_HET_selected)
                    T_HET_TABLE2.append(T_HET_i)
                    TYPE.append(type_select)

    final_df = {'populations': POP_TABLE2, 'seed': SEED_TABLE2, 'THET': T_HET_TABLE2, 'CHET': C_HET_TABLE2,
                'count type': TYPE, 'proportions': PROP}
    # for x in final_df:
    #    print(str(x)+':'+str(len(final_df[x])))
    FIN_PROP = pd.DataFrame(final_df, columns=['populations', 'seed', 'THET', 'CHET', 'count type', 'proportions'])

    # -- Averging the seed proportions
    AV = []
    POP_TABLE3 = []
    T_HET_TABLE3 = []
    C_HET_TABLE3 = []
    TYPE2 = []

    for C_HET_selected in list_het:
        # -- Selecting CHET
        FIN_PROP_C = FIN_PROP.loc[FIN_PROP["CHET"].isin([C_HET_selected]), :]
        for T_HET_i in list_het:
            # -- Selecting THET
            FIN_PROP_CT = FIN_PROP_C.loc[FIN_PROP_C["THET"].isin([T_HET_i]), :]
            for type_select in count_type:
                FIN_PROP_CTT = FIN_PROP_CT.loc[FIN_PROP_CT["count type"].isin([type_select]), :]

                av = np.average(list(FIN_PROP_CTT['proportions']))
                ct = list(FIN_PROP_CTT['count type'])[0]
                type_S3 = list(FIN_PROP_CTT['populations'])[0]

                POP_TABLE3.append(type_S3)
                C_HET_TABLE3.append(C_HET_selected)
                T_HET_TABLE3.append(T_HET_i)
                TYPE2.append(ct)
                AV.append(av)

    final_df2 = {'populations': POP_TABLE3, 'THET': T_HET_TABLE3, 'CHET': C_HET_TABLE3, 'count_type': TYPE2,
                 'average_proportions': AV}
    # for x in final_df:
    #    print(str(x)+':'+str(len(final_df[x])))
    FIN_PROP2 = pd.DataFrame(final_df2, columns=['populations', 'THET', 'CHET', 'count_type', 'average_proportions'])

    # -- Creating figures

    # -- CHET on axis
    fig, axes = plt.subplots(5, 1, figsize=(6, 12), sharey=True)
    fig.suptitle('Population ' + pop_selected + ': Cancer Population Counts')
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=0.8)

    for HET_i in list_het:
        data_in2 = FIN_PROP2.loc[FIN_PROP2["THET"].isin([HET_i]), :]
        if HET_i == '000':
            num = 0
        elif HET_i == '010':
            num = 1
        elif HET_i == '020':
            num = 2
        elif HET_i == '030':
            num = 3
        elif HET_i == '040':
            num = 4

        # print(data_in2)
        sns.lineplot(ax=axes[num], data=data_in2, x="CHET", y="average_proportions", hue='count_type',
                     palette=['#78cfaa', '#d96777', '#b7d6e8', '#c1b9ae'])
        axes[num].set_title('THET: ' + HET_i)
        axes[num].legend(bbox_to_anchor=(1.25, 0.95), fancybox=False, shadow=False, ncol=1)
        axes[num].set_ylim(top=1.1)
        axes[num].set_ylim(bottom=0)
        # ax.Axes.get_legend(self=axes[num]).remove()
    plt.savefig(savepath6 + pop_selected + '.pdf', bbox_inches='tight')

    plt.clf()

    # -- THET on axis
    fig, axes = plt.subplots(5, 1, figsize=(6, 12), sharey=True)
    fig.suptitle('Population ' + pop_selected + ': Cancer Population Counts')
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=0.8)

    for HET_i in list_het:
        data_in2 = FIN_PROP2.loc[FIN_PROP2["CHET"].isin([HET_i]), :]
        if HET_i == '000':
            num = 0
        elif HET_i == '010':
            num = 1
        elif HET_i == '020':
            num = 2
        elif HET_i == '030':
            num = 3
        elif HET_i == '040':
            num = 4

        # print(data_in2)
        sns.lineplot(ax=axes[num], data=data_in2, x="THET", y="average_proportions", hue='count_type',
                     palette=['#78cfaa', '#d96777', '#b7d6e8', '#c1b9ae'])
        axes[num].set_title('CHET: ' + HET_i)
        axes[num].legend(bbox_to_anchor=(1.25, 0.95), fancybox=False, shadow=False, ncol=1)
        axes[num].set_ylim(top=1.1)
        axes[num].set_ylim(bottom=0)
        # ax.Axes.get_legend(self=axes[num]).remove()
    plt.savefig(savepath7 + pop_selected + '.pdf', bbox_inches='tight')

#-- Total Counts csv ####
for pop_selected in recomb:
    open_this = os.path.join(save_path, pop_selected + '_all.pkl')
    with open(open_this, 'rb') as d:
        count_pkl = pickle.load(d)

    #-- Selecting the columns required
    select = count_pkl[['total_A', 'total_B', 'total_C', 'total_X', 'seed', 'C_HET', 'T_HET', 'populations','timepoint']]

    select.to_csv(f"{savepath5}{pop_selected}.csv")

#-- Average Lineplots over Time ####

for pop_selected in recomb:
    print('--------------')
    print(pop_selected)
    open_this = os.path.join(save_path, pop_selected + '_all.pkl')
    with open(open_this, 'rb') as d:
        count_pkl = pickle.load(d)

    # -- Selecting the columns required

    print('Selecting the columns required...')
    select = count_pkl[
        ['total_A', 'total_B', 'total_C', 'total_X', 'seed', 'C_HET', 'T_HET', 'populations', 'timepoint']]

    print('Creating total table...')
    POP_TABLE = []
    COUNT = []
    SEED_TABLE = []
    C_HET_TABLE = []
    T_HET_TABLE = []
    TIME_TABLE = []
    for time_pick in time_list:
        select2 = select.loc[select["timepoint"].isin([time_pick]), :]
        for T_HET_i in list_het:
            T = select2.loc[select['T_HET'] == T_HET_i, :]
            for C_HET_selected in list_het:
                TC = T.loc[T['C_HET'] == C_HET_selected, :]
                for seed_selected in seed_list:
                    rows_of_interest = TC.loc[TC['seed'] == seed_selected, :]

                    SUM = []
                    for type_select in count_type:
                        SUM.append(rows_of_interest[type_select].values[0])
                    sum_count = sum(SUM)

                    POP_TABLE.append(pop_selected)
                    COUNT.append(sum_count)
                    SEED_TABLE.append(seed_selected)
                    C_HET_TABLE.append(C_HET_selected)
                    T_HET_TABLE.append(T_HET_i)
                    TIME_TABLE.append(time_pick)

    final_df = {'populations': POP_TABLE, 'seed': SEED_TABLE, 'T_HET': T_HET_TABLE, 'C_HET': C_HET_TABLE,
                'total count': COUNT, 'time': TIME_TABLE}
    # for x in final_df:
    #    print(str(x)+':'+str(len(final_df[x])))
    FIN_TOT = pd.DataFrame(final_df, columns=['populations', 'seed', 'T_HET', 'C_HET', 'total count', 'time'])

    # -- Obtaining the proportions
    print('Obtaining the proportions...')
    POP_TABLE2 = []
    PROP = []
    SEED_TABLE2 = []
    C_HET_TABLE2 = []
    T_HET_TABLE2 = []
    TYPE = []
    TIME_T = []

    for time_pick in time_list:
        FIN_TOT_T = FIN_TOT.loc[FIN_TOT["time"].isin([time_pick]), :]
        select2_T = select.loc[select["timepoint"].isin([time_pick]), :]
        for seed_selected in seed_list:
            # -- Selecting seed
            TOT_S = FIN_TOT_T.loc[FIN_TOT_T["seed"].isin([seed_selected]), :]
            select2_S = select2_T.loc[select2_T["seed"].isin([seed_selected]), :]
            for C_HET_selected in list_het:
                # -- Selecting CHET
                TOT_SC = TOT_S.loc[TOT_S["C_HET"].isin([C_HET_selected]), :]
                select2_SC = select2_S.loc[select2_S["C_HET"].isin([C_HET_selected]), :]
                for T_HET_i in list_het:
                    # -- Selecting THET
                    TOT_SCT = TOT_SC.loc[TOT_SC["T_HET"].isin([T_HET_i]), :]
                    select2_SCT = select2_SC.loc[select2_SC["T_HET"].isin([T_HET_i]), :]

                    for type_select in count_type:
                        try:
                            prop = int(select2_SCT[type_select]) / int(TOT_SCT['total count'])
                        except ZeroDivisionError:
                            prop = 0
                        type_S = list(select2_SCT['populations'])[0]

                        POP_TABLE2.append(type_S)
                        PROP.append(prop)
                        SEED_TABLE2.append(seed_selected)
                        C_HET_TABLE2.append(C_HET_selected)
                        T_HET_TABLE2.append(T_HET_i)
                        TYPE.append(type_select)
                        TIME_T.append(time_pick)

    final_df = {'populations': POP_TABLE2, 'seed': SEED_TABLE2, 'THET': T_HET_TABLE2, 'CHET': C_HET_TABLE2,
                'count type': TYPE, 'proportions': PROP, 'time': TIME_T}
    # for x in final_df:
    #    print(str(x)+':'+str(len(final_df[x])))
    FIN_PROP = pd.DataFrame(final_df,
                            columns=['populations', 'seed', 'THET', 'CHET', 'count type', 'proportions', 'time'])

    print('Averaging...')
    # -- Averging the seed proportions
    AV = []
    POP_TABLE3 = []
    T_HET_TABLE3 = []
    C_HET_TABLE3 = []
    TYPE2 = []
    TIME_T2 = []

    for time_pick in time_list:
        FIN_PROP_T = FIN_PROP.loc[FIN_PROP["time"].isin([time_pick]), :]
        for C_HET_selected in list_het:
            # -- Selecting CHET
            FIN_PROP_C = FIN_PROP_T.loc[FIN_PROP_T["CHET"].isin([C_HET_selected]), :]
            for T_HET_i in list_het:
                # -- Selecting THET
                FIN_PROP_CT = FIN_PROP_C.loc[FIN_PROP_C["THET"].isin([T_HET_i]), :]
                for type_select in count_type:
                    FIN_PROP_CTT = FIN_PROP_CT.loc[FIN_PROP_CT["count type"].isin([type_select]), :]

                    av = np.average(list(FIN_PROP_CTT['proportions']))
                    ct = list(FIN_PROP_CTT['count type'])[0]
                    type_S3 = list(FIN_PROP_CTT['populations'])[0]

                    POP_TABLE3.append(type_S3)
                    C_HET_TABLE3.append(C_HET_selected)
                    T_HET_TABLE3.append(T_HET_i)
                    TYPE2.append(ct)
                    AV.append(av)
                    TIME_T2.append(time_pick)
    final_df2 = {'populations': POP_TABLE3, 'THET': T_HET_TABLE3, 'CHET': C_HET_TABLE3, 'count_type': TYPE2,
                 'average_proportions': AV, 'time': TIME_T2}
    # for x in final_df:
    #    print(str(x)+':'+str(len(final_df[x])))
    FIN_PROP2 = pd.DataFrame(final_df2,
                             columns=['populations', 'THET', 'CHET', 'count_type', 'average_proportions', 'time'])

    print('Creating figures...')
    # -- Creating figures

    for T_HET_i in list_het:
        FIN_PROP3 = FIN_PROP2.loc[FIN_PROP2["populations"].isin([pop_selected]), :]
        data_in = FIN_PROP3.loc[FIN_PROP3["THET"].isin([T_HET_i]), :]

        fig, axes = plt.subplots(5, 1, figsize=(6, 12), sharey=True)
        fig.suptitle('Population ' + pop_selected + ': Cancer Population Counts Over t')
        plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=0.8)

        for HET_i in list_het:
            data_in2 = data_in.loc[data_in["CHET"].isin([HET_i]), :]
            if HET_i == '000':
                num = 0
            elif HET_i == '010':
                num = 1
            elif HET_i == '020':
                num = 2
            elif HET_i == '030':
                num = 3
            elif HET_i == '040':
                num = 4

            # print(data_in2)
            sns.lineplot(ax=axes[num], data=data_in2, x="time", y="average_proportions", hue='count_type',
                         palette=['#78cfaa', '#d96777', '#b7d6e8', '#c1b9ae'])
            axes[num].set_title('THET: ' + T_HET_i + ', CHET: ' + HET_i + '- Simulation: ' + pop_selected)
            axes[num].legend(bbox_to_anchor=(1.25, 0.95), fancybox=False, shadow=False, ncol=1)
            axes[num].set_ylim(top=1.1)
            axes[num].set_ylim(bottom=0)
        # ax.Axes.get_legend(self=axes[num]).remove()
        plt.savefig(savepath10 + pop_selected + '_T' + T_HET_i + '.pdf', bbox_inches='tight')
        plt.clf()
