import ABM
import os
import pickle
import location_maps
from argparse import ArgumentParser

__author__ = "Alexis N. Prybutok"
__email__ = "aprybutok@u.northwestern.edu"

'''
SAMPLE_MAPS makes a list of the mapping of all full biopsies to their associated 
locations and those associated indices. It will extract data into dictionary sampleMaps in the form:

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
            "0": [locs at rad 0 for "center" and "u" samples]
            "1": [locs at rad 0 for "center" and "u" samples, locs at rad 1 for "center" and "u" samples]
            .
            .
            .
            "34": [locs at rad 0 for "center" and "u" samples, locs at rad 1 for "center" and "u" samples,
                        ..., locs at rad 34 for "center" and "u" samples]
        }
        "3": -- dict of samples at all radii for "center", "u", and "v" samples --
        "4": -- dict of samples at all radii for "center", "u", "v", and "w" samples --
        "5": -- dict of samples at all radii for "center", "u", "v", "w", and "uv" samples --
        "6": -- dict of samples at all radii for "center", "u", "v", "w", "uv", and "vw" samples --
        "7": -- dict of samples at all radii for "center", "u", "v", "w", "uv", "vw", and "uw" samples --
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
            "0": [locs at width 0 for "u" and "v" samples]
            "1": [locs at width 0 for "u" and "v" samples, locs at width 1 for "u" and "v" samples]
            .
            .
            .
            "34": [locs at width 0 for "u" and "v" samples, locs at width 1 for "u" and "v" samples,
                        ..., locs at width 34 for "u" and "v" samples]
        }
        "3": -- dict of samples at all widths for "u", "v", and "w" samples --
        "4": -- dict of samples at all widths for "u", "v", "w", and "uv" samples --
        "5": -- dict of samples at all widths for "u", "v", "w", "uv", and "vw" samples --
        "6": -- dict of samples at all widths for "u", "v", "w", "uv", "vw", and "uw" samples --
    }

}

where each location is a tuple of the location at specified radii/width 
and its assocaited index as follows:

    [locs at rad/width x for samples y] = [(loc, index), (loc, index), ... , (loc, index)]

Usage: 

    python sample_maps.py [--save] [--saveLoc SAVELOC] [--usePkl] [--pklLoc PKLLOC]
    
    --


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

    return parser


# -------------------- BIOPSY LOCATION FUNCTIONS -------------------------

def make_biops(strategy, locMaps, thickness, number):
    locs = set()
    for n in range(1,number+1):
        for t in range(0,thickness+1):
            for m in range(len(locMaps[strategy][str(n)][t])):
                locs.add(locMaps[strategy][str(n)][t][m])
    return locs



# -------------------- GET SAMPLE MAPS FUNCITON -------------------------

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

# -------------------- MAIN FUNCTION --------------------------

if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()

    if args.usePkl:
        locMaps = pickle.load(open(args.pklLoc + "locMaps.pkl", "rb"))

    else:
        locMaps = location_maps.get_location_maps()

    sampleMaps = get_sample_maps(locMaps)

    if not args.nosave:
        pickle.dump(sampleMaps, open(args.saveLoc + "sampleMaps.pkl", "wb"))