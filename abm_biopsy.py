import ABM
from abm_parse import load as ABM_load
import os
import re
import pickle
import pandas as pd
import numpy as np
from itertools import combinations
from argparse import ArgumentParser

__author__ = "Alexis N. Prybutok"
__email__ = "aprybutok@u.northwestern.edu"

'''
ABM_BIOPSY takes a directory of (or a single) parsed ABM file (.pkl), performs each type of 
biopsy on the tumor, and creates a list of each biopsy, with it's associated measured features and 
a record of the tumor it came from. It will also take all associated measurements for the full tumor. 
It will extract all data into dataframe biopsies in the form:

    TUMOR ID | SEED |  HET % | TISSUE HET % | CELL LINES | TIME | BIOPSY TYPE | THICKNESS | FEATURES |   

where

    TUMOR ID = FILE NAME
    SEED = SEED (0-10)
    HET % = {0, 10, 20, 30, 40}
    TISSUE HET % = {0, 10, 20, 30, 40}
    CELL LINES = all possible combinations of {X, A, B, C}
    TIME = Day of biopsy {15, 22}
    BIOPSY TYPE = {PUNCH, NEEDLE, TUMOR}
    THICNKESS = RADIUS/WIDTH of biopsy (1-34)

and FEATURES (for which one column exists for each feature) includes

    CANCER                          int
    HEALTHY                         int
    TOTAL                           int
    POP X                           int
    POP A                           int
    POP B                           int
    POP C                           int
    APOPT (TYPE 1) CANCER           int
    APOPT (TYPE 1) HEALTHY          int
    APOPT (TYPE 1) TOTAL            int
    QUIES (TYPE 2) CANCER           int
    QUIES (TYPE 2) HEALTHY          int
    QUIES (TYPE 2) TOTAL            int
    MIGRA (TYPE 3) CANCER           int
    MIGRA (TYPE 3) HEALTHY          int
    MIGRA (TYPE 3) TOTAL            int
    PROLI (TYPE 4) CANCER           int
    PROLI (TYPE 4) HEALTHY          int
    PROLI (TYPE 4) TOTAL            int
    NECRO (TYPE 6) CANCER           int
    NECRO (TYPE 6) HEALTHY          int
    NECRO (TYPE 6) TOTAL            int
    AVG CELL CYCLES CANCER          list<double>
    AVG CELL CYCLES HEALTHY         list<double>
    AVG CELL CYCLES TOTAL           list<double>
    CELL VOLUMES CANCER             list<double>
    CELL VOLUMES HEALTHY            list<double>
    CELL VOLUMES TOTAL              list<double>
    CROWDING TOLERANCE CANCER       list<double>
    CROWDING TOLERANCE HEALTHY      list<double>
    CROWDING TOLERANCE TOTAL        list<double>
    METABOLIC PREFERENCE CANCER     list<double>
    METABOLIC PREFERENCE HEALTHY    list<double>
    METABOLIC PREFERENCE TOTAL      list<double>
    MIGRATORY THRESHOLD CANCER      list<double>
    MIGRATORY THRESHOLD HEALTHY     list<double>
    MIGRATORY THRESHOLD TOTAL       list<double>
    
Usage: 

    python abm_biopsy.py FILES [--time TIME] [--type TYPE] [--samples SAMPLES] 
        [--thickness THICKNESS] [--saveLoc] [--sampleMapsLoc] [--saveTogether]

    FILES
        Path to .pkl file or directory
    [--param PARAM]
        Path to PARAM .json file or directory
    [--time TIME]
        Comma-separated, hyphen-separated range, or min:interval:max of days to record data from (default: 15,22)
    [--type TYPE]
        Comma-separated list of sample types to take (punch, needle, and/or tumor) (default: punch,needle,tumor)
    [--samples SAMPLES]
        Comma-separated, hyphen-separated range, or min:interval:max of samples to take for punch (max 7) and needle (max 6) biopsies; min 1, max 7 (default: 1-7)
    [--thickness THICKNESS]
        Comma-separated, hyphen-separated range, or min:interval:max of thicknesses to measure; min 1, max 34 (default: 0-34)
    [--combos]
        Flag indicating whether or not to do all combos of given samples
    [--saveLoc]
        Location of where to save results
    [--sampleMapsLoc]
        Location of where to find sampleMaps.pkl file
    [--saveTogether]
        Save all data in one dataframe in one pkl, else saves a file per biopsy type broken by day and number of samples


'''


# -------------- PARSING AND INPUT/OUTPUT FUNCTIONS -------------

