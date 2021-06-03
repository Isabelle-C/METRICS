import ABM
import os
import os.path
from os import path
import pickle
import pandas as pd
from statsmodels.distributions.empirical_distribution import ECDF
from scipy.stats import hypergeom
from scipy.stats import ks_2samp
from scipy.stats import kstest
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from argparse import ArgumentParser
from abm_biopsy import make_dict as make_abm_biopsy_dict
from abm_biopsy import make_df as make_abm_biopsy_df

__author__ = "Alexis N. Prybutok"
__email__ = "aprybutok@u.northwestern.edu"

'''
BIOPSY_STAT takes a .pkl file of a dataframe containing all tumor and biopsy information or a list of
.pkl files containing dataframes each with subsets of the data and calculates relevant probabilities of
interest by comparing biopsies to tumors. The features of interest to be compared include:
    
    CELL LINES (X, A, B, C, H)
    CELL STATES (MIGRA, PROLI, QUIES, APOPT, NECRO)
    CYCLE LENGTH
    AVERAGE VOLUME
    CROWDING TOLERANCE
    METABOLIC PREFERENCE
    MIGRATORY THRESHOLD 

Usage: 

    python biopsy_stat BIOPSY_FILES TUMOR_FILES

    FILES
        Path to .pkl file or directory of .pkl files
    [--time TIME]
        Either single time point to use for both tumor and biopsies or comma-separated list of times for biopsy:tumor (default: 22)
    [--features]
        List of features to analyze (default: all)
    [--saveData SAVEDATA]
        Location of where to save resulting analysis data (default: data not saved) 
    [--saveFigs SAVEFIGS]
        Path designating where figures are saved (default: figures not saved)

Test Cases:
    XABC C:40 T:40
    A C:0 T:0
    AB C:10 T:30
'''

# -------------- PARSING AND INPUT/OUTPUT FUNCTIONS -------------

def get_parser():
    # Setup argument parser.
    parser = ArgumentParser(description="Receord all biopsy data into a dataframe")
    parser.add_argument(dest="files", help="Path to .pkl file or directory")
    parser.add_argument("--features", default="all", dest="features",
                        help="List of features to analyze (default: all)")
    parser.add_argument("--time", default="22", dest="time",
                        help="Either single time point to use for both tumor and biopsies or comma-separated times for biopsy,tumor (default: 22)")
    parser.add_argument("--saveData", default="", dest="saveData",
                        help="Location of where to save resulting analysis data (default: data not saved)")
    parser.add_argument("--saveFigs", default="", dest="saveFigs",
                        help="Path designating where figures are saved (default: figures not saved)")

    return parser

def get_pkl_files(arg):
    if arg[-1] == "/" or arg[-1] == "\\":
        return [arg + f for f in os.listdir(arg) if ABM.is_pkl(f)]
    else:
        assert ABM.is_pkl(arg)
        return [arg]

# -------------- MAKE EMPTY CONTAINERS -------------

def make_df():
    columns = ['TUMOR ID',
               'SEED',
               'HET %',
               'TISSUE HET %',
               'CELL LINES',
               'BIOP TIME',
               'TUMOR TIME',
               'BIOPSY TYPE',
               'BIOPSY NUMBER',
               'THICKNESS',
               'PROB FRAC POP X',
               'PROB FRAC POP A',
               'PROB FRAC POP B',
               'PROB FRAC POP C',
               'PROB FRAC APOPT',
               'PROB FRAC QUIES',
               'PROB FRAC MIGRA',
               'PROB FRAC PROLI',
               'PROB FRAC NECRO',
               'DIFF AVG CELL CYCLES',
               'DIFF CELL VOLUMES',
               'DIFF CROWDING TOLERANCE',
               'DIFF METABOLIC PREFERENCE',
               'DIFF MIGRATORY THRESHOLD'
               ]

    dataDF = pd.DataFrame(columns=columns)

    return dataDF

