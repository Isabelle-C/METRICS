#!/usr/bin/env python3

import yaml
from metrics.workflows import run_parse_simulations, run_calculate_stats


def main() -> None:
    """
    TODO
    """
    with open("/Users/isabellechen/METRICS/src/metrics/config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

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
                run_calculate_stats(
                    database_path, simulation, seed, features, timepoints, **samples[sample]
                )


if __name__ == "__main__":
    main()