def get_parser():
    # Setup argument parser.
    parser = ArgumentParser(description="Receord all biopsy data into a dataframe")
    parser.add_argument(dest="files", help="Path to .pkl file or directory")
    parser.add_argument("--param", default="", dest="param", help="Path to PARM .json file or directory")
    parser.add_argument("--time", default="15,22", dest="time",
                        help="Comma-separated list of days to record data from or min:interval:max (default: 15,22)")
    parser.add_argument("--type", default="punch,needle,tumor", dest="type",
                        help="Comma-separated list of sample types to take (punch, needle, and/or tumor) (default: punch,needle,tumor)")
    parser.add_argument("--samples", default="1-7", dest="samples",
                        help="Comma-separated list or hyphen-separated range of samples to take for punch (max 7) and needle (max 6) biopsies; min 1, max 7 (default: 1-7)")
    parser.add_argument("--thickness", default="1-34", dest="thickness",
                        help="Comma-separated list or hyphen-separated range of thicknesses to measure; min 0, max 34")
    parser.add_argument("--combos", default=False, dest="combos", action="store_true",
                        help="Flag indicating whether or not to do all combos of given samples")
    parser.add_argument("--saveLoc", default='./', dest="saveLoc",
                        help="Location of where to save file, default will save here")
    parser.add_argument("--sampleMapsLoc", default='./', dest="sampleMapsLoc",
                        help="Location of where to find sampleMaps pickle, default will search here")
    parser.add_argument("--saveTogether", default=False, dest="saveTogether", action="store_true",
                        help="Save all data in one dataframe in one pkl, else saves a file per biopsy type broken by day and number of samples")

    return parser

# Function: get_pkl_files
# Author: Andrea Collins
# If arg is a directory, returns a list of all the files in that
# directory that are pkl files. If arg is a single file, checks
# if that file is a pkl file and if it is, returns that filename.
def get_pkl_files(arg):
    if arg[-1] == "/" or arg[-1] == "\\":
        return [arg + f for f in os.listdir(arg) if ABM.is_pkl(f)]
    else:
        assert ABM.is_pkl(arg)
        return [arg]

def get_json_files(arg):
    if arg[-1] == "/" or arg[-1] == "\\":
        return [arg + f for f in os.listdir(arg) if ABM.is_json(f)]
    else:
        assert ABM.is_json(arg)
        return [arg]



# ---------------- MAKE EMPTY CONTAINERS ---------------------

def make_df():
    columns = ['TUMOR ID',
               'SEED',
               'HET %',
               'TISSUE HET %',
               'CELL LINES',
               'TIME',
               'BIOPSY TYPE',
               'BIOPSY NUMBER',
               'THICKNESS',
               'CANCER',
               'HEALTHY',
               'TOTAL',
               'POP X',
               'POP A',
               'POP B',
               'POP C',
               'APOPT CANCER',
               'APOPT HEALTHY',
               'APOPT TOTAL',
               'QUIES CANCER',
               'QUIES HEALTHY',
               'QUIES TOTAL',
               'MIGRA CANCER',
               'MIGRA HEALTHY',
               'MIGRA TOTAL',
               'PROLI CANCER',
               'PROLI HEALTHY',
               'PROLI TOTAL',
               'NECRO CANCER',
               'NECRO HEALTHY',
               'NECRO TOTAL',
               'AVG CELL CYCLES CANCER',
               'AVG CELL CYCLES HEALTHY',
               'AVG CELL CYCLES TOTAL',
               'CELL VOLUMES CANCER',
               'CELL VOLUMES HEALTHY',
               'CELL VOLUMES TOTAL',
               'CROWDING TOLERANCE CANCER',
               'CROWDING TOLERANCE HEALTHY',
               'CROWDING TOLERANCE TOTAL',
               'METABOLIC PREFERENCE CANCER',
               'METABOLIC PREFERENCE HEALTHY',
               'METABOLIC PREFERENCE TOTAL',
               'MIGRATORY THRESHOLD CANCER',
               'MIGRATORY THRESHOLD HEALTHY',
               'MIGRATORY THRESHOLD TOTAL'
    ]
    biopsiesDF = pd.DataFrame(columns=columns)

    return biopsiesDF

