"""
    FILE: biopsy.py
    Author: Andrea Collins, 2019
    Purpose: Given a pkl file of abm sim data,
    models a biopsy of the simulated tissue.
    Resources: Alex Prybutok (Leonard Lab), Jessica Yu (Bagheri Lab), Northwestern University
    Version: healthy cells not included in tumor calculations, but are included in biopsy calculations.

    To run this script, use the following command:

    'python biopsy.py [absolute path to directory of pkl files or single pkl file]'

    This script outputs a JSON file for each folder in the input directory,
    located in the folder where the script itself is located,
    with data in the following format:

    { sim seed 1:
    {rad1:
        [
            [ags score, %proliferative, %migratory, %cancerous, %neutral, %apoptotic, %quiescent, %senescent,
                avg volume, stdev cell volume, avg health. cell cycle time, stdev health. cycle time, avg canc. cell cycle time,stdev canc.cycle time, cell count, [hex coord]],
            ...
        ] , rad2: ...
    },
      sim seed 2: {rad1: [[ags score, %proliferative, %migratory, %cancerous, cell cycle time fraction], ...] , rad2: ...},
      ...
      -1: [tumor ags score, ....]
     }

     where sim seed is the seed of the simulation in the file, and the "seed" -1 maps to the whole
     tumor aggressiveness score and data.

"""

import os
import json
from numpy import mean, std
from abm_parse import load as ABM_load
import ABM

# Constants
TIME_POINT = 42 # the end of the simulation
MAX_ENV_RAD = 34
N_SEEDS = 50
CELLS_IN_HEX = 6
BIOPS_RAD = 6
NEUT = 0
APOP = 1
QUIES = 2
MIGR = 3
PROLIF = 4
SENES = 5
TUMOR_CENTER = [0, 0, 0]


# Main method
def main():
    parser = ABM.get_parser("Parses simulation files", setup=False)
    parser.add_argument(dest="files", help="Path to .json, .tar.xz, or directory")
    args = parser.parse_args()

    # For each file, get the cell and population information, then model the biopsies and output the
    # biopsy information to a JSON file.
    for f in get_pkl_files(args.files):
        print("----" + f + "----")
        D, C, POPS = get_matrix(f)
        biopsies_by_seed = {}  # dict listing seeds to a dict listing radii to lists of cells

        # For every seed, get the biopsy information at every radius and the whole tumor information.
        all_seeds = []
        for s in range(N_SEEDS):
            print("       > Extracting biopsies from seed " + str(s + 1) + "...")
            healthy_pop = max(POPS)
            all_hexes = D['agents'][s][TIME_POINT][0]
            biopsies = take_biopsy(all_hexes, C, healthy_pop)
            biopsies_by_seed[s + 1] = biopsies

            # Get the tumor information. Switch True to False to include healthy cells in tumor calculations
            tumor_info = calc_tiss_info(all_hexes, healthy_pop, [[0, 0, 0]], 0, True)
            all_seeds.append(tumor_info)

        # Average the tumor information across all seeds.
        ags = [t[0] for t in all_seeds]
        p = [t[1] for t in all_seeds]
        m = [t[2] for t in all_seeds]
        c = [t[3] for t in all_seeds]
        n = [t[4] for t in all_seeds]
        a = [t[5] for t in all_seeds]
        q = [t[6] for t in all_seeds]
        s = [t[7] for t in all_seeds]
        av = [t[8] for t in all_seeds]
        sv = [t[9] for t in all_seeds]
        aht = [t[10] for t in all_seeds]
        sht = [t[11] for t in all_seeds]
        act = [t[12] for t in all_seeds]
        sct = [t[13] for t in all_seeds]
        count = [t[14] for t in all_seeds]

        avg_info = [mean(ags), mean(p), mean(m), mean(c), mean(n), mean(a), mean(q), mean(s), mean(av),
                    mean(sv), mean(aht), mean(sht), mean(act), mean(sct), mean(count), TUMOR_CENTER]
        biopsies_by_seed[-1] = avg_info
        output_file(biopsies_by_seed, f)


# Function: take_biopsy
# Given data about all hexagons in sim at a certain time point, simulates a biopsy at every radius
# and returns a dictionary of radius to aggressiveness score of the biopsy at that radius.
def take_biopsy(all_hexes, C, healthy_pop):
    max_tumor_rad = calc_max_rad(all_hexes, C, healthy_pop)
    biopsies = {}

    # For each radius in the tumor, get all the hexagons at that radius.
    # Take a biopsy centered around each hexagon in that radius and map it
    # to its index in C (the list of hex coords) in a dict. Then, map that
    # dict to its corresponding radius.
    for rad in range(max_tumor_rad):
        rad_hexes = get_hexes_at_rad(all_hexes, C, rad, [0, 0, 0])
        rad_biopsies = {}
        for r in rad_hexes:
            pos = C[r]
            b = get_hexes_within_rad(all_hexes, C, BIOPS_RAD, pos)
            rad_biopsies[r] = b
        biopsies[rad] = rad_biopsies
    biopsies = get_biopsy_info(biopsies, healthy_pop, max_tumor_rad, C)
    return biopsies


