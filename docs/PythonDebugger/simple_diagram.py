#!/usr/bin/env python3
"""
Script that show a basic Airflow + Celery Topology
"""
try:
    import sys
    import argparse
    from argparse import ArgumentTypeError
    import traceback
    from diagrams import Cluster, Diagram
    from diagrams.onprem.workflow import Airflow
    from diagrams.onprem.queue import Celery
except ImportError:
    print("Exception while importing modules, did you run 'pip install?':")
    print("-" * 60)
    traceback.print_exc(file=sys.stderr)
    print("-" * 60)
    print("Starting the debugger", file=sys.stderr)
    breakpoint()
    raise


def generate_diagram(diagram_file: str, workers_n: int):
    """
    Generate the network diagram for the given number of workers
    @param diagram_file: Where to save the diagram
    @param workers_n: Number of workers
    """
    with Diagram("Airflow topology", filename=diagram_file, show=False):
        with Cluster("Airflow"):
            airflow = Airflow("Airflow")

        with Cluster("Celery workers"):
            workers = []
            for i in range(workers_n):
                workers.append(Celery(f"Worker {i + 1}"))
        airflow - workers


def valid_range(value: str, upper: int = 10):
    try:
        int_val = int(value)
        if 1 <= int_val <= upper:
            return int_val
        raise ArgumentTypeError(f"Not true: 1<= {value} <= {upper}")
    except ValueError:
        raise ArgumentTypeError(f"'{value}' is not an Integer")


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(
        description="Generate network diagrams for examples used on this tutorial",
        prog=__file__
    )
    PARSER.add_argument(
        '--workers',
        action='store',
        type=valid_range,
        default=1,
        help="Number of workers"
    )
    PARSER.add_argument(
        'diagram',
        action='store',
        help="Name of the network diagram to generate"
    )
    ARGS = PARSER.parse_args()

    generate_diagram(ARGS.diagram, ARGS.workers)