def make_dict():
    biopsiesDict = {'TUMOR ID': None,
                    'SEED': None,
                    'HET %': None,
                    'TISSUE HET %': None,
                    'CELL LINES': None,
                    'TIME': None,
                    'BIOPSY TYPE': None,
                    'BIOPSY NUMBER': None,
                    'THICKNESS': None,
                    'CANCER': None,
                    'HEALTHY': None,
                    'TOTAL': None,
                    'POP X':  None,
                    'POP A': None,
                    'POP B': None,
                    'POP C': None,
                    'APOPT CANCER': None,
                    'APOPT HEALTHY': None,
                    'APOPT TOTAL': None,
                    'QUIES CANCER': None,
                    'QUIES HEALTHY': None,
                    'QUIES TOTAL': None,
                    'MIGRA CANCER': None,
                    'MIGRA HEALTHY': None,
                    'MIGRA TOTAL': None,
                    'PROLI CANCER': None,
                    'PROLI HEALTHY': None,
                    'PROLI TOTAL': None,
                    'NECRO CANCER': None,
                    'NECRO HEALTHY': None,
                    'NECRO TOTAL': None,
                    'AVG CELL CYCLES CANCER': None,
                    'AVG CELL CYCLES HEALTHY': None,
                    'AVG CELL CYCLES TOTAL': None,
                    'CELL VOLUMES CANCER': None,
                    'CELL VOLUMES HEALTHY': None,
                    'CELL VOLUMES TOTAL': None,
                    'CROWDING TOLERANCE CANCER': None,
                    'CROWDING TOLERANCE HEALTHY': None,
                    'CROWDING TOLERANCE TOTAL': None,
                    'METABOLIC PREFERENCE CANCER': None,
                    'METABOLIC PREFERENCE HEALTHY': None,
                    'METABOLIC PREFERENCE TOTAL': None,
                    'MIGRATORY THRESHOLD CANCER': None,
                    'MIGRATORY THRESHOLD HEALTHY': None,
                    'MIGRATORY THRESHOLD TOTAL': None
    }

    return biopsiesDict

# ---------------------- GET TUMOR ---------------------------

def parse_tumor(f, PARAM, SEED, TIME, agents, tumorDF, C):

    # Parse file name
    fileName = re.sub('.*VIVO', 'VIVO', f)
    TUMORID = fileName.replace('.pkl', '')
    fsplit = str(TUMORID).split('_')
    HET = int(fsplit[-3])
    TISSUEHET = int(fsplit[-2])
    CELLLINES = fsplit[-1]

    # Record full tumor information
    tumorDict = make_dict()
    tumorDict['TUMOR ID'] = TUMORID
    tumorDict['SEED'] = SEED
    tumorDict['HET %'] = HET - 100
    tumorDict['TISSUE HET %'] = TISSUEHET - 100
    tumorDict['CELL LINES'] = CELLLINES
    tumorDict['TIME'] = TIME / 2
    tumorDict['BIOPSY TYPE'] = 'TUMOR'

    tumorDict = get_tumor(agents, PARAM, TIME, tumorDict, C)
    tumorDF = tumorDF.append(tumorDict, ignore_index=True)

    return tumorDF