# -------------------- PARSING AND INPUT/OUTPUT -------------------------


# Function: get_pkl_files
# If arg is a directory, returns a list of all the files in that
# directory that are pkl files. If arg is a single file, checks
# if that file is a pkl file and if it is, returns that filename.
def get_pkl_files(arg):
    if arg[-1] == "/":
        return [arg + f for f in os.listdir(arg) if ABM.is_pkl(f)]
    else:
        assert ABM.is_pkl(arg)
        return [arg]


# Function: output_file
# Writes the entire dict of biopsies to a JSON file with the tag 'BPS'
# added on to the end of the filename.
# For each seed, the whole tumor aggressiveness is mapped to the key -1.
def output_file(biopsies_by_seed, pathname):
    out_file = output_filename(pathname)
    with open(out_file, 'x') as f:
        json.dump(biopsies_by_seed, f, indent=4)


# Function: output_filename
# Extracts the filename from the inputted pathname, adding the 'BPS' tag and the '.json' ending.
def output_filename(pathname):
    ch_pos = -1
    ch = pathname[ch_pos]
    while ch != '/':
        ch_pos -= 1
        ch = pathname[ch_pos]
    return pathname[(ch_pos + 1):-4] + "_BPS.json"


# Function: get_matrix
# Takes in a path to a pkl file and extracts and returns the matrix of simulation data.
def get_matrix(pathname):
    D, d, R, H, T, N, C, POPS, TYPES = ABM_load(pathname)
    return D, C, POPS


# -------------------- BIOPSY LOCATION FUNCTIONS -------------------------

# Function: get_hexes_within_rad
# Returns a list of hex info for all hexagons within a specified radius from the center.
def get_hexes_within_rad(all_hexes, C, rad, ctr):
    num_hexes = len(all_hexes)
    rad_hexes = [all_hexes[h] for h in range(num_hexes) if calc_rad(C[h], ctr) <= rad]
    return rad_hexes


# Function: get_hexes_at_rad
# Returns a dict mapping the index of the hexagon in C (list of hex coordinates) to hex info
# for all hexagons at the specified radius from the center.
def get_hexes_at_rad(all_hexes, C, rad, ctr):
    rad_hexes = {}
    num_hexes = len(all_hexes)
    for hex_pos in range(num_hexes):
        hex = all_hexes[hex_pos]
        hex_coord = C[hex_pos]
        hex_rad = calc_rad(hex_coord, ctr)
        if hex_rad == rad:
            rad_hexes[hex_pos] = hex
    return rad_hexes


# Function: calc_rad
# Given a list of 3 hexagonal coordinates, returns the radius of that spot from center_coord.
def calc_rad(pt_coord, cntr_coord):
    return (abs(pt_coord[0] - cntr_coord[0])
            + abs(pt_coord[1] - cntr_coord[1])
            + abs(pt_coord[2] - cntr_coord[2])) / 2


# Function: calc_max_rad
# Calculates the maximum radius of the tumor, where the ratio of live cells to empty
# spots is less than a certain benchmark.
def calc_max_rad(all_hexes, C, healthy):
    max_rad = MAX_ENV_RAD
    min_fillage = 1 # 1%

    for r in range(MAX_ENV_RAD):
        rad_hexes = get_hexes_at_rad(all_hexes, C, r, [0, 0, 0])
        fillage = 100 * get_cancer_count(list(rad_hexes.values()), healthy) / (CELLS_IN_HEX * len(rad_hexes))
        if fillage < min_fillage:
            max_rad = r
            break
    return max_rad


# -------------------- AGGRESSIVENESS FUNCTIONS -------------------------


# Function: get_biopsy_info
# Given a dict mapping each radius to a list of lists of hexagons at that radius (biopsies), returns a dict mapping
# each radius to a list of lists, each containing the biopsy information in the list format at the top of this file
# for one biopsy at that radius.
def get_biopsy_info(biopsies, healthy_pop, max_tumor_rad, C):
    for rad in range(max_tumor_rad):
        rad_biopsies = biopsies[rad]
        rad_info = [calc_tiss_info(rad_biopsies[b], healthy_pop, C, b, False) for b in rad_biopsies]
        biopsies[rad] = rad_info
    return biopsies


