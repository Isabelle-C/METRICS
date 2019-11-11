"""
    FILE: biopsy_stat.py
    Author: Andrea Collins, 2019
    Purpose: Analyzes biopsy data to find at which radius
    from the tumor core a biopsy is the most predictive of
    the aggressiveness of a tumor.
    Version:
    Resources: Alex Prybutok (Leonard Lab), Jessica Yu (Bagheri Lab), Northwestern University, redblobgames.com,
    https://stackoverflow.com/questions/268272/getting-key-with-maximum-value-in-dictionary

    Format of each biopsy information list in the input JSON file:
    [
        ags score, %proliferative, %migratory, %cancerous, %neutral, %apoptotic, %quiescent, %senescent,
        avg volume, stdev cell volume, avg healthy cell cycle time, stdev healthy cycle time, avg canc. cell cycle time, stdev canc.cycle time, cell count, [hex coord]
    ]

    To run this script, use the following command:

    'python biopsy_stat.py [absolute path to directory of .json files from biopsy.py or a single json file]'

"""

import numpy as np
import json
import ABM
import math
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats
import seaborn

# Constants
alpha = 0.01
MAX_TUMOR_RAD = 34

# Dict mapping feature name to position in each biopsy information list from the input JSON
features = {0: "aggressiveness score", 1: "proliferative percentage", 2: "migratory percentage", 3: "cancerous percentage", 4: "neutral percentage", 5: "apoptotic percentage",
            6: "quiescent percentage", 7: "senescent percentage", 8: "average cell volume", 9: "stdev cell volume", 10: "average healthy cell cycle time", 11: "stdev healthy cell cycle time",
            12: "average cancer cell cycle time", 13: "stdev cancer cell cycle time", 14: "cell count", 15: "hex coordinates"}