def get_tumor(agents, PARAM, TIME, tumorDict, C):

    CANCERPOPS = [0, 1, 2, 3]

    # Initiate empty lists
    COUNTS = [0, 0, 0]  # CANCER, HEALTHY, TOTAL
    POPS = [0, 0, 0, 0, 0]  # X, A, B, C, HEALTHY
    TYPES = [[0, 0, 0, 0, 0, 0, 0],  # CANCER
             [0, 0, 0, 0, 0, 0, 0],  # HEALTHY
             [0, 0, 0, 0, 0, 0, 0]]  # TOTAL
    CYCLES = [[], [], []]   # CANCER, HEALTHY, TOTAL
    VOLUMES = [[], [], []]  # CANCER, HEALTHY, TOTAL
    CROWDINGTOLERANCE = [[], [], []]    # CANCER, HEALTHY, TOTAL
    METAPREF = [[], [], []]             # CANCER, HEALTHY, TOTAL
    MIGRATHRESHOLD = [[], [], []]       # CANCER, HEALTHY, TOTAL

    # Iterate through locations and collect all data if
    # there is a cancer cell in that location at all
    for loc in range(len(agents)):
        UVW = C[loc]
        index = None
        if len(set(agents[loc]['pop']) & set(CANCERPOPS)) > 0:
            for p in range(0, 6):
                if agents[loc]['pop'][p] != -1:
                    COUNTS[2] += 1
                    POPS[agents[loc]['pop'][p]] += 1
                    TYPES[2][agents[loc]['type'][p]] += 1

                    if agents[loc]['cycle'][p] != -1:
                        CYCLES[2].append(agents[loc]['cycle'][p])
                    VOLUMES[2].append(agents[loc]['volume'][p])

                    # Parse PARAM json and make sure grabbing the right cell information
                    if loc < len(PARAM['timepoints'][TIME]['cells']) and UVW + [0] == PARAM['timepoints'][TIME]['cells'][loc][0]:
                        for i in range(len(PARAM['timepoints'][TIME]['cells'][loc][1])):
                            if PARAM['timepoints'][TIME]['cells'][loc][1][i][3] == p:
                                CROWDINGTOLERANCE[2].append(PARAM['timepoints'][TIME]['cells'][loc][1][i][4][3])
                                METAPREF[2].append(PARAM['timepoints'][TIME]['cells'][loc][1][i][4][8])
                                MIGRATHRESHOLD[2].append(PARAM['timepoints'][TIME]['cells'][loc][1][i][4][9])
                                break

                    else:
                        for t in range(0, len(PARAM['timepoints'][TIME]['cells'])):
                            if UVW + [0] == PARAM['timepoints'][TIME]['cells'][t][0]:
                                index = t
                                for i in range(len(PARAM['timepoints'][TIME]['cells'][index][1])):
                                    if PARAM['timepoints'][TIME]['cells'][index][1][i][3] == p:
                                        pos = i
                                        CROWDINGTOLERANCE[2].append(PARAM['timepoints'][TIME]['cells'][index][1][pos][4][3])
                                        METAPREF[2].append(PARAM['timepoints'][TIME]['cells'][index][1][pos][4][8])
                                        MIGRATHRESHOLD[2].append(PARAM['timepoints'][TIME]['cells'][index][1][pos][4][9])
                                        break
                                break

                    if agents[loc]['pop'][p] == 4:
                        COUNTS[1] += 1
                        TYPES[1][agents[loc]['type'][p]] += 1
                        if agents[loc]['cycle'][p] != -1:
                            CYCLES[1].append(agents[loc]['cycle'][p])
                        VOLUMES[1].append(agents[loc]['volume'][p])

                        # Parse PARAM json and make sure grabbing the right cell information
                        if loc < len(PARAM['timepoints'][TIME]['cells']) and UVW + [0] == PARAM['timepoints'][TIME]['cells'][loc][0]:
                            CROWDINGTOLERANCE[1].append(PARAM['timepoints'][TIME]['cells'][loc][1][pos][4][3])
                            METAPREF[1].append(PARAM['timepoints'][TIME]['cells'][loc][1][pos][4][8])
                            MIGRATHRESHOLD[1].append(PARAM['timepoints'][TIME]['cells'][loc][1][pos][4][9])

                        else:
                            CROWDINGTOLERANCE[1].append(PARAM['timepoints'][TIME]['cells'][index][1][pos][4][3])
                            METAPREF[1].append(PARAM['timepoints'][TIME]['cells'][index][1][pos][4][8])
                            MIGRATHRESHOLD[1].append(PARAM['timepoints'][TIME]['cells'][index][1][pos][4][9])

                    else:
                        COUNTS[0] += 1
                        TYPES[0][agents[loc]['type'][p]] += 1
                        if agents[loc]['cycle'][p] != -1:
                            CYCLES[0].append(agents[loc]['cycle'][p])
                        VOLUMES[0].append(agents[loc]['volume'][p])

                        # Parse PARAM json and make sure grabbing the right cell information
                        if loc < len(PARAM['timepoints'][TIME]['cells']) and UVW + [0] == PARAM['timepoints'][TIME]['cells'][loc][0]:
                            CROWDINGTOLERANCE[0].append(PARAM['timepoints'][TIME]['cells'][loc][1][pos][4][3])
                            METAPREF[0].append(PARAM['timepoints'][TIME]['cells'][loc][1][pos][4][8])
                            MIGRATHRESHOLD[0].append(PARAM['timepoints'][TIME]['cells'][loc][1][pos][4][9])

                        else:
                            CROWDINGTOLERANCE[0].append(PARAM['timepoints'][TIME]['cells'][index][1][pos][4][3])
                            METAPREF[0].append(PARAM['timepoints'][TIME]['cells'][index][1][pos][4][8])
                            MIGRATHRESHOLD[0].append(PARAM['timepoints'][TIME]['cells'][index][1][pos][4][9])

    # Store data in biopsiesDict
    tumorDict['CANCER'] = COUNTS[0]
    tumorDict['HEALTHY'] = COUNTS[1]
    tumorDict['TOTAL'] = COUNTS[2]
    tumorDict['POP X'] = POPS[0]
    tumorDict['POP A'] = POPS[1]
    tumorDict['POP B'] = POPS[2]
    tumorDict['POP C'] = POPS[3]
    tumorDict['APOPT CANCER'] = TYPES[0][1]
    tumorDict['APOPT HEALTHY'] = TYPES[1][1]
    tumorDict['APOPT TOTAL'] = TYPES[2][1]
    tumorDict['QUIES CANCER'] = TYPES[0][2]
    tumorDict['QUIES HEALTHY'] = TYPES[1][2]
    tumorDict['QUIES TOTAL'] = TYPES[2][2]
    tumorDict['MIGRA CANCER'] = TYPES[0][3]
    tumorDict['MIGRA HEALTHY'] = TYPES[1][3]
    tumorDict['MIGRA TOTAL'] = TYPES[2][3]
    tumorDict['PROLI CANCER'] = TYPES[0][4]
    tumorDict['PROLI HEALTHY'] = TYPES[1][4]
    tumorDict['PROLI TOTAL'] = TYPES[2][4]
    tumorDict['NECRO CANCER'] = TYPES[0][6]
    tumorDict['NECRO HEALTHY'] = TYPES[1][6]
    tumorDict['NECRO TOTAL'] = TYPES[2][6]
    tumorDict['AVG CELL CYCLES CANCER'] = CYCLES[0]
    tumorDict['AVG CELL CYCLES HEALTHY'] = CYCLES[1]
    tumorDict['AVG CELL CYCLES TOTAL'] = CYCLES[2]
    tumorDict['CELL VOLUMES CANCER'] = VOLUMES[0]
    tumorDict['CELL VOLUMES HEALTHY'] = VOLUMES[1]
    tumorDict['CELL VOLUMES TOTAL'] = VOLUMES[2]
    tumorDict['CROWDING TOLERANCE CANCER'] = CROWDINGTOLERANCE[0]
    tumorDict['CROWDING TOLERANCE HEALTHY'] = CROWDINGTOLERANCE[1]
    tumorDict['CROWDING TOLERANCE TOTAL'] = CROWDINGTOLERANCE[2]
    tumorDict['METABOLIC PREFERENCE CANCER'] = METAPREF[0]
    tumorDict['METABOLIC PREFERENCE HEALTHY'] = METAPREF[1]
    tumorDict['METABOLIC PREFERENCE TOTAL'] = METAPREF[2]
    tumorDict['MIGRATORY THRESHOLD CANCER'] = MIGRATHRESHOLD[0]
    tumorDict['MIGRATORY THRESHOLD HEALTHY'] = MIGRATHRESHOLD[1]
    tumorDict['MIGRATORY THRESHOLD TOTAL'] = MIGRATHRESHOLD[2]

    return tumorDict



