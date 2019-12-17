import ABM
import os
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from argparse import ArgumentParser

__author__ = "Alexis N. Prybutok"
__email__ = "aprybutok@u.northwestern.edu"

'''
PLOT_TUMOR takes a .pkl file of a dataframe containing all tumor information and makes 
individual bar or distribution plots for the following features of interest:
    
    CELL LINES (X, A, B, C, H)
    CELL STATES (MIGRA, PROLI, QUIES, APOPT, NECRO)
    CYCLE LENGTH
    AVERAGE VOLUME
    CROWDING TOLERANCE
    METABOLIC PREFERENCE
    MIGRATORY THRESHOLD 

Usage: 

    python plot_tumor.py FILE

    FILE
        Path to .pkl file
    [--tumor TUMOR]
        Tumor ID to plot
    [--seed SEED]
        Tumor seed to plot
    [--time TIME]
        Day to record data from (default: 22.0)
    [--saveFigs SAVEFIGS]
        Path designating where figures are saved (default: figures not saved)
    

'''

# -------------- COLORS ---------------------------------------

neutral = '#555555'
apoptotic = '#EDAD08'
quiescent = '#087644'
proliferative = '#993333'
migratory = '#1D6996'
necrotic = '#E17C05'
senescent = '#442B5E'

X = '#c1b9ae' # '#9d9181'
A = '#78cfaa' # '#42bd89'
B = '#e3929d' # '#d96777'
C = '#b7d6e8' # '#79b4d7'
H = '#cbbda9' # '#f3e1a8'

CANCER = '#187178'

# -------------- PARSING AND INPUT/OUTPUT FUNCTIONS -------------

def get_parser():
    # Setup argument parser.
    parser = ArgumentParser(description="Plot tumor feature data for given tumor")
    parser.add_argument(dest="file", help="Path to .pkl file")
    parser.add_argument("--tumor", default="VIVO_HET_DAMAGE_140_140_XABC", dest="tumor",
                        help='Tumor ID to plot')
    parser.add_argument("--seed", default="0", dest="seed",
                        help='Tumor seed to plot')
    parser.add_argument("--time", default="22", dest="time",
                        help="Day to record data from (default: 22)")
    parser.add_argument("--saveFigs", default="", dest="saveFigs",
                        help="Path designating where figures are saved (default: figures not saved)")

    return parser

# -------------------- PLOTTING FUNCTIONS --------------------------

def plot_params(tumorDF, args):

    nbins = 30

    plot_cell_lines(tumorDF, args)
    plot_cell_states(tumorDF, args)
    plot_cell_cycles(tumorDF, nbins, args)
    plot_cell_volumes(tumorDF, nbins, args)
    plot_crowding_tolerance(tumorDF, nbins, args)
    plot_meta_pref(tumorDF, nbins, args)
    plot_migratory_threshold(tumorDF, nbins, args)

def plot_cell_lines(tumorDF, args):

    # Plot cell lines on bar plot
    lines = []
    lineNames = []
    for i in ['X', 'A', 'B', 'C']:
        lines.append(tumorDF['POP ' + i].values[0])
        lineNames.append(i)
    lines.append(tumorDF['HEALTHY'].values[0])
    lineNames.append('H')

    xCL = range(0, len(lines))
    width = 0.35

    figCL = plt.figure()
    axCL = figCL.add_subplot(1, 1, 1)
    axCL.bar(xCL, lines, width, align='center', color=[CANCER, CANCER, CANCER, CANCER, H])
    axCL.set_title("CELL LINES COUNT")
    axCL.set_xlabel("CELL LINES")
    axCL.set_ylabel("COUNT")
    plt.xticks(xCL, lineNames)
    plt.show()

    if args.saveFigs != "":
        plt.savefig(args.saveFigs + "FIG_1B_" + args.tumor + "_0" + args.seed + "_DAY_" + args.time + "_CELLLINES" + ".svg", bbox_inches='tight')

