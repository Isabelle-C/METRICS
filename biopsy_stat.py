import ABM
import os
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

# -------------- PROBABILITY CALCULATING FUNCTIONS -------------
def sum_tumor_replicates(replicatesDF):
    sumDict = make_abm_biopsy_dict()
    sumDF = make_abm_biopsy_df()

    groups = ['CANCER', 'HEALTHY', 'TOTAL']

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

def compare_discrete(biopsyDF, tumorDF, dataDict):

    N = tumorDF['CANCER']

    lines = ['X', 'A', 'B', 'C']
    for line in lines:
        pop = 'POP ' + line
        biopPop = biopsyDF[pop]
        tumorPop = tumorDF[pop]
        biopTot = biopsyDF['CANCER']
        # TO DO: DECIDE IF THIS SHOULD BE COMPARE BIOP CANCER TO TUMOR CANCER OR BIOP TOTAL TO TUMOR TOTAL
        prob = hypergeom.pmf(biopsyDF[pop], N, tumorDF[pop], biopsyDF['CANCER'])
        dataDict['PROB FRAC ' + pop] = prob

    states = ['APOPT', 'QUIES', 'MIGRA', 'PROLI', 'NECRO']
    for state in states:
        biopState = biopsyDF[state + ' CANCER'] + biopsyDF[state + ' HEALTHY']
        tumorState = tumorDF[state + ' CANCER']
        biopsyTot = biopsyDF['CANCER'] + biopsyDF['HEALTHY']
        # TO DO: DECIDE IF THIS SHOULD BE COMPARE BIOP CANCER TO TUMOR CANCER OR BIOP TOTAL TO TUMOR TOTAL
        prob = hypergeom.pmf(biopState, N, tumorState, biopsyTot)
        dataDict['PROB FRAC ' + state] = prob

    return dataDict


def compare_continuous(biopsyDF, tumorDF, dataDict):

    features = ['AVG CELL CYCLES', 'CELL VOLUMES', 'CROWDING TOLERANCE', 'METABOLIC PREFERENCE', 'MIGRATORY THRESHOLD']

    for feature in features:
        biopFeat = biopsyDF[feature + ' CANCER'] + [feature + ' HEALTHY']
        tumorFeat = tumorDF[feature + ' CANCER']
        tumorCDF = ECDF(tumorFeat)
        pval = kstest(biopFeat, tumorCDF)
        print(pval[1])
        dataDict['P-VALUE ' + feature] = pval[1]

    return dataDict

def compare(biopsiesDF, tumorsDF, dataDF):

    tumorDF = make_abm_biopsy_df()
    prevTumorID = ''

    for ind in biopsiesDF.index:
        dataDict = make_dict()

        tumorID = biopsiesDF['TUMOR ID'][ind]
        seed = biopsiesDF['SEED'][ind]

        if tumorID != prevTumorID:

            # Sum tumor data
            tumorDF = tumorsDF.loc[tumorsDF['TUMOR ID'] == tumorID]
            tumorDF = sum_tumor_replicates(tumorDF)
            tumorDF = tumorDF.iloc[0] # CHECK THIS
            prevTumorID = tumorID

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

        dataDict = compare_discrete(biopsyDF, tumorDF, dataDict)
        dataDict = compare_continuous(biopsyDF, tumorDF, dataDict)

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

    tumorFiles = []
    # Isolate tumor information
    for file in files:
        if 'TUMORS' in file:
            tumorFiles.append(file)
    tumorsDF = pd.concat([pickle.load(open(f, "rb")) for f in tumorFiles])

    # If didn't find single tumor file.
    if tumorFiles == []:
        for file in files:
            if 'BIOPSIES.pkl' in file:
                DF = pickle.load(open(file, "rb"))

                tumorsDF = DF.loc[DF['BIOPSY TYPE'] == 'TUMOR']

    tumorsDF = tumorsDF.loc[tumorsDF['TIME'] == TIME[1]]

    for file in files:
        if 'NEEDLE' in file or 'PUNCH' in file:
            biopsiesDF = pickle.load(open(file, "rb"))
        if 'BIOPSIES.pkl' in file:
            DF = pickle.load(open(file, "rb"))
            biopsiesDF = DF.loc[DF['BIOPSY TYPE'] != 'TUMOR']

        biopsiesDF = biopsiesDF.loc[tumorsDF['TIME'] == TIME[0]]

        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', -1)

        dataDF = compare(biopsiesDF, tumorsDF, dataDF)

    # pickle.dump(dataDF, open(args.saveData + "BIOPSIES_ANALYZED_" + timeString + ".pkl", "wb"))