def make_dict():
    dataDict = {'TUMOR ID': None,
               'SEED': None,
               'HET %': None,
               'TISSUE HET %': None,
               'CELL LINES': None,
               'BIOPSY TIME': None,
               'TUMOR TIME': None,
               'BIOPSY TYPE': None,
               'BIOPSY NUMBER': None,
               'BIOPSY THICKNESS': None,
               'PROB FRAC POP X': None,
               'PROB FRAC POP A': None,
               'PROB FRAC POP B': None,
               'PROB FRAC POP C': None,
               'PROB FRAC APOPT': None,
               'PROB FRAC QUIES': None,
               'PROB FRAC MIGRA': None,
               'PROB FRAC PROLI': None,
               'PROB FRAC NECRO': None,
               'P-VALUE AVG CELL CYCLES': None,
               'P-VALUE CELL VOLUMES': None,
               'P-VALUE CROWDING TOLERANCE': None,
               'P-VALUE METABOLIC PREFERENCE': None,
               'P-VALUE MIGRATORY THRESHOLD': None
    }

    return dataDict

def path_create(path_needed):
    if not os.path.exists(path_needed):
        os.mkdir(path_needed)
# -------------- PROBABILITY CALCULATING FUNCTIONS -------------
def sum_tumor_replicates(replicatesDF):
    sumDict = make_abm_biopsy_dict()
    sumDF = make_abm_biopsy_df()

    groups = ['CANCER', 'HEALTHY']

    lines = ['X', 'A', 'B', 'C']
    states = ['APOPT', 'QUIES', 'MIGRA', 'PROLI', 'NECRO']
    features = ['AVG CELL CYCLES', 'CELL VOLUMES', 'CROWDING TOLERANCE', 'METABOLIC PREFERENCE', 'MIGRATORY THRESHOLD']

    # Initialize empty dictionary.
    for group in groups:
        sumDict[group] = 0

        for state in states:
            sumDict[state + ' ' + group] = 0

        for feature in features:
            sumDict[feature + ' ' + group] = []


    for line in lines:
        sumDict['POP ' + line] = 0

    i = 0

    # Sum all replicate data.
    for ind in replicatesDF.index:
        replicateDF = replicatesDF.iloc[ind]

        if i == 0:
            sumDict['TUMOR ID'] = replicateDF['TUMOR ID']
            sumDict['SEED'] = 'ALL'
            sumDict['HET %'] = replicateDF['HET %']
            sumDict['TISSUE HET %'] = replicateDF['TISSUE HET %']
            sumDict['CELL LINES'] = replicateDF['CELL LINES']
            sumDict['TIME'] = replicateDF['TIME']
            sumDict['BIOPSY TYPE'] = replicateDF['BIOPSY TYPE']
            sumDict['BIOPSY NUMBER'] = replicateDF['BIOPSY NUMBER']
            sumDict['THICKNESS'] = replicateDF['THICKNESS']

        for group in groups:
            sumDict[group] += replicateDF[group]

            for state in states:
                sumDict[state + ' ' + group] += replicateDF[state + ' ' + group]

            for feature in features:
                sumDict[feature + ' ' + group] += replicateDF[feature + ' ' + group]

        for line in lines:
            sumDict['POP ' + line] += replicateDF['POP ' + line]

        i += 1

    print(sumDict)
    # Add data to biopsy dataframe.
    sumDF = sumDF.append(sumDict, ignore_index=True)
    print(sumDF)

    return sumDF

