#!/usr/bin/env python3
import os
import tarfile
from typing import Any
import warnings

import itertools

import yaml
from metrics.workflows import run_parse_simulations, run_calculate_analysis


warnings.simplefilter("ignore")


def untar_files(folder_path: str) -> None:
    """
    Untar all files in a specified folder path.

    Parameters
    ----------
    folder_path : str
        Path to the folder
    """
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if file_name.endswith(".tar.xz"):
            with tarfile.open(file_path, "r:xz") as tar:
                tar.extractall(folder_path)


def recursive_file_delete(folder_path: str) -> None:
    """
    Recursively delete all files in a specified folder path.

    Parameters
    ----------
    folder_path : str
        Path to the folder
    """
    for root, _, files in os.walk(folder_path):
        for file in files:
            if not file.endswith(".tar.xz"):
                file_path = os.path.join(root, file)
                os.remove(file_path)


def make_list_based_on_resolution(resolution: Any, range_param: list, is_seed: bool) -> list:
    """
    Create list based on specified resolution parameter, if applicable.

    Parameters
    ----------
    resolution: Union[float, str, int]

    range_param: list

    seed: bool

    Returns
    -------
    resolution_list : list
        List based on resolution parameters.
    """

    if resolution and resolution.lower() not in ("none", "None"):
        if is_seed:
            resolution_list = [
                str(x * resolution).zfill(2)
                for x in range(range_param[0], int(range_param[1] / resolution) + 1)
            ]
        else:
            resolution_list = [
                x * resolution for x in range(range_param[0], int(range_param[1] / resolution) + 1)
            ]
    else:
        if is_seed:
            resolution_list = [str(x).zfill(2) for x in range_param]
        else:
            resolution_list = range_param

    return resolution_list


def main() -> None:
    """
    TODO
    """

    filename = "./src/metrics/config.yaml"
    with open(filename, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        print(config)

    experiment_section = config["experiment"]

    database = experiment_section["database"]

    time_range = experiment_section["timepoints"]
    time_resolution = experiment_section["timepoint_resolution"]

    observation_time_range = experiment_section["observation_timepoints"]
    observation_time_resolution = experiment_section["observation_timepoint_resolution"]

    seed_range = experiment_section["seeds"]
    seed_resolution = experiment_section["seed_resolution"]

    seeds = make_list_based_on_resolution(seed_resolution, seed_range, True)
    timepoints = make_list_based_on_resolution(time_resolution, time_range, False)

    observation_timepoints = make_list_based_on_resolution(
        observation_time_resolution, observation_time_range, False
    )

    simulation_path = experiment_section["simulation_path"]

    tissue_heterogeneity = experiment_section["tissue_heterogeneity"]
    cancer_heterogeneity = experiment_section["cancer_heterogeneity"]

    contexts = experiment_section["contexts"]
    populations = experiment_section["populations"]

    for context, population, cancer_heterogeneity_level in itertools.product(
        contexts, populations, cancer_heterogeneity
    ):
        print(cancer_heterogeneity_level)
        if context == "C":
            simulation = f"{simulation_path}{context}_{population}_{cancer_heterogeneity_level}"
        elif context == "CH":
            simulation = f"{simulation_path}{context}_{population}_{cancer_heterogeneity_level}_{tissue_heterogeneity}"
        else:
            raise ValueError("Invalid context.")

        database_path = f"{database}{population}_{context}_{cancer_heterogeneity_level}.db"

        untar_files(simulation)
        untar_files(f"{simulation}.PARAM")

        if config["parse"]:
            for seed in seeds:
                run_parse_simulations(database_path, simulation, seed, timepoints)

        if config["analyze"]:
            analysis_params = config["analysis"]
            features = analysis_params["features"]
            samples = analysis_params["samples"]
            comparisons = analysis_params["comparisons"]

            for seed in seeds:
                run_calculate_analysis(
                    database_path,
                    simulation,
                    seed,
                    features,
                    timepoints,
                    observation_timepoints,
                    samples,
                    comparisons,
                )

        recursive_file_delete(simulation)
        recursive_file_delete(f"{simulation}.PARAM")


if __name__ == "__main__":
    main()
