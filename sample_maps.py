import ABM
import os
import pickle
import location_maps
from argparse import ArgumentParser
from itertools import combinations

__author__ = "Alexis N. Prybutok"
__email__ = "aprybutok@u.northwestern.edu"

'''
SAMPLE_MAPS makes a list of the mapping of all full biopsies (at any one of 7 locations for punch 
and 6 locations for needle) to their associated locations and those associated indices. 
It will extract data into dictionary sampleMaps in the form:

{
    "punch": {
        "1": {
            "0": [locs at rad 0 for "center" sample]
            "1": [locs at rad 0 for "center" sample, locs at rad 1 for "center" sample]
            .
            .
            .
            "34": [locs at rad 0 for "center" sample, locs at rad 1 for "center" sample, ..., 
                        locs at rad 34 for "center" sample]
        }
        "2": {
            "0": [locs at rad 0 for "u" samples]
            "1": [locs at rad 0 for "u" samples, locs at rad 1 for "u" samples]
            .
            .
            .
            "34": [locs at rad 0 for "u" samples, locs at rad 1 for "u" samples,
                        ..., locs at rad 34 for "u" samples]
        }
        "3": -- dict of samples at all radii for "v" samples --
        "4": -- dict of samples at all radii for "w" samples --
        "5": -- dict of samples at all radii for "uv" samples --
        "6": -- dict of samples at all radii for "vw" samples --
        "7": -- dict of samples at all radii for "uw" samples --
    },
    
    "needle": {
        "1": {
            "0": [locs at width 0 for "u" sample]
            "1": [locs at width 1 for "u" sample, locs at width 1 for "u" sample]
            .
            .
            .
            "34": [locs at width 0 for "u" sample, locs at width 1 for "u" sample, ..., 
                        locs at width 34 for "u" sample]
        }
        "2": {
            "0": [locs at width 0 for "v" samples]
            "1": [locs at width 0 for "v" samples, locs at width 1 for "v" samples]
            .
            .
            .
            "34": [locs at width 0 for "v" samples, locs at width 1 for "v" samples,
                        ..., locs at width 34 for "v" samples]
        }
        "3": -- dict of samples at all widths for "w" samples --
        "4": -- dict of samples at all widths for "uv" samples --
        "5": -- dict of samples at all widths for "vw" samples --
        "6": -- dict of samples at all widths for "uw" samples --
    }

}

where each location is a tuple of the location at specified radii/width 
and its assocaited index as follows:

    [locs at rad/width x for samples y] = [(loc, index), (loc, index), ... , (loc, index)]

Usage: 

    python sample_maps.py [--nosave] [--saveLoc SAVELOC] [--usePkl] [--pklLoc PKLLOC] [--combos]
    
    [--nosave]
        Flag to indicate whether or not to save samples as a pickle
    [--saveLoc LOC]
        Location of where to save file, default will save here
    [--usePkl]
        Flag to indicate whether or not to get location mapping from a pickle
    [--pklLoc PKLLOC]
        Location of where to find locMaps pickle, default will search here
    [--combos]
        Take all possible combinations of all numbers and angles of samples

'''

# -------------------- Parsing Function ---------------------------------

def get_parser():
    parser = ArgumentParser(description="Make a list of all biopsy types and associated locations and indices")
    parser.add_argument("--nosave", default=False, dest="nosave", action='store_true',
                        help="Flag to indicate whether or not to save samples as a pickle")
    parser.add_argument("--saveLoc", default='./', dest="saveLoc",
                        help="Location of where to save file, default will save here")
    parser.add_argument("--usePkl", default=False, dest="usePkl", action='store_true',
                        help="Flag to indicate whether or not to get location mapping from a pickle")
    parser.add_argument("--pklLoc", default='./', dest="pklLoc",
                        help="Location of where to find locMaps pickle, default will search here")
    parser.add_argument("--combos", default=False, dest="combos", action='store_true',
                        help="Take all possible combinations of all numbers and angles of samples")
    return parser


# -------------------- BIOPSY LOCATION FUNCTIONS -------------------------