# Function: main
# Main method
def main():
    parser = ABM.get_parser("Parses simulation files", setup=False)
    parser.add_argument(dest="files", help="Path to .json, .tar.xz, or directory")
    args = parser.parse_args()
    r_max_likelihoods = []
    r_min_likelihoods = []
    merged_nonsig = {}
    merged_sig= {}

    # Make an empty DataFrame with the correct column names.
    total_df = pd.DataFrame(columns=["radius", "tumor aggressiveness", "tumor prolif percentage", "tumor migratory percentage", "tumor cancer percentage",
                                     "tumor average cell volume", "tumor healthy cell cycle time", "tumor cancer cell cycle time",
                                     "biopsy aggressiveness", "proliferative percentage", "migratory percentage", "cancerous percentage",
                                     "neutral percentage", "apoptotic percentage", "quiescent percentage", "average cell volume", "healthy cell cycle time",
                                     "cancer cell cycle time", "cancer het", "healthy het", "pop count", "p0", "p1", "p2", "p3"])

    # For every file, get the biopsy information from the JSON file. Perform several
    # analyses and data visualization techniques on the biopsy data.
    for f in ABM.get_files(args.files):
        print("processing " + f + "...")
        merged_data = merge_across_files(f)
        max_r = int(max(merged_data.keys(), key=int)) # maximum radius for the tumor in this file

        # Make a dataframe for this tumor and add the tumor aggressiveness score, tumor heterogeneity
        # and cell population information, and radii from this tumor.
        file_df = pd.DataFrame({})
        tumor_infos = merged_data['-1'][0]
        file_df["radius"] = pd.Series([int(r) / max_r for r in merged_data if int(r) >= 0])
        file_df["tumor aggressiveness"] = tumor_infos[0]
        file_df["tumor prolif percentage"] = tumor_infos[1]
        file_df["tumor migratory percentage"] = tumor_infos[2]
        file_df["tumor cancer percentage"] = tumor_infos[3]
        file_df["tumor average cell volume"] = tumor_infos[8]
        file_df["tumor healthy cell cycle time"] = tumor_infos[10]
        file_df["tumor cancer cell cycle time"] = tumor_infos[12]

        # Extract the heterogeneity and population information from the filename and
        # add them to the DataFrame.
        het, pm, pops, n_pops = parse_filename(f)
        file_df["cancer het"] = het
        file_df["healthy het"] = pm
        file_df["pop count"] = n_pops

        # Add a 1 to the dataframe if the tumor contains the population, and a 0 otherwise.
        if pops.__contains__('0'):
            file_df["p0"] = 1
        else:
            file_df["p0"] = 0

        if pops.__contains__('1'):
            file_df["p1"] = 1
        else:
            file_df["p1"] = 0

        if pops.__contains__('2'):
            file_df["p2"] = 1
        else:
            file_df["p2"] = 0

        if pops.__contains__('3'):
            file_df["p3"] = 1
        else:
            file_df["p3"] = 0


        # Extract data from the tumor and store it in pandas Series.
        biopsy_ags = pd.Series([b[0] for r in merged_data for b in merged_data[r]])
        prolif= pd.Series([b[1] for r in merged_data if int(r) >= 0 for b in merged_data[r]])
        migrat = pd.Series([b[2] for r in merged_data if int(r) >= 0 for b in merged_data[r]])
        cancer = pd.Series([b[3] for r in merged_data if int(r) >= 0 for b in merged_data[r]])
        neutral = pd.Series([b[4] for r in merged_data if int(r) >= 0 for b in merged_data[r]])
        apoptotic = pd.Series([b[5] for r in merged_data if int(r) >= 0 for b in merged_data[r]])
        quiescent = pd.Series([b[6] for r in merged_data if int(r) >= 0 for b in merged_data[r]])
        vol = pd.Series([b[8] for r in merged_data if int(r) >= 0 for b in merged_data[r]])
        healthy_time = pd.Series([b[10] for r in merged_data if int(r) >= 0 for b in merged_data[r]])
        cancer_time = pd.Series([b[12] for r in merged_data if int(r) >= 0 for b in merged_data[r]])

        # Add the data from the Series above to the dataframe.
        file_df["biopsy aggressiveness"] = biopsy_ags
        file_df["proliferative percentage"] = prolif
        file_df["migratory percentage"] = migrat
        file_df["cancerous percentage"] = cancer
        file_df["neutral percentage"] = neutral
        file_df["apoptotic percentage"] = apoptotic
        file_df["quiescent percentage"] = quiescent
        file_df["average cell volume"] = vol
        file_df["healthy cell cycle time"] = healthy_time
        file_df["cancer cell cycle time"] = cancer_time

        # Concatenate this tumor's dataframe to the overall dataframe storing data for all the tumors.
        # Uses dict
        total_df = pd.concat([total_df, file_df], sort=False)

        # Graph various features of the tumor at different radii. Also perform the
        # log likelihood analysis and make heatmaps of the log likelihood.
        graph_data(merged_data, max_r)

        # Merge the equivalence p-value information together across files.
        # Uses dict
        p = stat_analysis(merged_data)
        s, ns = analyze_p(p, max_r)
        if merged_nonsig:
            merged_nonsig = merge_dicts(merged_nonsig, ns)
        else:
            merged_nonsig = ns

        if merged_sig:
            merged_sig = merge_dicts(merged_sig, s)
        else:
            merged_sig = s


        # Get the radii with the greatest likelihood of representing this tumor.
        # Uses dict
        l_by_r = get_likelihoods_by_rad(merged_data)
        max_l = float(calc_max_likelihood(l_by_r)) / max_r
        r_max_likelihoods.append(max_l)
        min_l = float(calc_min_likelihood(l_by_r)) / max_r
        r_min_likelihoods.append(min_l)

    # convert df to csv

    # Find the percent radius with the maximum log likelihood across all the tumors.
    # Uses dict
    r_max_likelihoods = np.asarray(r_max_likelihoods)
    max_tumor_l = np.mean(r_max_likelihoods)
    max_std = np.std(r_max_likelihoods)
    print("average fraction of total radius away from tumor core with max likelihood: " + str(max_tumor_l))
    print("standard deviation: " + str(max_std))

    # Find the percent radius with the minimum log likelihood across all the tumors.
    # Uses dict
    r_min_likelihoods = np.asarray(r_min_likelihoods)
    min_tumor_l = np.mean(r_min_likelihoods)
    min_std = np.std(r_min_likelihoods)
    print("average fraction of total radius away from tumor core with min likelihood: " + str(min_tumor_l))
    print("standard deviation: " + str(min_std))
    vis_p(merged_sig, merged_nonsig)


    # For the range of minimum and maximum log likelihood, as well as the hard-coded hand-drawn
    # range found on the equivalence test violin plot, make parity plots of the various features.
    # Uses DF
    for rnge in [[min_tumor_l - min_std, min_tumor_l + min_std], [max_tumor_l - max_std, max_tumor_l + max_std], [0.4, 0.5]]:
        graph_ags_score_parity(total_df, rnge[0], rnge[1])