# ------------------ TAKE SINGLE BIOPSY -----------------------

def take_biopsy(agents, PARAM, TIME, sampleMap, biopsiesDict):

    # Initiate empty lists
    COUNTS = [0, 0, 0]  # CANCER, HEALTHY, TOTAL
    POPS = [0, 0, 0, 0, 0]  # X, A, B, C, HEALTHY
    TYPES = [ [0, 0, 0, 0, 0, 0, 0],    # CANCER
              [0, 0, 0, 0, 0, 0, 0],    # HEALTHY
              [0, 0, 0, 0, 0, 0, 0] ]   # TOTAL
    CYCLES = [[], [], []]   # CANCER, HEALTHY, TOTAL
    VOLUMES = [[], [], []]  # CANCER, HEALTHY, TOTAL
    CROWDINGTOLERANCE = [[], [], []]    # CANCER, HEALTHY, TOTAL
    METAPREF = [[], [], []]             # CANCER, HEALTHY, TOTAL
    MIGRATHRESHOLD = [[], [], []]       # CANCER, HEALTHY, TOTAL

    # Itterate through locations and collect all data
    for loc in sampleMap:
        UVW = list(loc[0])
        index = None
        for p in range(0,6):
            pos = None
            # Collect information for all cells regardless of type
            if agents[loc[1]]['pop'][p] != -1:
                COUNTS[2] += 1
                POPS[agents[loc[1]]['pop'][p]] += 1
                TYPES[2][agents[loc[1]]['type'][p]] += 1

                if agents[loc[1]]['cycle'][p] != -1:
                    CYCLES[2].append(agents[loc[1]]['cycle'][p])

                VOLUMES[2].append(agents[loc[1]]['volume'][p])

                # Parse PARAM json and make sure grabbing the right cell information
                if loc[1] < len(PARAM['timepoints'][TIME]['cells']) and UVW + [0] == PARAM['timepoints'][TIME]['cells'][loc[1]][0]:
                    for i in range(len(PARAM['timepoints'][TIME]['cells'][loc[1]][1])):
                        if PARAM['timepoints'][TIME]['cells'][loc[1]][1][i][3] == p:
                            pos = i
                            CROWDINGTOLERANCE[2].append(PARAM['timepoints'][TIME]['cells'][loc[1]][1][pos][4][3])
                            METAPREF[2].append(PARAM['timepoints'][TIME]['cells'][loc[1]][1][pos][4][8])
                            MIGRATHRESHOLD[2].append(PARAM['timepoints'][TIME]['cells'][loc[1]][1][pos][4][9])
                            break

                else:
                    for t in range(0, len(PARAM['timepoints'][TIME]['cells'])):
                        if list(loc[0]) + [0] == PARAM['timepoints'][TIME]['cells'][t][0]:
                            index = t
                            for i in range(len(PARAM['timepoints'][TIME]['cells'][index][1])):
                                if PARAM['timepoints'][TIME]['cells'][index][1][i][3] == p:
                                    pos = i
                                    CROWDINGTOLERANCE[2].append(PARAM['timepoints'][TIME]['cells'][index][1][pos][4][3])
                                    METAPREF[2].append(PARAM['timepoints'][TIME]['cells'][index][1][pos][4][8])
                                    MIGRATHRESHOLD[2].append(PARAM['timepoints'][TIME]['cells'][index][1][pos][4][9])
                                    break
                            break

                # Sort by healthy vs cancer
                if agents[loc[1]]['pop'][p] == 4:
                    COUNTS[1] += 1
                    TYPES[1][agents[loc[1]]['type'][p]] += 1
                    if agents[loc[1]]['cycle'][p] != -1:
                        CYCLES[1].append(agents[loc[1]]['cycle'][p])
                    VOLUMES[1].append(agents[loc[1]]['volume'][p])

                    # Parse PARAM json and make sure grabbing the right cell information
                    if loc[1] < len(PARAM['timepoints'][TIME]['cells']) and UVW + [0] == PARAM['timepoints'][TIME]['cells'][loc[1]][0]:
                        CROWDINGTOLERANCE[1].append(PARAM['timepoints'][TIME]['cells'][loc[1]][1][pos][4][3])
                        METAPREF[1].append(PARAM['timepoints'][TIME]['cells'][loc[1]][1][pos][4][8])
                        MIGRATHRESHOLD[1].append(PARAM['timepoints'][TIME]['cells'][loc[1]][1][pos][4][9])

                    else:
                        CROWDINGTOLERANCE[1].append(PARAM['timepoints'][TIME]['cells'][index][1][pos][4][3])
                        METAPREF[1].append(PARAM['timepoints'][TIME]['cells'][index][1][pos][4][8])
                        MIGRATHRESHOLD[1].append(PARAM['timepoints'][TIME]['cells'][index][1][pos][4][9])

                else:
                    COUNTS[0] += 1
                    TYPES[0][agents[loc[1]]['type'][p]] += 1
                    if agents[loc[1]]['cycle'][p] != -1:
                        CYCLES[0].append(agents[loc[1]]['cycle'][p])
                    VOLUMES[0].append(agents[loc[1]]['volume'][p])

                    # Parse PARAM json and make sure grabbing the right cell information
                    if loc[1] < len(PARAM['timepoints'][TIME]['cells']) and UVW + [0] == PARAM['timepoints'][TIME]['cells'][loc[1]][0]:
                        CROWDINGTOLERANCE[0].append(PARAM['timepoints'][TIME]['cells'][loc[1]][1][pos][4][3])
                        METAPREF[0].append(PARAM['timepoints'][TIME]['cells'][loc[1]][1][pos][4][8])
                        MIGRATHRESHOLD[0].append(PARAM['timepoints'][TIME]['cells'][loc[1]][1][pos][4][9])

                    else:
                        CROWDINGTOLERANCE[0].append(PARAM['timepoints'][TIME]['cells'][index][1][pos][4][3])
                        METAPREF[0].append(PARAM['timepoints'][TIME]['cells'][index][1][pos][4][8])
                        MIGRATHRESHOLD[0].append(PARAM['timepoints'][TIME]['cells'][index][1][pos][4][9])

    # Store data in biopsiesDict
    biopsiesDict['CANCER'] = COUNTS[0]
    biopsiesDict['HEALTHY'] = COUNTS[1]
    biopsiesDict['TOTAL'] = COUNTS[2]
    biopsiesDict['POP X'] = POPS[0]
    biopsiesDict['POP A'] = POPS[1]
    biopsiesDict['POP B'] = POPS[2]
    biopsiesDict['POP C'] = POPS[3]
    biopsiesDict['APOPT CANCER'] = TYPES[0][1]
    biopsiesDict['APOPT HEALTHY'] = TYPES[1][1]
    biopsiesDict['APOPT TOTAL'] = TYPES[2][1]
    biopsiesDict['QUIES CANCER'] = TYPES[0][2]
    biopsiesDict['QUIES HEALTHY'] = TYPES[1][2]
    biopsiesDict['QUIES TOTAL'] = TYPES[2][2]
    biopsiesDict['MIGRA CANCER'] = TYPES[0][3]
    biopsiesDict['MIGRA HEALTHY'] = TYPES[1][3]
    biopsiesDict['MIGRA TOTAL'] = TYPES[2][3]
    biopsiesDict['PROLI CANCER'] = TYPES[0][4]
    biopsiesDict['PROLI HEALTHY'] = TYPES[1][4]
    biopsiesDict['PROLI TOTAL'] = TYPES[2][4]
    biopsiesDict['NECRO CANCER'] = TYPES[0][6]
    biopsiesDict['NECRO HEALTHY'] = TYPES[1][6]
    biopsiesDict['NECRO TOTAL'] = TYPES[2][6]
    biopsiesDict['AVG CELL CYCLES CANCER'] = CYCLES[0]
    biopsiesDict['AVG CELL CYCLES HEALTHY'] = CYCLES[1]
    biopsiesDict['AVG CELL CYCLES TOTAL'] = CYCLES[2]
    biopsiesDict['CELL VOLUMES CANCER'] = VOLUMES[0]
    biopsiesDict['CELL VOLUMES HEALTHY'] = VOLUMES[1]
    biopsiesDict['CELL VOLUMES TOTAL'] = VOLUMES[2]
    biopsiesDict['CROWDING TOLERANCE CANCER'] = CROWDINGTOLERANCE[0]
    biopsiesDict['CROWDING TOLERANCE HEALTHY'] = CROWDINGTOLERANCE[1]
    biopsiesDict['CROWDING TOLERANCE TOTAL'] = CROWDINGTOLERANCE[2]
    biopsiesDict['METABOLIC PREFERENCE CANCER'] = METAPREF[0]
    biopsiesDict['METABOLIC PREFERENCE HEALTHY'] = METAPREF[1]
    biopsiesDict['METABOLIC PREFERENCE TOTAL'] = METAPREF[2]
    biopsiesDict['MIGRATORY THRESHOLD CANCER'] = MIGRATHRESHOLD[0]
    biopsiesDict['MIGRATORY THRESHOLD HEALTHY'] = MIGRATHRESHOLD[1]
    biopsiesDict['MIGRATORY THRESHOLD TOTAL'] = MIGRATHRESHOLD[2]

    return biopsiesDict

