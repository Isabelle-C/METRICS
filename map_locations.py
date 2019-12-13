import ABM
import pickle
from abm_parse import get_hex_coords
from argparse import ArgumentParser

__author__ = "Alexis N. Prybutok"
__email__ = "aprybutok@u.northwestern.edu"

'''
MAP_LOCATIONS makes a list of the mapping of all biopsy types to their associated 
locations and those associated indices. It will extract data into dictionary locMaps in the form:

{
    "punch": {
        "1": [[locs at rad 0], [locs at rad 1], .... , [locs at rad 34]],
        "2": [[locs at rad 0], [locs at rad 1], .... , [locs at rad 34]],
        "3": [[locs at rad 0], [locs at rad 1], .... , [locs at rad 34]],
        "4": [[locs at rad 0], [locs at rad 1], .... , [locs at rad 34]],
        "5": [[locs at rad 0], [locs at rad 1], .... , [locs at rad 34]],
        "6": [[locs at rad 0], [locs at rad 1], .... , [locs at rad 34]],
        "7": [[locs at rad 0], [locs at rad 1], .... , [locs at rad 34]]
    },
    
    "needle": {
        "1": [[locs at width 1], [locs at width 3], .... , [locs at width 34]],
        "2": [[locs at width 1], [locs at width 3], .... , [locs at width 34]],
        "3": [[locs at width 1], [locs at width 3], .... , [locs at width 34]],
        "4": [[locs at width 1], [locs at width 3], .... , [locs at width 34]],
        "5": [[locs at width 1], [locs at width 3], .... , [locs at width 34]],
        "6": [[locs at width 1], [locs at width 3], .... , [locs at width 34]]
    }

}

where each entry in the location arrays are lists of tuples of locations at various radii/widths 
and their assocaited indices as follows:

    [locs at rad/width x] = [(loc, index), (loc, index), ... , (loc, index)]

For "punch" biopsies, locs at rad x produce rings x distance away from center of punch. Center is [0,0,0],
while other punch biopsies occur centered at a distance of 15 away from the center.

For "needle" biopsies, a needle goes to a depth equal to the center of the simulation, are taken in all
directions, and locs at width x produce a set of locations x distance from the specified angle center.

Usage: 

    python map_locations.py [--save] [--saveLoc SAVELOC] [--error]
    
    [--save]
        Flag to indicate whether or not to save locMaps as a pickle
    [--saveLoc]
        Location of where to save file, default will save here
    [--error]

'''

# -------------------- Parsing Function --------------------------

def get_parser():
    parser = ArgumentParser(description="Make a map of all simulation locations to parsed indices")
    parser.add_argument("--save", default=False, dest="save", action='store_true',
                        help="Flag to indicate whether or not to save locMaps as a pickle")
    parser.add_argument("--saveLoc", default='./', dest="saveLoc",
                        help="Location of where to save file, default will save here")
    parser.add_argument("--error", default=False, dest="error", action='store_true',
                        help="")
    return parser


# -------------------- BIOPSY LOCATION FUNCTIONS -------------------------

def make_punch_biop_centers_list(R):
    return [(0, -R, R), (R, 0, -R), (-R, R, 0), (R, -R, 0), (0, R, -R), (-R, 0, R)]

# Function: get_hexes_within_rad
# Returns a list of hex info for all hexagons at a specified radius from the center.
def get_hexes_at_rad(locs, rad, ctr):
    rad_hexes = [(tuple(locs[h]), h) for h in range(len(locs)) if get_rad(locs[h], ctr) == rad]
    return rad_hexes

# Function: calc_rad
# Given a list of 3 hexagonal coordinates, returns the radius of that spot from center_coord.
def get_rad(pt_coord, cntr_coord):
    return (abs(pt_coord[0] - cntr_coord[0])
            + abs(pt_coord[1] - cntr_coord[1])
            + abs(pt_coord[2] - cntr_coord[2])) / 2

def get_hexes_at_width(locs, width, direction):
    if direction == 1:
        width_hexes = [(tuple(locs[h]), h) for h in range(len(locs)) if abs(locs[h][0]) == width
                            and locs[h][1] <= 0 and locs[h][2] >=0 ]
    elif direction == 2:
        width_hexes = [(tuple(locs[h]), h) for h in range(len(locs)) if locs[h][0] >= 0
                            and abs(locs[h][1]) == width and locs[h][2] <= 0]
    elif direction == 3:
        width_hexes = [(tuple(locs[h]), h) for h in range(len(locs)) if locs[h][0] <= 0
                            and locs[h][1] >= 0 and abs(locs[h][2]) == width]
    elif direction == 4:
        width_hexes = [(tuple(locs[h]), h) for h in range(len(locs)) if locs[h][0] >= 0
                       and locs[h][1] <= 0 and abs(locs[h][2]) == width]
    elif direction == 5:
        width_hexes = [(tuple(locs[h]), h) for h in range(len(locs)) if abs(locs[h][0]) == width
                            and locs[h][1] >= 0 and locs[h][2] <=0]
    elif direction == 6:
        width_hexes = [(tuple(locs[h]), h) for h in range(len(locs)) if locs[h][0] <= 0
                       and abs(locs[h][1]) == width and locs[h][2] >= 0]
    return width_hexes


# -------------------- GET LOCATION MAPS FUNCITON --------------------------

def get_location_maps():

    # Setup location maps dictionary
    locMaps = {
        "punch": {
            "1": [],
            "2": [],
            "3": [],
            "4": [],
            "5": [],
            "6": [],
            "7": []
        },
        "needle": {
            "1": [],
            "2": [],
            "3": [],
            "4": [],
            "5": [],
            "6": []
        }
    }
    # Make a list of all hex coords in a 40 radius hexagonal simulation
    locs = get_hex_coords(34)

    punchCenters = [(0, 0, 0)]
    punchCenters += make_punch_biop_centers_list(15)

    # Make lists for biopsies
    for i in range(0,34):

        # Make lists for punch biopsies
        locMaps["punch"]["1"].append(get_hexes_at_rad(locs, i, punchCenters[0]))
        locMaps["punch"]["2"].append(get_hexes_at_rad(locs, i, punchCenters[1]))
        locMaps["punch"]["3"].append(get_hexes_at_rad(locs, i, punchCenters[2]))
        locMaps["punch"]["4"].append(get_hexes_at_rad(locs, i, punchCenters[3]))
        locMaps["punch"]["5"].append(get_hexes_at_rad(locs, i, punchCenters[4]))
        locMaps["punch"]["6"].append(get_hexes_at_rad(locs, i, punchCenters[5]))
        locMaps["punch"]["7"].append(get_hexes_at_rad(locs, i, punchCenters[6]))

        # Makes lists for needle biopsies
        locMaps["needle"]["1"].append(get_hexes_at_width(locs, i, 1))
        locMaps["needle"]["2"].append(get_hexes_at_width(locs, i, 2))
        locMaps["needle"]["3"].append(get_hexes_at_width(locs, i, 3))
        locMaps["needle"]["4"].append(get_hexes_at_width(locs, i, 4))
        locMaps["needle"]["5"].append(get_hexes_at_width(locs, i, 5))
        locMaps["needle"]["6"].append(get_hexes_at_width(locs, i, 6))

    return locMaps

# -------------------- MAIN FUNCTION --------------------------

if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()

    locMaps = get_location_maps()

    if args.save:
        pickle.dump(locMaps, open(args.saveLoc + "locationMaps.pkl", "wb"))