# -------------------- UTILITY FUNCTIONS --------------------------


# Function: hex_to_cart
# Given a list of x, y, z, hexagonal (cube) coordinates, converts them to Cartesian (axial) coordinates.
def hex_to_cart(hex_coord):
    x = hex_coord[0]
    y = hex_coord[2]
    return [x, y]

# Function: key_with_max_val
# Finds and returns the key in a dictionary with the maximum value.
def key_with_max_val(d):
    vals = list(d.values())
    keys = list(d.keys())
    return keys[vals.index(max(vals))]


# Function: key_with_min_val
# Finds and returns the key in a dictionary with the minimum value.
def key_with_min_val(d):
    vals = list(d.values())
    keys = list(d.keys())
    return keys[vals.index(min(vals))]


# Function: parse_filename
# Parses the file name of a JSON file to get the healthy and cancer heterogeneity,
# the populations in the tumor, and the number of populations.
def parse_filename(f):
    start = f.find("heterogeneity_") + 14
    het = (int(f[start:start + 4]) - 1000) / 10
    pm = (int(f[start + 7:start + 11]) - 1000) / 10
    end = f.find("_", start + 12)
    p = f[start + 14:end]
    pops = [pop for pop in p]
    n_pops = int(len(pops))
    return het, pm, pops, n_pops


# -------------------- EQUIVALENCE TEST FUNCTIONS --------------------------


# Function: vis_p
# Creates a violin plot of radii with significant p-values. merged_sig and merged_nonsig are dictionaries mapping each feature to
# a list of radii where the biopsies are significantly similar or non-similar to the tumor feature, respectively.
def vis_p(merged_sig, merged_nonsig):
    # Create a dataframe. Add the first feature to the dataframe.
    feat = 0
    s = merged_sig[feat]
    ns = merged_nonsig[feat]
    sig = pd.DataFrame(s, columns=["Percent radius from tumor core"])
    nonsig = pd.DataFrame(ns, columns=["Percent radius from tumor core"])
    sig["significance"] = "significantly similar"
    sig["feature"] = features[feat]
    nonsig["significance"] = "non-significant"
    nonsig["feature"] = features[feat]
    all = pd.concat([sig, nonsig])
    del merged_sig[feat]
    del merged_nonsig[feat]

    # Add the rest of the features to the dataframe.
    for next_feat in merged_sig:
        s = merged_sig[next_feat]
        ns = merged_nonsig[next_feat]
        sig = pd.DataFrame(s, columns=["Percent radius from tumor core"])
        nonsig = pd.DataFrame(ns, columns=["Percent radius from tumor core"])
        sig["significance"] = "significantly similar"
        sig["feature"] = features[next_feat]
        nonsig["significance"] = "non-significant"
        nonsig["feature"] = features[next_feat]
        both = pd.concat([sig, nonsig])
        all = pd.concat([both, all])

    # Create the violin plot from all the data.
    ax = seaborn.violinplot(x="Percent radius from tumor core", y="feature", hue="significance", split=True, data=all, orient='h', cut=0, inner="point")
    plt.title("Similarity of Biopsy Features to Tumor Features")
    plt.ylabel("Similarity of Biopsy to Tumor")
    plt.show()