# ---------- TAKE ALL BIOPSIES FOR A GIVEN SEED ----------------

def take_biopsies(f, PARAM, SEED, TIME, agents, sampleMaps, biopsiesDF, TYPE, SAMPLES, THICKNESS, SAVETOGETHER, SAVELOC):

    # Parse file name
    fileName = re.sub('.*VIVO', 'VIVO', f)
    TUMORID = fileName.replace('.pkl', '')
    fsplit = str(TUMORID).split('_')
    HET = int(fsplit[-3])
    TISSUEHET = int(fsplit[-2])
    CELLLINES = fsplit[-1]

    # Make lists for biopsies
    for type in TYPE:
        if type == 'needle' or type == 'punch':
            for n in SAMPLES:

                if not SAVETOGETHER:
                    biopsiesDF = pickle.load(open(SAVELOC + "BIOPSIES_" + str(type).upper() + "_DAY_" +
                                                  str(int(TIME/2)) + "_SAMPLES_" + str(n) + ".pkl", "rb"))

                for thickness in THICKNESS:
                    if '7' in str(n) and type == 'needle':
                        continue
                    else:
                        # Set up empty dictionary to eventually be added to the DF
                        biopsiesDict = make_dict()
                        biopsiesDict['TUMOR ID'] = TUMORID
                        biopsiesDict['SEED'] = SEED
                        biopsiesDict['HET %'] = HET - 100
                        biopsiesDict['TISSUE HET %'] = TISSUEHET - 100
                        biopsiesDict['CELL LINES'] = CELLLINES
                        biopsiesDict['TIME'] = TIME / 2
                        biopsiesDict['BIOPSY TYPE'] = type.upper()
                        biopsiesDict['BIOPSY NUMBER'] = n
                        biopsiesDict['THICKNESS'] = thickness
                        biopsiesDict = take_biopsy(agents, PARAM, TIME, sampleMaps[type][str(n)][str(thickness)], biopsiesDict)
                        biopsiesDF = biopsiesDF.append(biopsiesDict, ignore_index=True)

                if not SAVETOGETHER:
                    pickle.dump(biopsiesDF, open(SAVELOC + "BIOPSIES_" + str(type).upper() + "_DAY_" +
                                                    str(int(TIME/2)) + "_SAMPLES_" + str(n) + ".pkl", "wb"))

    if SAVETOGETHER:
        return biopsiesDF