def make_biops(strategy, locMaps, thickness, number):
    locs = set()
    for t in range(0, thickness+1):
        for m in range(len(locMaps[strategy][str(number)][t])):
            locs.add(locMaps[strategy][str(number)][t][m])
    return locs

def make_combos(punchLocs, needleLocs):

    punchCombos = []
    needleCombos = []

    for s in range(1, 8):
        punchCombos.append([s])
        if s != 7:
            needleCombos.append([s])

    for c in range(2, 8):
        combP = combinations(punchLocs, c)
        for i in combP:
            punchCombos.append(list(i))

    for c in range(2, 7):
        combN = combinations(needleLocs, c)
        for i in combN:
            needleCombos.append(list(i))

    return punchCombos, needleCombos


def make_biops_combos(strategy, locMaps, thickness, combosList):
    locs = set()
    for n in combosList:
        for t in range(0, thickness+1):
            for m in range(len(locMaps[strategy][str(n)][t])):
                locs.add(locMaps[strategy][str(n)][t][m])
    return locs

# -------------------- GET SAMPLE MAPS FUNCITONS -------------------------

def get_sample_maps(locMaps):

    # Setup samples dictionary
    sampleMaps = {
        "punch": {
            "1": {},
            "2": {},
            "3": {},
            "4": {},
            "5": {},
            "6": {},
            "7": {}
        },
        "needle": {
            "1": {},
            "2": {},
            "3": {},
            "4": {},
            "5": {},
            "6": {}
        }
    }

    # Make lists for biopsies
    for i in range(1, 8):
        for thickness in range(0, 34):

            # Make lists for punch biopsies
            sampleMaps["punch"][str(i)][str(thickness)] = make_biops("punch", locMaps, thickness, i)

            # Make lists for needle biopsies
            if i != 7:
                sampleMaps["needle"][str(i)][str(thickness)] = make_biops("needle", locMaps, thickness, i)

    return sampleMaps

def get_sample_maps_combos(locMaps):

    # Setup samples dictionary
    sampleMaps = {
        "punch": {},
        "needle": {}
    }

    punchLocs = [1, 2, 3, 4, 5, 6, 7]
    needleLocs = [1, 2, 3, 4, 5, 6]

    punchCombos, needleCombos = make_combos(punchLocs, needleLocs)

    punchNames = []
    needleNames = []

    for n in range(0, len(punchCombos)):
        string = ""
        for i in range(0, len(punchCombos[n])):
            string += str(punchCombos[n][i])
        punchNames.append(string)
        sampleMaps["punch"][str(string)] = {}

    for n in range(0, len(needleCombos)):
        string = ""
        for i in range(0, len(needleCombos[n])):
            string += str(needleCombos[n][i])
        needleNames.append(string)
        sampleMaps["needle"][str(string)] = {}

    # Make lists for biopsies
    for i in range(0, len(punchCombos)):
        punchCombo = punchCombos[i]
        punchName = punchNames[i]
        for thickness in range(0, 34):

            # Make lists for punch biopsies
            sampleMaps["punch"][punchName][str(thickness)] = make_biops_combos("punch", locMaps, thickness, punchCombo)

    for i in range(0, len(needleCombos)):
        needleCombo = needleCombos[i]
        needleName = needleNames[i]
        for thickness in range(0, 34):
                sampleMaps["needle"][needleName][str(thickness)] = make_biops_combos("needle", locMaps, thickness, needleCombo)

    return sampleMaps

# -------------------- MAIN FUNCTION --------------------------

if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    combos = args.combos

    if args.usePkl:
        locMaps = pickle.load(open(args.pklLoc + "locMaps.pkl", "rb"))

    else:
        locMaps = location_maps.get_location_maps()

    if not args.combos:
        sampleMaps = get_sample_maps(locMaps)
    else:
        sampleMaps = get_sample_maps_combos(locMaps)

    if not args.nosave:
        if not args.combos:
            pickle.dump(sampleMaps, open(args.saveLoc + "sampleMaps.pkl", "wb"))
        else:
            pickle.dump(sampleMaps, open(args.saveLoc + "sampleMapsCombos.pkl", "wb"))