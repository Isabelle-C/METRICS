import os
import json
import csv
import re
import numpy as np
import pandas as pd
# import tarfile as tf
from itertools import groupby, product
from functools import reduce
from argparse import ArgumentParser
# from math import sqrt


# FIELDS = ["PARAM", "PERC", "AUX", "INIT", "CONFIG"]
# FIELDS = []
# SEED = "[0-9]{2}"
# REGEX = {
#     "PARAM": "[a-z_]*",
#     "PERC": "[0-9]{3,4}",
#     "INIT": "[H|C|S][HSC0-9]*",
#     "CONFIG": "[23][CMSR][CMSR]",
#     "AUX": "([a-z]{2}[0-9]+[_]*)*"
# }
# PATTERNS = [REGEX[i] for i in FIELDS]

# ------------------------------------------------------------------------------

def get_parser(desc, setup = True):
    parser = ArgumentParser(description=desc)
    if setup:
        parser.add_argument(dest="setup",
            help="Path to XML setup file describing the simulations")
    parser.add_argument("--nosave", default=False, dest="nosave",
        action='store_true', help="Do not save results to files")
    parser.add_argument("--noprint", default=False, dest="noprint",
        action='store_true', help="Do not print results to console")
    return parser

# def clean_name(name):
#     return re.sub("^_", "", re.sub("__+", "_", "_".join(name)))

# def remove_defaults(command):
#     defaults = ["--start 0 ", "--end 1 ", "--days 21 ",
#         "-d 2D ", "--metares C ", "--sigres C ", "--cells H ", "--ratio 100 "]
#     for d in defaults:
#         command = command.replace(d," ")
#     return re.sub("  +", " ", command)

# def compile_name(fields, parsed, inds):
#     split_name = [""] * 5;
#     icol, irow = inds[0]
#     split_name[irow] = fields[0]
#     split_name[icol] = fields[1]
#     split_name[inds[2][0]] = parsed[inds[2][0]][0]
#     split_name[inds[2][1]] = parsed[inds[2][1]][0]
    
#     if len(inds[1]) == 1:
#         split_name[inds[1][0]] = fields[2]
#     else:
#         split_name[inds[2][2]] = parsed[inds[2][2]][0]

#     return clean_name(split_name)

def format_json(jn):
    jn = jn.replace(":", ": ")
    for arr in re.findall('\[\n\s+[A-z0-9$",\-\.\n\s]*\]', jn):
        jn = jn.replace(arr, re.sub(r',\n\s+', r',', arr))
    jn = re.sub(r'\[\n\s+([A-Za-z0-9,"$\.\-]+)\n\s+\]', r'[\1]', jn)
    jn = jn.replace("],[", "],\n            [")
    return jn

def get_files(arg):
    if arg[-1] == "/":
        return [arg + f for f in os.listdir(arg) if is_tar(f) or is_json(f)]
    else:
        assert is_tar(arg) or is_json(arg)
        return [arg]

def is_tar(f):
    return f[-7:] == ".tar.xz"

def is_json(f):
    return f[-5:] == ".json"

def is_pkl(f):
    return f[-4:] == ".pkl"

def load_tar(tar_file, member):
    f = tar_file.extractfile(member)
    contents = [a.decode("utf-8") for a in f.readlines()]
    return json.loads("".join(contents))

def load_json(json_file):
    return json.load(open(json_file, "r"))