def biopsy(PKLFILES, PARAMLOC, sampleMaps, TIME, TYPE, SAMPLES, THICKNESS, SAVETOGETHER, SAVELOC):

    # Create dataframe to hold biopsy data
    biopsiesDF = make_df()
    tumorDF = make_df()

    PKLS = []
    if not SAVETOGETHER:
        for type in TYPE:
            if type == 'punch' or type == 'needle':
                for time in TIME:
                    for sample in SAMPLES:
                        pklName = "BIOPSIES_" + str(type).upper() + "_DAY_" + str(int(time/2)) + "_SAMPLES_" + str(sample)
                        PKLS.append(pklName)
    for pkl in PKLS:
        pickle.dump(biopsiesDF, open(SAVELOC + pkl + ".pkl", "wb"))

    for f in PKLFILES:
        D, d, R, H, T, N, C, POPS, TYPES = ABM_load(f)
        for s in range(N):
            fileName = re.sub('.*VIVO', 'VIVO', f)
            TUMORID = fileName.replace('.pkl', '')
            print("\t" + TUMORID + "_0" + str(s))
            paramName = PARAMLOC + TUMORID + "_0" + str(s) + ".PARAM.json"
            PARAM = ABM.load_json(paramName)
            for time in TIME:
                agents = D['agents'][s][time][0]
                biopsiesDF = take_biopsies(f, PARAM, s, time, agents, sampleMaps, biopsiesDF, TYPE, SAMPLES, THICKNESS, SAVETOGETHER, SAVELOC)
                if 'tumor' in TYPE:
                    tumorDF = parse_tumor(f, PARAM, s, time, agents, tumorDF, C)

    if SAVETOGETHER:
        totalDF = pd.concat([tumorDF, biopsiesDF])
        pickle.dump(totalDF, open(SAVELOC + "BIOPSIES" + ".pkl", "wb"))
    else:
        if 'tumor' in TYPE:
            pickle.dump(tumorDF, open(SAVELOC + "TUMORS" + ".pkl", "wb"))

    return biopsiesDF, tumorDF