# Function: stat_analysis
# Implements statistical analysis on the given data. Performs an equivalence test on each of the features of interest between all the biopsies in each radius (sample)
# and the feature of the whole tumor (population). Returns a dictionary mapping the position of each feature to a dictionary mapping each radius to the p-value of
# the equivalence test performed on the biopsies at that radius.
def stat_analysis(data):
    tumor_infos = data['-1'][0]
    p_vals_feat = {}

    # For every feature of interest (aggressiveness score, prolif percentage, migrat percentage,
    # cancer percentage, and cancer cell cycle time), perform an equivalence test for each tumor
    # between all the biopsies at each radius and the feature of the tumor overall.
    for feat in [0, 1, 2, 3, 12]:
        p_vals_rad = {}
        mu = tumor_infos[feat]
        range = 0.20
        for r in data:
            if r != '-1':
                sample = []
                for b in data[r]:
                    sample.append(b[feat])
                sample = np.asarray(sample).astype(np.float)
                p_vals_rad[r] = equivalence_test(sample, mu, range)
        p_vals_feat[feat] = p_vals_rad
    return p_vals_feat


# Function: analyze_p
# Searches through data to separate the data into significant radii and non-significant radii. Returns two dictionaries,
# each mapping each feature in data to a list of the radii where the feature is significantly similar/non-significant.
def analyze_p(data, n_tests):
    sig_by_feat = {}
    nonsig_by_feat = {}
    for feat in data:
        sig = []
        nonsig = []
        for r in data[feat]:
            p = data[feat][r]
            if p[0] < (alpha / n_tests) and p[1] < (alpha / n_tests):
                sig.append(int(r) / n_tests)
            else:
                nonsig.append(int(r) / n_tests)
        sig_by_feat[feat] = sig
        nonsig_by_feat[feat] = nonsig
    return sig_by_feat, nonsig_by_feat


# Function: equivalence_test
# Performs a 1-sample equivalence test between the sample and mu, the population mean.
def equivalence_test(sample, mu, range):
    d1 = -range * mu
    d2 = range * mu
    n = len(sample)
    df = n - 1
    x_bar = np.mean(sample)
    s = np.std(sample)
    denom = s / math.sqrt(n)
    if denom == 0:
        t1 = 1
        t2 = 1
    else:
        t1 = ((x_bar - mu) - d1) / denom
        t2 = ((x_bar - mu) - d2) / denom
    p1 = (1 - stats.t.cdf(math.fabs(t1), df)) * 2
    p2 = (1 - stats.t.cdf(math.fabs(t2), df)) * 2
    return [p1, p2]


# -------------------- DATA VISUALIZATION FUNCTIONS --------------------------


# Function: graph_data
# Creates graphs/plots to visualize the given data, which is assumed to be a dict.
def graph_data(data, max_r):
    # Graph the percent of proliferative cells.
    prolif_data = separate_rad_y_avg(data, 1, max_r)
    plt.plot(prolif_data.keys(), prolif_data.values(), 'b', label='Proliferative Cell Percentage')

    # Graph the percent of migratory cells.
    migrat_data = separate_rad_y_avg(data, 2, max_r)
    plt.plot(migrat_data.keys(), migrat_data.values(), 'r', label='Migratory Cell Percentage')

    # Graph the percent of cancerous cells.
    cancer_data = separate_rad_y_avg(data, 3, max_r)
    plt.plot(cancer_data.keys(), cancer_data.values(), 'g', label='Cancerous Cell Percentage')


    plt.xlabel('Percent distance from tumor core')
    plt.ylabel('Percent of cells in biopsy')
    plt.title('Average Proliferative, Migratory, and Cancerous Cell Percentage in Biopsies')
    plt.legend(loc='upper right')
    plt.show()

    graph_rad_ags(data, max_r)
    graph_rad_cancer_time(data, max_r)

    vis_likelihood(data)


# Function: separate_x_y
# Given a 2D array of data, separates the data at the given indices into two
# 1D arrays and returns them.
def separate_x_y(data, ind, dep, max_r):
    x = []
    y = []
    for rad in data:
        for elem in data[rad]:
            if elem[ind] != -1:
                x.append(elem[ind]) / max_r
                y.append(elem[dep])
    return x, y

# Function: separate_rad_y_avg
# Creates a dict mapping radius to the average of a specified type of data.
def separate_rad_y_avg(data, dep, max_r):
    avg_data = {}
    for rad in data:
        if rad != '-1':
            y = []
            for elem in data[rad]:
                y.append(elem[dep])
            y = np.asarray(y)
            avg_data[float(rad) / max_r] = np.mean(y)
    return avg_data