# Function: calc_tiss_info
# Takes in a dict of all the cells in the given hexagons to their positions in C and calculates and returns a list in the format:
# [ags score, %proliferative, %migratory, %cancerous, %neutral, %apoptotic, %quiescent, %senescent,
# avg volume, stdev cell volume, avg healthy cell cycle time, stdev healthy cycle time, avg canc. cell cycle time, stdev canc. cycle time, coord]
def calc_tiss_info(all_hexes, healthy_pop, C, pos, exclude_healthy):
    c, c_std, h, h_std = get_time_frac(all_hexes, healthy_pop)
    cell_cycle_frac = c / h if c != 0 and h !=0 else 0
    avg_vol, stdev_vol = get_avg_vol(all_hexes, healthy_pop, exclude_healthy)
    coord = C[pos]

    cell_count = get_cancer_count(all_hexes, healthy_pop) if exclude_healthy else get_cell_count(all_hexes)

    perc_migr = get_percent_state(all_hexes, MIGR, cell_count, exclude_healthy, healthy_pop)
    perc_prolif = get_percent_state(all_hexes, PROLIF, cell_count, exclude_healthy, healthy_pop)
    perc_neut = get_percent_state(all_hexes, NEUT, cell_count, exclude_healthy, healthy_pop)
    perc_apop = get_percent_state(all_hexes, APOP, cell_count, exclude_healthy, healthy_pop)
    perc_quies = get_percent_state(all_hexes, QUIES, cell_count, exclude_healthy, healthy_pop)
    perc_senes = get_percent_state(all_hexes, SENES, cell_count, exclude_healthy, healthy_pop)
    perc_cancer = 1 if exclude_healthy else 1 - get_percent_pop(all_hexes, healthy_pop, cell_count)
    return [calc_ags_score(perc_migr, perc_prolif, perc_cancer, cell_cycle_frac),
            perc_prolif, perc_migr, perc_cancer, perc_neut, perc_apop, perc_quies, perc_senes, avg_vol, stdev_vol, h, h_std, c, c_std, cell_count, coord]


# Function: calc_ags_score
# Given the percent of the cells that are migratory, proliferative, and cancerous, calculates the aggressiveness
# score of the cells at that radius.
def calc_ags_score(perc_migr, perc_prolif, perc_cancer, cell_cycle_frac):
    return ((perc_migr + perc_prolif) * perc_cancer) * cell_cycle_frac


# Function: get_avg_vol
# Calculates and returns the average cell volume and standard deviation of cell volume of the cells in hexes.
def get_avg_vol(hexes, healthy, exclude_healthy):
    vols = []
    for hexg in hexes:
        for triangle in hexg:
            if exclude_healthy:
                if triangle[2] != -1 and triangle[1] != healthy:
                    vols.append(triangle[2])
            else:
                if triangle[2] != -1:
                    vols.append(triangle[2])
    return mean(vols), std(vols)


# Function: get_time_frac
# Given a list of hexagons, calculates the average cell cycle time of all the healthy and cancerous cells
# in the list and returns their quotient.
def get_time_frac(hexes, healthy_pop):
    cancer_cycle_times = []
    healthy_cycle_times = []

    for hexg in hexes:
        for triangle in hexg:
            if triangle[3] != -1:
                if triangle[0] == healthy_pop:
                    healthy_cycle_times.append(triangle[3])
                else:
                    cancer_cycle_times.append(triangle[3])
    if len(cancer_cycle_times) == 0 or len(healthy_cycle_times) == 0:
        return 0, 0, 0, 0
    c = mean(cancer_cycle_times)
    c_std = std(cancer_cycle_times)
    h = mean(healthy_cycle_times)
    h_std = std(healthy_cycle_times)
    return c, c_std, h, h_std


# Function: get_cell_count
# Given a list of hexagon positions, returns the number of cells (non-empty positions) in those hexagons
def get_cell_count(hexes):
    cell_count = 0
    for hexg in hexes:
        for triangle in hexg:
            if triangle[0] != -1:
                cell_count += 1
    return cell_count


# Function: get_healthy_count
# Given a list of hexagon positions, returns the number of cancerous cells in those hexagons.
def get_cancer_count(hexes, healthy):
    cell_count = 0
    for hexg in hexes:
        for triangle in hexg:
            if triangle[0] != healthy and triangle[0] != -1:
                cell_count += 1
    return cell_count


# Function: get_percent_state
# Given a list of hexagons, returns the percent of cells in the given state.
def get_percent_state(hexes, state, cell_count, exclude_healthy, healthy):
    state_count = 0
    for hexg in hexes:
        for triangle in hexg:
            if exclude_healthy:
                if triangle[1] == state and triangle[0] != healthy and triangle[0] != -1:
                    state_count += 1
            else:
                if triangle[1] == state:
                    state_count += 1
    return state_count / cell_count


# Function: get_percent_pop
# Returns the percent of cells from the given population.
def get_percent_pop(hexes, pop, cell_count):
    pop_count = 0
    for hexg in hexes:
        for triangle in hexg:
            if triangle[0] == pop:
                pop_count += 1
    return pop_count / cell_count


# If statement to run main method
if __name__ == "__main__":
    main()