def compare_discrete(tumorID, seed, file, biopsyDF, tumorDF, dataDict,pop_direct,cell_state_direct):
    '''
    Use of hypergeometric test, specifically hypergeom.pmf in scipy.stats package, to
    calculate the probability for the following:
    1. Per state per seed in each simulation 6*10
    2. Per population per seed in each simulation up to 4*10

    Definitions:
    1. pmf = Probability mass function: a function that gives the probability that
       a discrete random variable is exactly equal to some value
    2. Biopsy = only cancer cells
    3. Cancer = only cancer cells

    Returns the DataDict with probabilities as well as plotting figures.
    '''

    M = tumorDF['CANCER']   # -- total of the big pool

    lines = ['X', 'A', 'B', 'C']
    lines_prob = []
    for line in lines:
        pop = 'POP ' + line
        biopPop = biopsyDF[pop]  # -- the amount of target things picked
        tumorPop = tumorDF[pop]  # -- the amount of target things in the big pool
        biopTot = biopsyDF['CANCER']  # -- the number of things picked (i.e. # cells in biopsy)

        prob = hypergeom.pmf(biopPop, M, tumorPop, biopTot)
        lines_prob.append(prob)
        # hypergeom.pmf(k, M, n, N, loc)  where M = total of the big pool; N = the number of things picked (i.e. # cells in biopsy)
        #                             n = the amount of target things in the big pool; k = the amount of target things picked
        dataDict['PROB FRAC ' + pop] = prob

    states = ['APOPT', 'QUIES', 'MIGRA', 'PROLI', 'NECRO']
    states_prob = []
    for state in states:
        biopState = biopsyDF[state + ' CANCER'] # -- the amount of target things picked
        tumorState = tumorDF[state + ' CANCER'] # -- the amount of target things in the big pool
        biopsyTot = biopsyDF['CANCER'] # -- the number of things picked (i.e. # cells in biopsy)

        prob = hypergeom.pmf(biopState, M, tumorState, biopsyTot)
        dataDict['PROB FRAC ' + state] = prob
        states_prob.append(prob)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(lines, lines_prob, 'bo')
    ax.vlines(lines, 0, lines_prob, lw=2)

    ax.set_xlabel('Populations')
    ax.set_ylabel('Probability')
    plt.title(f"{file[35:-4]}, {tumorID}, S{str(int(seed))}")

    FILENAME_fig = f"{file[35:-4]}_{tumorID}_S{seed}_POPULATIONS.svg"
    FILENAME_FIG = os.path.join(pop_direct, FILENAME_fig)
    if args.saveFigs != "":
        plt.savefig(FILENAME_FIG, bbox_inches='tight')

    plt.clf()
    plt.close()

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(states, states_prob, 'bo')
    ax.vlines(states, 0, states_prob, lw=2)
    ax.set_xlabel('Cell States')
    ax.set_ylabel('Probability')
    plt.title(f"{file[35:-4]}, {tumorID}, S{str(int(seed))}")


    FILENAME_fig = f"{file[35:-4]}_{tumorID}_S{seed}_CELL_STATES.svg"
    FILENAME_FIG = os.path.join(cell_state_direct, FILENAME_fig)

    if args.saveFigs != "":
        plt.savefig(FILENAME_FIG, bbox_inches='tight')

    plt.clf()
    plt.close()
    return dataDict

def CDF_plot(tumorFeat,feature,tumorID,seed,tumorCDF,simul_direct):

    subfolder_direct = os.path.join(simul_direct,f"CDF_{feature}/")
    path_create(subfolder_direct)

    FILENAME_fig = f"CDF_{feature}_{tumorID}_S{seed}.svg"
    FILENAME_FIG = os.path.join(subfolder_direct, FILENAME_fig)

    if path.isfile(FILENAME_FIG) == True:
        print('File has been created in the previous run.')
    else:
        min_value = min(tumorFeat)
        max_value = max(tumorFeat)
        if min_value != max_value:
            n_of_steps = (max_value-min_value)/999
            x_steps = list(np.arange(start=min_value, stop=max_value, step=n_of_steps))
            y_output = list(tumorCDF(x_steps))

            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.plot(x_steps, y_output, 'bo')

            ax.set_xlabel('Values')
            ax.set_ylabel('Percentage')
            plt.title(f"CDF: {feature}, {tumorID}, S{str(int(seed))}")

            if args.saveFigs != "":
                plt.savefig(FILENAME_FIG, bbox_inches='tight')
            plt.clf()
            plt.close()