# Function: graph_ags_score_parity
# Makes parity plots for the aggressiveness score, the proliferative percentage, the migratory percentage, the cancerous percentage,
# and the cancer cell cycle time. Plots the feature's value in biopsies at each radius against the feature's value in the tumors as a whole.
# Colors each graph by the radius, population count, cancer heterogeneity, healthy heterogeneity, or presence/absence of pop 0, 1, 2, 3.
def graph_ags_score_parity(total_df, low, high):
    # For each coloring scheme, make parity plots for all the features of aggressiveness.
    for color in ["radius", "pop count", "cancer het", "healthy het", "p0", "p1", "p2", "p3"]:
        range_data = total_df.loc[(total_df['radius'] >= low) & (total_df['radius'] <= high)]
        range_data.plot.scatter(x="biopsy aggressiveness", y="tumor aggressiveness", c=color, colormap='Wistia')
        plt.title("Parity Plot of Aggressiveness Scores Between Radii " + str(low) + " and " +  str(high))
        plt.xlim(0, 0.35)
        plt.ylim(0, 0.35)
        plt.show()

        range_data.plot.scatter(x="proliferative percentage", y="tumor prolif percentage", c=color, colormap='Wistia')
        plt.title("Parity Plot of Proliferative Percentages Between Radii " + str(low) + " and " + str(high))
        plt.xlim(0, 0.25)
        plt.ylim(0, 0.25)
        plt.show()

        range_data.plot.scatter(x="migratory percentage", y="tumor migratory percentage", c=color, colormap='Wistia')
        plt.title("Parity Plot of Migratory Percentages Between Radii " + str(low) + " and " + str(high))
        plt.xlim(0, 0.075)
        plt.ylim(0, 0.075)
        plt.show()

        range_data.plot.scatter(x="cancerous percentage", y="tumor cancer percentage", c=color, colormap='Wistia')
        plt.title("Parity Plot of Cancerous Percentages Between Radii " + str(low) + " and " + str(high))
        plt.xlim(0, 1.0)
        plt.ylim(0, 1.0)
        plt.show()

        range_data.plot.scatter(x="cancer cell cycle time", y="tumor cancer cell cycle time", c=color, colormap='Wistia')
        plt.title("Parity Plot of Cancer Cell Cycle Times Between Radii " + str(low) + " and " + str(high))
        plt.xlim(0, 1750)
        plt.ylim(0, 1750)
        plt.show()


# Function: graph_rad_cancer_time
# Creates a line graph of the average cancerous cell cycle time in biopsies
# taken at each radius from the tumor core.
def graph_rad_cancer_time(data, max_r):
    avg_data = separate_rad_y_avg(data, 12, max_r)
    figure1 = plt.figure()
    plt.plot(avg_data.keys(), avg_data.values(), 'r:')
    plt.xlabel('Perent radius from tumor core')
    plt.ylabel('Average Cancerous Cell Cycle Time')
    figure1.suptitle('Average Cancerous Cell Cycle Time in Biopsies at Different Radii')
    plt.show()


# Function: graph_rad_cancer
# Creates a line graph of the average percentage of cancerous cells in biopsies
# taken at each radius from the tumor core.
def graph_rad_cancer(data, max_r):
    avg_data = separate_rad_y_avg(data, 3, max_r)
    figure1 = plt.figure()
    plt.plot(avg_data.keys(), avg_data.values(), 'b--')
    plt.xlabel('Percent radius from tumor core')
    plt.ylabel('Average percentage of cancerous cells')
    figure1.suptitle('Percentage of Cancerous Cells in Biopsies at Different Radii')
    plt.show()


# Function: graph_rad_migrat
# Creates a line graph of the average percentage of migratory cells in biopsies
# taken at each radius from the tumor core.
def graph_rad_migrat(data, max_r):
    avg_data = separate_rad_y_avg(data, 2, max_r)
    figure1 = plt.figure()
    plt.plot(avg_data.keys(), avg_data.values(), 'b--')
    plt.xlabel('Percent radius from tumor core')
    plt.ylabel('Average percentage of migratory cells')
    figure1.suptitle('Percentage of Migratory Cells in Biopsies at Different Radii')
    plt.show()