def plot_cell_states(tumorDF, args):

    # Plot cell states on bar plot
    statesC = []
    statesH = []
    stateNames = ['MIGRA', 'PROLI', 'QUIES', 'NECRO', 'APOPT']
    for i in range(0, len(stateNames)):
        s = stateNames[i]
        statesC.append(tumorDF[s + ' CANCER'].values[0])
        statesH.append(tumorDF[s + ' HEALTHY'].values[0])
        stateNames.append(s)

    xS = range(0, len(statesC))
    width = 0.35

    figS = plt.figure()
    axS = figS.add_subplot(1, 1, 1)
    axS.bar(xS, statesC, width, align='center', label='CANCER', color=CANCER)
    axS.bar(xS, statesH, width, bottom=statesC, align='center', label='HEALTHY', color=H)
    axS.set_title("STATES COUNT")
    axS.set_xlabel("STATE")
    axS.set_ylabel("COUNT")
    plt.xticks(xS, stateNames)
    plt.legend(bbox_to_anchor=(1.3, 1), frameon=False)
    plt.show()

    if args.saveFigs != "":
        plt.savefig(args.saveFigs + "FIG_1B_" + args.tumor + "_0" + args.seed + "_DAY_" + args.time + "_CELLSTATES" + ".svg", bbox_inches='tight')

def plot_cell_cycles(tumorDF, nbins, args):

    # Plot cell cycles on histogram
    cyclesC = tumorDF['AVG CELL CYCLES CANCER'].values[0]
    cyclesH = tumorDF['AVG CELL CYCLES HEALTHY'].values[0]

    cycles = cyclesC + cyclesH
    cyclesBins = np.linspace(min(cycles) - 50, max(cycles) + 50, nbins)

    figC = plt.figure()
    axC = figC.add_subplot(1, 1, 1)
    axC.hist(cyclesC, cyclesBins, label='CANCER', color=CANCER, alpha=0.8)
    axC.hist(cyclesH, cyclesBins, label='HEALTHY', color=H, alpha=0.8)
    axC.set_title("AVG CELL CYCLE DISTRIBUTION")
    axC.set_xlabel("AVG CELL CYCLE")
    axC.set_ylabel("FREQUENCY")
    plt.legend(bbox_to_anchor=(1.3, 1), frameon=False)
    plt.show()

    if args.saveFigs != "":
        plt.savefig(args.saveFigs + "FIG_1B_" + args.tumor + "_0" + args.seed + "_DAY_" + args.time + "_CELLCYCLES" + ".svg", bbox_inches='tight')

def plot_cell_volumes(tumorDF, nbins, args):

    # Plot cell volumes on histogram
    volumesC = tumorDF['CELL VOLUMES CANCER'].values[0]
    volumesH = tumorDF['CELL VOLUMES HEALTHY'].values[0]

    volumes = volumesC + volumesH
    volumesBins = np.linspace(min(volumes) - 50, max(volumes) + 50, nbins)

    figV = plt.figure()
    axV = figV.add_subplot(1, 1, 1)
    axV.hist(volumesC, volumesBins, label='CANCER', color=CANCER, alpha=0.8)
    axV.hist(volumesH, volumesBins, label='HEALTHY', color=H, alpha=0.8)
    axV.set_title("CELL VOLUME DISTRIBUTION")
    axV.set_xlabel("VOLUME")
    axV.set_ylabel("FREQUENCY")
    plt.legend(bbox_to_anchor=(1.3, 1), frameon=False)
    plt.show()

    if args.saveFigs != "":
        plt.savefig(args.saveFigs + "FIG_1B_" + args.tumor + "_0" + args.seed + "_DAY_" + args.time + "_CELLVOLUMES" + ".svg", bbox_inches='tight')