# -------------------- MAIN FUNCTION --------------------------

if __name__ == "__main__":

    parser = get_parser()
    args = parser.parse_args()

    # Parse inputs
    if ":" in args.time:
        dsplit = str(args.time).split(':')
        if len(dsplit) == 3:
            TIME = [int(d*2) for d in np.arange(float(dsplit[0]), float(dsplit[2]) + float(dsplit[1]), float(dsplit[1]))]
        else:
            TIME = [int(d*2) for d in np.arange(float(dsplit[0]), float(dsplit[1]) + 1)]
    elif "-" in args.time:
        dsplit = str(args.time).split('-')
        TIME = [int(d*2) for d in np.arange(float(dsplit[0]), float(dsplit[1]) + 0.5, 0.5)]
    else:
        TIME = [int(float(d)*2) for d in str(args.time).split(',')]

    TYPE = str(args.type).split(',')

    if ":" in args.samples:
        ssplit = str(args.samples).split(':')
        if len(ssplit) == 3:
            SAMPLES = [s for s in range(int(ssplit[0]), int(ssplit[2]) + int(ssplit[1]), int(ssplit[1]))]
        else:
            SAMPLES = [s for s in range(int(ssplit[0]), int(ssplit[1]) + 1)]
    elif "-" in args.samples:
        ssplit = str(args.samples).split('-')
        SAMPLES = [s for s in range(int(ssplit[0]), int(ssplit[1]) + 1)]
    else:
        SAMPLES = [int(s) for s in str(args.samples).split(',')]

    if args.combos:
        sampleCombos = [[s] for s in SAMPLES]
        for c in range(2, len(SAMPLES)+1):
            comb = combinations(SAMPLES, c)
            for i in comb:
                sampleCombos.append(list(i))
        sampleNames = []
        for n in range(0, len(sampleCombos)):
            string = ""
            for i in range(0, len(sampleCombos[n])):
                string += str(sampleCombos[n][i])
            sampleNames.append(string)

        SAMPLES = [int(m) for m in sampleNames]

    if ":" in args.thickness:
        tsplit = str(args.thickness).split(':')
        if len(tsplit) == 3:
            THICKNESS = [t for t in range(int(tsplit[0]), int(tsplit[2]) + int(tsplit[1]), int(tsplit[1]))]
        else:
            THICKNESS = [t for t in range(int(tsplit[0]), int(tsplit[1]) + 1)]
    elif "-" in args.thickness:
        tsplit = str(args.thickness).split('-')
        THICKNESS = [t for t in range(int(tsplit[0]), int(tsplit[1]) + 1)]
    else:
        THICKNESS = [int(t) for t in str(args.thickness).split(',')]

    SAVETOGETHER = args.saveTogether
    SAVELOC = args.saveLoc

    # Retrieve sample maps
    if args.combos:
        sampleMaps = pickle.load(open(args.sampleMapsLoc + "sampleMapsCombos.pkl", "rb"))
    else:
        sampleMaps = pickle.load(open(args.sampleMapsLoc + "sampleMaps.pkl", "rb"))

    # Get files
    pklfiles = get_pkl_files(args.files)
    paramLoc = args.param

    biopsiesDF, tumorDF = biopsy(pklfiles, paramLoc, sampleMaps, TIME, TYPE, SAMPLES, THICKNESS, SAVETOGETHER, SAVELOC)