# Function: graph_rad_prolif
# Creates a line graph of the average percentage of proliferative cells in biopsies
# taken at each radius from the tumor core.
def graph_rad_prolif(data, max_r):
    avg_data = separate_rad_y_avg(data, 1, max_r)
    figure1 = plt.figure()
    plt.plot(avg_data.keys(), avg_data.values(), 'b--')
    plt.xlabel('Percent radius from tumor core')
    plt.ylabel('Average percentage of proliferative cells')
    figure1.suptitle('Percentage of Proliferative Cells in Biopsies at Different Radii')
    plt.show()


# Function: graph_rad_diff
# Creates a graph with radius from the tumor core on the x-axis and and average
# biopsy aggressiveness scores and total tumor aggressiveness score on the y-axis.
def graph_rad_ags(data, max_r):
    avg_data = separate_rad_y_avg(data, 0, max_r)
    figure1 = plt.figure()
    plt.plot(avg_data.keys(), avg_data.values(), 'b--')
    plt.xlabel('Percent adius from tumor core')
    plt.ylabel('Average aggressiveness score')
    figure1.suptitle('Average Biopsy Aggressiveness Scores at Different Radii')
    plt.show()


# -------------------- LOG LIKELIHOOD FUNCTIONS --------------------------


# Function: calc_likelihood
# Calculates the probability that the given biopsy came from the overall tumor based on the number
# of observed type 'feature' features.
def calc_likelihood(tumor_infos, biopsy, feature):
    M = np.average([t[14] for t in tumor_infos]) # avg total number of cells in the tumor
    n = M * np.average([t[feature] for t in tumor_infos]) # total number of type feature cells in the tumor
    N = biopsy[14] # total number of cells in biopsy
    k = N * biopsy[feature] # total number of type feature cells in the biopsy
    p = stats.hypergeom(M, n, N)
    prob = p.pmf(k)
    return prob


# Function: get_likelihoods
# Gets the log likelihoods of biopsies taken at each point coming from the overall tumor distribution.
# log likelihood = log(prob(%prolif)) + log(prob(%migrat)) + log(prob(%cancerous))
# Returns a list of likelihoods of all biopsies, and a list of cartesian coordinates of all biopsies.
def get_likelihoods(data):
    tumor_infos = data['-1']
    likelihoods = []
    coords = []
    for r in data:
        for b in data[r]:
            coords.append(b[15])
            # likelihood = 1
            likelihood = 0
            for state in range(1, 4):
                # likelihood *= calc_likelihood(tumor_infos, b, state)
                prob = calc_likelihood(tumor_infos, b, state)
                if prob != 0:
                    likelihood += math.log(prob)
            likelihoods.append(likelihood)
    cart_coord = [hex_to_cart(p) for p in coords]
    return likelihoods, cart_coord

# Function: get_likelihoods_by_rad
# Gets the log likelihoods of biopsies taken at each point coming from the overall tumor distribution.
# log likelihood = log(prob(%prolif)) + log(prob(%migrat)) + log(prob(%cancerous))
# Returns a dictionary mapping a radius to likelihoods of all biopsies at that radius
def get_likelihoods_by_rad(data):
    tumor_infos = data['-1']
    likelihoods_by_rad = {}
    for r in data:
        l_by_r = []
        for b in data[r]:
            # likelihood = 1
            likelihood = 0
            for state in range(1, 4):
                # likelihood *= calc_likelihood(tumor_infos, b, state)
                prob = calc_likelihood(tumor_infos, b, state)
                if prob != 0:
                    likelihood += math.log(prob)
            l_by_r.append(likelihood)
        likelihoods_by_rad[r] = l_by_r
    return likelihoods_by_rad