def compare_continuous(tumorID, seed, file, biopsyDF, tumorDF, dataDict,simul_direct,cont_p_direct):
    '''
    Continuous: per param per seed (KS test)

    The Kolmogorov–Smirnov statistic quantifies a distance between the
    empirical distribution function of the sample and the cumulative distribution
    function of the reference distribution,
    or between the empirical distribution functions of two samples.

    '''
    features = ['AVG CELL CYCLES', 'CELL VOLUMES', 'CROWDING TOLERANCE', 'METABOLIC PREFERENCE', 'MIGRATORY THRESHOLD']
    features_p_values = []

    for feature in features:
        biopFeat = biopsyDF[feature + ' CANCER']
        tumorFeat = tumorDF[feature + ' CANCER']

        tumorCDF = ECDF(tumorFeat) #-- Cumulative distribution function
        CDF_plot(tumorFeat,feature,tumorID,seed,tumorCDF,simul_direct) #-- Plot the CDF files for tumor.

              #kstest(rvs, cdf)
        pval = kstest(biopFeat, tumorCDF)
        # rvs: If an array, it should be a 1-D array of observations of random variables
        # cdf: If array_like, it should be a 1-D array of observations of random variables, and the two-sample test is performed (and rvs must be array_like)

        dataDict['P-VALUE ' + feature] = pval[1]
        features_p_values.append(pval[1])

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(features, features_p_values, 'bo')
    ax.vlines(features, 0, features_p_values, lw=2)
    ax.set_xlabel('Continuous Properties')
    ax.set_ylabel('P Value')

    plt.title(f"{file[35:-4]}, {tumorID}, S{str(int(seed))}")

    FILENAME_fig = f"{file[35:-4]}_{tumorID}_S{seed}_CONTINUOUS_PROPERTIES.svg"
    FILENAME_FIG = os.path.join(cont_p_direct, FILENAME_fig)

    if args.saveFigs != "":
        plt.savefig(FILENAME_FIG, bbox_inches='tight')
    plt.clf()
    plt.close()

    return dataDict

def compare(file,biopsiesDF, tumorsDF, dataDF,sample_direct):

    tumorDF = make_abm_biopsy_df()
    prevTumorID = ''

    for ind in biopsiesDF.index:
        dataDict = make_dict()

        tumorID = biopsiesDF['TUMOR ID'][ind]

        if tumorID == 'VIVO_HET_GRAPH_040_040_XABC' or tumorID == 'VIVO_HET_GRAPH_000_000_A' or tumorID == 'VIVO_HET_GRAPH_010_030_AB':
            seed = biopsiesDF['SEED'][ind]
            if tumorID != prevTumorID:
                tumorDF = tumorsDF.loc[tumorsDF['TUMOR ID'] == tumorID]
                tumorDF = tumorDF.reset_index(drop=True)
                tumorDF = sum_tumor_replicates(tumorDF) # Sum tumor data
                tumorDF = tumorDF.iloc[0] # CHECK THIS
                prevTumorID = tumorID

                #-- Create specific directory for saving the figures
                simul_direct = os.path.join(sample_direct, f"{tumorID}/")
                path_create(simul_direct)

                cont_p_direct = os.path.join(simul_direct, "CONTINUOUS_PROPERTIES/")
                path_create(cont_p_direct)

                cell_state_direct = os.path.join(simul_direct, "CELL_STATE_PROB/")
                path_create(cell_state_direct)

                pop_direct = os.path.join(simul_direct, "POPULATION_PROB/")
                path_create(pop_direct)

            biopsyDF = biopsiesDF.iloc[ind]
            dataDict['TUMOR ID'] = tumorID
            dataDict['SEED'] = seed
            dataDict['HET %'] = biopsyDF['HET %']
            dataDict['TISSUE HET%'] = biopsyDF['TISSUE HET %']
            dataDict['CELL LINES'] = biopsyDF['CELL LINES']
            dataDict['BIOPSY TIME'] = biopsyDF['TIME']
            dataDict['TUMOR TIME'] = tumorDF['TIME']
            dataDict['BIOPSY TYPE'] = biopsyDF['BIOPSY TYPE']
            dataDict['BIOPSY NUMBER'] = biopsyDF['BIOPSY NUMBER']
            dataDict['BIOPSY THICKNESS'] = biopsyDF['THICKNESS']

            dataDict = compare_discrete(tumorID, seed, file, biopsyDF, tumorDF, dataDict, pop_direct, cell_state_direct)
            dataDict = compare_continuous(tumorID, seed, file, biopsyDF, tumorDF, dataDict, simul_direct, cont_p_direct)

            dataDF = dataDF.append(dataDict, ignore_index=True)

    return dataDF