def plot_crowding_tolerance(tumorDF, nbins, args):

    # Plot crowding tolerance on histogram
    ctC = tumorDF['CROWDING TOLERANCE CANCER'].values[0]
    ctH = tumorDF['CROWDING TOLERANCE HEALTHY'].values[0]

    ct = ctC + ctH
    ctBins = np.linspace(min(ct) - 5, max(ct) + 5, nbins)

    figCT = plt.figure()
    axCT = figCT.add_subplot(1, 1, 1)
    axCT.hist(ctC, ctBins, label='CANCER', color=CANCER, alpha=0.8)
    axCT.hist(ctH, ctBins, label='HEALTHY', color=H, alpha=0.8)
    axCT.set_title("CROWDING TOLERANCE DISTRIBUTION")
    axCT.set_xlabel("CROWDING TOLERANCE")
    axCT.set_ylabel("FREQUENCY")
    plt.legend(bbox_to_anchor=(1.3, 1), frameon=False)
    plt.show()

    if args.saveFigs != "":
        plt.savefig(args.saveFigs + "FIG_1B_" + args.tumor + "_0" + args.seed + "_DAY_" + args.time + "_CROWDINGTOLERANCE" + ".svg",bbox_inches='tight')

def plot_meta_pref(tumorDF, nbins, args):

    # Plot metabolic preference on histogram
    mpC = tumorDF['METABOLIC PREFERENCE CANCER'].values[0]
    mpH = tumorDF['METABOLIC PREFERENCE HEALTHY'].values[0]
    mpBins = np.linspace(0, 1, nbins)

    figMP = plt.figure()
    axMP = figMP.add_subplot(1, 1, 1)
    axMP.hist(mpC, mpBins, label='CANCER', color=CANCER, alpha=0.8)
    axMP.hist(mpH, mpBins, label='HEALTHY', color=H, alpha=0.8)
    axMP.set_title("METABOLIC PREFERENCE DISTRIBUTION")
    axMP.set_xlabel("METABOLIC PREFERENCE")
    axMP.set_ylabel("FREQUENCY")
    plt.legend(bbox_to_anchor=(1.3, 1), frameon=False)
    plt.show()

    if args.saveFigs != "":
        plt.savefig(args.saveFigs + "FIG_1B_" + args.tumor + "_0" + args.seed + "_DAY_" + args.time + "_METAPREF" + ".svg", bbox_inches='tight')

def plot_migratory_threshold(tumorDF, nbins, args):

    # Plot migratory threshold on histogram
    mtC = tumorDF['MIGRATORY THRESHOLD CANCER'].values[0]
    mtH = tumorDF['MIGRATORY THRESHOLD HEALTHY'].values[0]

    mt = mtC + mtH
    mtBins = np.linspace(0, max(mt) + 1, nbins)

    figMT = plt.figure()
    axMT = figMT.add_subplot(1, 1, 1)
    axMT.hist(mtC, mtBins, label='CANCER', color=CANCER, alpha=0.8)
    axMT.hist(mtH, mtBins, label='HEALTHY', color=H, alpha=0.8)
    axMT.set_title("MIGRATORY THRESHOLD DISTRIBUTION")
    axMT.set_xlabel("MIGRATORY THRESHOLD")
    axMT.set_ylabel("FREQUENCY")
    plt.legend(bbox_to_anchor=(1.3, 1), frameon=False)
    plt.show()

    if args.saveFigs != "":
        plt.savefig(args.saveFigs + "FIG_1B_" + args.tumor + "_0" + args.seed + "_DAY_" + args.time + "_MIGRATORYTHRESHOLD" + ".svg", bbox_inches='tight')

# -------------------- MAIN FUNCTION --------------------------

if __name__ == "__main__":

    parser = get_parser()
    args = parser.parse_args()

    # Get files
    DF = pickle.load(open(args.file, "rb"))
    tumorDF = DF.loc[DF['BIOPSY TYPE'] == 'TUMOR']
    tumorDF = tumorDF.loc[tumorDF['TIME'] == float(args.time)]
    tumorDF = tumorDF.loc[tumorDF['TUMOR ID'] == args.tumor]
    tumorDF = tumorDF.loc[tumorDF['SEED'] == int(args.seed)]

    plot_params(tumorDF, args)