def load_csv(csv_file):
    with open(csv_file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        contents = [row for row in reader]
    return contents

def clean_name(key, value, pads):
    if key in pads.keys() and value.replace('.','',1).isdigit():
        value = str(int(float(value)*pads[key][0])).zfill(pads[key][1])
    value = value.replace(",","")
    return (key, value)

def make_name(name, combo, tags):
    padding = re.findall('{([A-z0-9\_]+)\|([0-9]+),([0-9]+)}', name)
    pads = {"{" + p[0] + "}" : (int(p[1]), int(p[2])) for p in padding}
    name = re.sub('\|([0-9]+),([0-9]+)','', name)
    singles, paired = make_replacements(tags, combo)
    replacements = [clean_name(k, v, pads) for k, v in singles + paired]
    return reduce(lambda a, kv: a.replace(*kv), replacements, name)

def make_replacements(tags, combo):
    singles = [("{" + t + "}", c) for t, c in zip(tags, combo) if type(c) is not tuple]
    paired = [("{" + t + "_" + str(i) + "}", cc) for t, c in zip(tags, combo) for i, cc in enumerate(c) if type(c) is tuple]
    return singles, paired

def get_rows(options):
    if len(options) < 1:
        return ["-"]
    elif len(options) < 3:
        return options[0]
    else:
        rows = [op for i, op in enumerate(options) if i%2 == 0]
        return pd.MultiIndex.from_product(rows)

def get_cols(options):
    if len(options) < 2:
        return ["-"]
    elif len(options) < 4:
        return options[1]
    else:
        cols = [op for i, op in enumerate(options) if i%2 != 0]
        return pd.MultiIndex.from_product(cols)

def get_row(option):
    if len(option) < 1:
        return "-"
    elif len(option) < 3:
        return option[0]
    else:
        rows = [op for i, op in enumerate(option) if i%2 == 0]
        return tuple(rows)

def get_col(option):
    if len(option) < 2:
        return "-"
    elif len(option) < 4:
        return option[1]
    else:
        cols = [op for i, op in enumerate(option) if i%2 != 0]
        return tuple(cols)

def df_to_combo(row, col, n):
    if n > 3:
        n = len(row) + len(col)
        return [row[int(i/2)] if i%2 == 0 else col[int((i - 1)/2)] for i in range(n)]
    elif n == 3:
        return [row[0], col, row[1]]
    elif n == 2:
        return [row, col]
    elif n == 1:
        return [row]
    else:
        return []

def find_setup(setup):
    # Get full path to location of setup file.
    full_path = os.getcwd() + "/" + setup
    split_path = full_path.split("/")
    file_path = "/".join(split_path[0:-1]) + "/"

    # Get setup file name without extension.
    split_setup = setup.split("/")
    file_prefix = split_setup[-1].replace(".xml","")

    return file_path, file_prefix

TAG_MATCH = '([A-z0-9]*)';
OPTIONS_MATCH = '\(([A-z0-9,\.\|\*:\)\()]*)\)';

def parse_setup(setup):
    # Load xml file
    with open(setup, 'r') as file:
        xml = [row for row in file]

    all_tags = []
    all_options = []
    tags = []

    # Search through XML for {tag:(options)}
    for row in xml:
        matches = re.findall("\{(" + TAG_MATCH + "::" + OPTIONS_MATCH + ")\}", row)
        if (matches):
            [all_tags.append(m[1]) for m in matches]
            [all_options.append(m[2].split('|')) for m in matches]
    
    # Sort for paired tags. Previously used set, but want to have consistent order
    tags = []
    for t in all_tags:
        if t not in tags:
            tags.append(t)
    pairs = []

    if len(tags) < len(all_tags):
        counts = [all_tags.count(tag) for tag in tags]
        pairs = [t for t, c in zip(tags, counts) if c > 1]
        inds = { p : [i for i, t in enumerate(all_tags) if t == p] for p in pairs }
    
    # Update template.
    template = "".join(xml)
    for t in tags:
        if t not in pairs:
            template = re.sub("\{" + t + "::" + OPTIONS_MATCH + "\}", "{" + t + "}", template)
        else:
            for i in range(len(inds[t])):
                template = re.sub("\{" + t + "::" + OPTIONS_MATCH + "\}", "{" + t + "_" + str(i) + "}", template, 1)

    # Sort options and consolidate into tuples if there are pairs
    options = []
    for tag in tags:
        if tag not in pairs:
            options.append(all_options[all_tags.index(tag)])
        else:
            ops = [all_options[i] for i in inds[tag]]
            options.append([x for x in zip(*ops)])

    ordering = list(np.argsort([len(op) for op in options]))
    ordering.reverse()
    options_ordered = [options[i] for i in ordering]
    tags_ordered = [tags[i] for i in ordering]
    
    # Make all combinations of options
    combos = list(product(*options_ordered))

    return tags_ordered, pairs, options_ordered, combos, template

# ------------------------------------------------------------------------------

# def get_seed_matches(matches):
#     return [int(m.group(0)[1:-1]) for x in matches
#         for m in [re.search("_" + SEED + "_", x)] if m]

# def get_matches(files, remove, pattern, irow, icol):
#     matches = [m.group(0)[:remove].replace(".","_")
#         for x in files for m in [re.search(pattern, x)] if m]
#     rows = get_field_matches(matches, PATTERNS[irow])
#     cols = get_field_matches(matches, PATTERNS[icol])
#     return matches, rows, cols

# def get_field_matches(matches, pattern):
#     return [m.group(0)[1:-1] for x in matches
#         for m in [re.search("_" + pattern + "_", x)] if m]

# def get_regex(field, inds, parsed, g):
#     i = FIELDS.index(field)
#     return PATTERNS[i] if i in inds[0] else g if i in inds[1] else parsed[i][0]

# def get_patterns(name, inds, parsed, g):
#     # Get regex components.
#     parameter = get_regex("PARAM", inds, parsed, g)
#     percent = get_regex("PERC", inds, parsed, g)
#     aux = get_regex("AUX", inds, parsed, g)
#     init = get_regex("INIT", inds, parsed, g)
#     config = get_regex("CONFIG", inds, parsed, g)

#     # Get patterns.
#     json_pattern = name + "_" + parameter + "_" + percent + "_" + aux + "_" + init + "_" + config
#     json_pattern = re.sub("__+", "_", json_pattern) + "_" + SEED + "\.json"
#     tar_pattern = json_pattern.replace("_" + SEED + "\.json", "\.tar\.xz")
#     pkl_pattern = json_pattern.replace("_" + SEED + "\.json", "\.pkl")

#     return json_pattern, tar_pattern, pkl_pattern

# ------------------------------------------------------------------------------

# def get_setup(setup):
#     jsn = load_json(setup)
#     summary = [jsn["summary"][f] for f in FIELDS]

#     # Get which fields are varied.
#     i_var = [i for i,x in enumerate(summary) if x == "*"]
#     i_static = [i for i,x in enumerate(summary) if x == []]
#     i_group = list(set(range(0,5)) - set(i_var + i_static))

#     # Check summary.
#     assert len(i_var) == 2
#     assert len(i_group) < 2

#     # Flip order of percent and parameter for clarity
#     if set(i_var) == set([0,1]):
#         i_var = [1,0]

#     # Flip order of config and aux for clarity
#     if set(i_var) == set([2,4]):
#         i_var = [4,2]

#     # Flip order of config and init for clarity
#     if set(i_var) == set([3,4]):
#         i_var = [4,3]

#     return jsn, i_var, i_static, i_group

# def parse_setup(setup):
#     jsn, i_var, i_static, i_group = get_setup(setup)
#     parsed = [parse_field(f, jsn) for f in FIELDS]

#     # Specify rows, cols, and groups.
#     i_col, i_row = i_var
#     cols = parsed[i_col]
#     rows = parsed[i_row]
#     groups = ["_" + a for a in parsed[i_group[0]]] if i_group else [""]

#     return jsn, parsed, rows, cols, groups, (i_var, i_group, i_static)

# # def convert_setup(setup):
# #     jsn, i_var, i_static, i_group = get_setup(setup)
# #     parsed = [parse_field(f, jsn) for f in FIELDS]
# #     convert = [convert_field(f, jsn) for f in FIELDS]

# #     if 0 in i_static and 1 in i_static:
# #         commands = [b + " " + c + " " + d for b in convert[2] for c in convert[3] for d in convert[4]]
# #     else:
# #         convert_params = [a[0] + " " + ",".join([a[1].upper() + ":" + c for c in b])
# #             for a, b in zip(convert[0], convert[1])]
# #         commands = [a + " " + b + " " + c + " " + d
# #             for a in convert_params
# #             for b in convert[2]
# #             for c in convert[3]
# #             for d in convert[4]]

# #     names = [clean_name([a, b, c, d, e])
# #         for a in parsed[0]
# #         for b in parsed[1]
# #         for c in parsed[2]
# #         for d in parsed[3]
# #         for e in parsed[4]]

# #     return {a : b for a, b in zip(names, commands)}
    
# def parse_field(field, jsn):
#     if field == "PARAM":
#         return jsn["parameters"] if jsn["parameters"] else [""]
#     elif field == "PERC":
#         return jsn["percents"] if jsn["percents"] else [""]
#     elif field == "INIT":
#         return parse_init(jsn["initialization"])
#     elif field == "CONFIG":
#         return parse_config(jsn["configuration"])
#     elif field == "AUX":
#         return parse_aux(jsn["auxiliary"])
#     else:
#         return []

# def parse_config(jsn):
#     return [dim[0] + meta[0].upper() + sig[0].upper()
#         for dim in jsn["dimension"]
#         for meta in jsn["metabolism"]
#         for sig in jsn["signaling"]]

# def parse_init(jsn):
#     cells = jsn["cells"]
#     ratios = jsn["ratios"]
#     codes = [[a for pop in zip(cells, [str(r).zfill(2) for r in ratio])
#         for a in pop] for ratio in zip(*ratios)]
#     codes = [[a if a != "100" else "" for a in c] for c in codes]
#     return ["".join(c) for c in codes]

# def parse_aux(jsn):
#     codes = [[x[1] + i for i in x[3]] for x in jsn]
#     return ["_".join(x) for x in list(itertools.product(*codes))]

# def convert_field(field, jsn):
#     if field == "PARAM":
#         return convert_param(jsn)
#     elif field == "PERC":
#         return convert_perc(jsn)
#     elif field == "INIT":
#         return convert_init(jsn["initialization"])
#     elif field == "CONFIG":
#         return convert_config(jsn["configuration"])
#     elif field == "AUX":
#         return convert_aux(jsn["auxiliary"])
#     else:
#         return []

# def convert_config(jsn):
#     return [" ".join(["-d", d, "--metares", m[0].upper(), "--sigres", s[0].upper()])
#         for d in jsn["dimension"]
#         for m in jsn["metabolism"]
#         for s in jsn["signaling"]]

# def convert_init(jsn):
#     cells = ":".join(jsn["cells"])
#     ratios = [":".join([str(r) for r in ratio]) for ratio in zip(*jsn["ratios"])]
#     return [" ".join(["--cells", cells, "--ratio", r]) for r in ratios]

# def convert_param(jsn):
#     if not jsn["parameters"]:
#         return [""]
#     else:
#         return [["--param", p] for p in jsn["parameters"] for n in jsn["percents"]]

# def convert_perc(jsn):
#     if not jsn["percents"]:
#         return [""]
#     else:
#         percs = jsn["percents"]
#         if "pops" in jsn:
#             return [[a[0] + "." + a[1:] + ":" + c for c in b]
#                 for p in jsn["parameters"] for a, b in zip(percs, jsn["pops"])]
#         else:
#             return [[a[0] + "." + a[1:]] for p in jsn["parameters"] for a in percs]

# def convert_aux(jsn):
#     codes = [["--" + x[0] + " " + i for i in x[2]] for x in jsn]
#     return [" ".join(x) for x in list(itertools.product(*codes))]

def parse_fields(jsn):
    R = jsn["config"]["size"]["radius"]
    H = jsn["config"]["size"]["height"]
    time = [tp["time"] for tp in jsn["timepoints"]]
    pops = [p[0] for p in jsn["config"]["pops"]]
    types = [i for i in range(0,7)]
    return R, H, time, pops, types