# -------------------- MAIN FUNCTION --------------------------

if __name__ == "__main__":

    parser = get_parser()
    args = parser.parse_args()

    # Make empty dataframes
    dataDF = make_df()

    if "," in args.time:
        dsplit = str(args.time).split(':')
        TIME = [float(d) for d in str(args.time).split(',')]
    else:
        TIME = [float(args.time), float(args.time)]

    timeString = "B" + str(TIME[0]) + "vT" + str(TIME[1])

    # Get files
    files = get_pkl_files(args.files)
    biopsy_files = files

    tumorFiles = []
    # Isolate tumor information

    for file in files:
        if 'TUMORS' in file:
            tumorFiles.append(file)
            biopsy_files.remove(file)
    #tumorsDF = pd.concat([pickle.load(open(f, "rb")) for f in tumorFiles])

    tumorsDF=pd.DataFrame()

    for f in tumorFiles:
        with open(f, 'rb') as file_opened:
            if tumorsDF.empty==True:
                tumorsDF = pd.read_pickle(file_opened, compression=None)
            else:
                add_file =  pd.read_pickle(file_opened, compression=None)
                tumorsDF = tumorsDF.append(add_file, ignore_index=True)


    # If didn't find single tumor file.
    if tumorFiles == []:
        for file in files:
            if 'BIOPSIES.pkl' in file:
                with open(file, 'rb') as d:
                    DF = pd.read_pickle(d, compression=None)
                tumorsDF = DF.loc[DF['BIOPSY TYPE'] == 'TUMOR']

    tumorsDF = tumorsDF.loc[tumorsDF['TIME'] == TIME[1]]

    for file in biopsy_files:
        if 'THICKNESS_7' in file:
            if 'NEEDLE' in file or 'PUNCH' in file:
                with open(file, 'rb') as d:
                    biopsiesDF = pd.read_pickle(d, compression=None)
            if 'BIOPSIES.pkl' in file:
                with open(file, 'rb') as d:
                    biopsiesDF = pd.read_pickle(d, compression=None)
                biopsiesDF = biopsiesDF.loc[DF['BIOPSY TYPE'] != 'TUMOR']

            biopsiesDF = biopsiesDF.loc[tumorsDF['TIME'] == TIME[0]]

            pd.set_option('display.max_rows', None)
            pd.set_option('display.max_columns', None)
            pd.set_option('display.width', None)
            pd.set_option('display.max_colwidth', -1)

            sample_direct = os.path.join(args.saveFigs, f"{file[35:-4]}/")
            path_create(sample_direct)

            dataDF = compare(file,biopsiesDF, tumorsDF, dataDF, sample_direct)

        print('Saving PKL File...')
        FILENAME_i = f"{file[35:-4]}_ANALYZED"
        FILENAME = os.path.join(args.saveData, FILENAME_i)

        with open(FILENAME + '.pkl', 'wb') as f:
            pickle.dump(dataDF, f)