# Function: heatmap_likelihood
# Creates a heatmap of the likelihood of a biopsy taken at a certain point coming from the whole tumor.
def vis_likelihood(data):
    # Graph the likelihoods at each point.
    likelihoods, cart_coord = get_likelihoods(data)
    x = []
    y = []
    for coord in cart_coord:
        x.append(coord[0])
        y.append(coord[1])
    df = pd.DataFrame({'X':x,'Y':y, 'Log Likelihood':likelihoods})
    df_pivoted = df.pivot_table(values="Log Likelihood", index="Y", columns="X")
    ax = seaborn.heatmap(df_pivoted, cmap='PuBu')
    plt.title("Log Likelihood of Biopsies Taken at Different Points")
    plt.show()


# Function: calc_max_likelihood
# Finds and returns the radius with the highest average likeliness.
def calc_max_likelihood(l_by_r):
    for r in l_by_r:
        l_by_r[r] = np.mean(l_by_r[r])
    if '-1' in l_by_r:
        del l_by_r['-1']
    max_l_r = key_with_max_val(l_by_r)
    return max_l_r


# Function: calc_min_likelihood
# Finds and returns the radius with the lowest average likeliness.
def calc_min_likelihood(l_by_r):
    for r in l_by_r:
        l_by_r[r] = np.mean(l_by_r[r])
    if '-1' in l_by_r:
        del l_by_r['-1']
    min_l_r = key_with_min_val(l_by_r)
    return min_l_r


# -------------------- MERGING/FORMATTING FUNCTIONS --------------------------


# Function: merge_across_file
# For every file in the inputted directory, concatenates the aggressiveness score differences
# for each radius first across every seed in each file, then across every file into one list,
# mapping each radius to its corresponding list of aggressiveness score differences.
# Format of merged_data: dict mapping radii to numpy arrays containing differences between
# aggressiveness scores of biopsies at that radii and tumor aggressiveness score
def merge_across_files(f):
    with open(f) as file:
        file_data = json.load(file)
        file_data, file_tumor = merge_across_seed(file_data)
        return file_data


# Function: merge_across_seed
# For every seed in the file arg, merges the aggressiveness score differences for each
# radius across every seed in the file into one list, leaving each radius mapped to
# its corresponding list.
def merge_across_seed(arg):
    arg_merge_rad = merge_across_rad(arg)
    arg_merge_seed = arg_merge_rad['1']
    tumor_info = arg_merge_rad['-1']
    del arg_merge_rad['-1']
    for s in arg_merge_rad:
        rad_dict = arg_merge_rad[s]
        arg_merge_seed = merge_dicts(arg_merge_seed, rad_dict)
    arg_merge_seed['-1'] = [tumor_info]
    return arg_merge_seed, tumor_info


# Function: merge_across_rad
# For every seed in the file arg, for every radius in each seed, merges the aggressiveness
# scores of each biopsy at that radius and deletes the tumor aggressiveness score from the dict.
def merge_across_rad(arg):
    arg_merge_rad = {}
    tumor_ags = arg['-1'][0]
    for s in arg:
        if s != '-1':
            arg_merge_rad[s] = calc_ags_diff(arg[s]) # merges each radius's biopsies
    arg_merge_rad['-1'] = arg['-1']
    return arg_merge_rad


# Function: calc_ags_diff
# TO DO: CHECK IF THIS FUNCTION IS NECESSARY AND IF NOT, DELETE
# Takes in a dict that maps radius to an array of arrays containing biopsy aggressiveness scores and
# information. Maps each radius to a list of lists of biopsy information.
def calc_ags_diff(arg_rad):
    arg_diff = {}
    for r in arg_rad:
        biopsies = arg_rad[r]
        biopsies = np.asarray(biopsies)
        arg_diff[r] = biopsies
    return arg_diff


# Function: merge_dicts
# Merges two dictionaries by concatenating values that map to the same keys.
# Assumption: dict1 and dict2 have identical keys, but each key can have different
# values between the two dictionaries.
def merge_dicts(dict1, dict2):
    if not dict1:
        return dict2
    elif not dict2:
        return dict1
    else:
        merged = {}
        for key1 in dict1:
            if key1 in dict2:
                merged[key1] = np.concatenate([dict1[key1], dict2[key1]])
            else:
                merged[key1] = dict1[key1]
        for key2 in dict2:
            if key2 not in merged:
                merged[key2] = dict2[key2]
        return merged


# If statement to run main method
if __name__ == "__main__":
    main()
