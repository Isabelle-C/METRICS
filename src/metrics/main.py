#!/usr/bin/env python3
import os
from pathlib import Path

import yaml
from metrics.workflows import run_parse_simulations, run_calculate_analysis


def main() -> None:
    """
    TODO
    """
    parent_folder = Path.cwd().parent
    filename = "config.yaml"

    for subdir, dirs, files in os.walk(parent_folder):
        for file in files:
            if file == filename:
                file_path = os.path.join(subdir, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)
                break

    database_path = config["experiment"]["database"]
    simulation = config["experiment"]["simulation"]
    time_range = config["experiment"]["timepoints"]
    time_resolution = config["experiment"]["timepoint_resolution"]
    seed_range = config["experiment"]["seeds"]
    seed_resolution = config["experiment"]["seed_resolution"]

    if time_resolution and time_resolution not in ("none", "None"):
        timepoints = list(
            map(
                lambda x: x * time_resolution,
                range(time_range[0], int(time_range[1] / time_resolution) + 1),
            )
        )
    else:
        timepoints = time_range

    if seed_resolution and seed_resolution not in ("none", "None"):
        seeds = list(
            map(
                lambda x: str(x * seed_resolution).zfill(2),
                range(seed_range[0], int(seed_range[1] / seed_resolution) + 1),
            )
        )
    else:
        seeds = list(map(lambda x: str(x).zfill(2), seed_range))

    if config["parse"]:
        for seed in seeds:
            run_parse_simulations(database_path, simulation, seed, timepoints)

    if config["analyze"]:
        analysis_params = config["analysis"]
        features = analysis_params["features"]
        samples = analysis_params["samples"]

        for seed in seeds:
            for sample in samples:
                run_calculate_analysis(
                    database_path, simulation, seed, features, timepoints, **samples[sample]
                )


if __name__ == "__main__":
    main()
