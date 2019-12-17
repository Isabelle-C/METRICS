import ABM
import os
import pickle
import pandas as pd
from scipy.stats import hypergeom
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from argparse import ArgumentParser

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

    python biopsy_stat FILES

    FILES
        Path to .pkl file or directory of .pkl files
    [--time TIME]
        Either single time point to use for both tumor and biopsies or comma-separated times for biopsy:tumor (default: 22)
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
                        help="Day to record data from (default: 22)")
    parser.add_argument("--time", default="22", dest="time",
                        help="Either single time point to use for both tumor and biopsies or comma-separated times for biopsy:tumor (default: 22)")
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
               'BIOP TIME': None,
               'TUMOR TIME': None,
               'BIOPSY TYPE': None,
               'BIOPSY NUMBER': None,
               'THICKNESS': None,
               'PROB FRAC POP X': None,
               'PROB FRAC POP A': None,
               'PROB FRAC POP B': None,
               'PROB FRAC POP C': None,
               'PROB FRAC APOPT': None,
               'PROB FRAC QUIES': None,
               'PROB FRAC MIGRA': None,
               'PROB FRAC PROLI': None,
               'PROB FRAC NECRO': None,
               'DIFF AVG CELL CYCLES': None,
               'DIFF CELL VOLUMES': None,
               'DIFF CROWDING TOLERANCE': None,
               'DIFF METABOLIC PREFERENCE': None,
               'DIFF MIGRATORY THRESHOLD': None
    }

    return dataDF

# -------------- PROBABILITY CALCULATING FUNCTIONS -------------

def compare_discrete(biopsyDF, tumorDF, dataDict):

    N = tumorDF['CANCER']

    lines = ['X', 'A', 'B', 'C']
    for line in lines:
        pop = 'POP ' + line
        prob = hypergeom.pmf(biopsyDF[pop], N, tumorDF[pop], biopsyDF['TOTAL'])
        dataDict['PROB FRAC ' + pop] = prob

    states = ['APOPT', 'QUIES', 'MIGRA', 'PROLI', 'NECRO']
    for state in states:
        prob = hypergeom.pmf(biopsyDF[state + ' TOTAL'], N, tumorDF[state + ' CANCER'], biopsyDF['TOTAL'])
        dataDict['PROB FRAC ' + state] = prob

    return dataDF


def compare_continuous(biopsyDF, tumorDF, dataDict):

    N = tumorDF['CANCER']

    features = ['AVG CELL CYCLES', 'CELL VOLUMES', 'CROWDING TOLERANCE', 'METABOLIC PREFERENCE', 'MIGRATORY THRESHOLD']



    return dataDF

def compare(biopsiesDF, tumorsDF):
    dataDF = make_df()

    for ind in biopsiesDF.index:
        dataDict = make_dict()

        tumorID = biopsiesDF['TUMOR ID'][ind]
        seed = biopsiesDF['SEED'][ind]
        tumorDF = tumorsDF.loc['TUMOR ID' == tumorID]
        tumorDF = tumorDF.loc['SEED' == seed]
        biopsyDF = biopsiesDF.iloc[ind]

        dataDict['TUMOR ID'] = tumorID
        dataDict['SEED'] = seed
        dataDict['HET %'] = biopsyDF['HET %']
        dataDict['TISSUE HET%'] = biopsyDF['TISSUE HET %']
        dataDict['CELL LINES'] = biopsyDF['CELL LINES']
        dataDict['BIOP TIME'] = biopsyDF['TIME']
        dataDict['TUMOR TIME'] = biopsyDF['TIME']

        dataDict = compare_discrete(biopsyDF, tumorDF, dataDict)

        dataDF = dataDF.append(dataDict)

    return dataDF

# -------------------- MAIN FUNCTION --------------------------

if __name__ == "__main__":

    parser = get_parser()
    args = parser.parse_args()

    # Make empty dataframes
    biopsiesDF = pd.DataFrame()
    tumorsDF = pd.DataFrame()

    if "," in args.time:
        dsplit = str(args.time).split(':')
        TIME = [float(d) for d in str(args.time).split(',')]
    else:
        TIME = [float(args.time), float(args.time)]

    # Get files
    files = get_pkl_files(args.files)
    for file in files:
        if 'NEEDLE' in file or 'PUNCH' in file:
            DF = pickle.load(open(file, "rb"))
            biopsiesDF.append(DF, ignore_index=True)
        if 'TUMORS' in file:
            DF = pickle.load(open(file, "rb"))
            tumorsDF.append(DF, ignore_index=True)
        if 'BIOPSIES.pkl' in file:
            DF = pickle.load(open(file, "rb"))

            tumorsDF = DF.loc[DF['BIOPSY TYPE'] == 'TUMOR']
            biopsiesDF = DF.loc[DF['BIOPSY TYPE'] != 'TUMOR']

    tumorsDF = tumorsDF.loc[tumorsDF['TIME'] == TIME[1]]
    biopsiesDF = biopsiesDF.loc[tumorsDF['TIME'] == TIME[0]]

    dataDF = compare(biopsiesDF, tumorsDF)
