#!/usr/bin/env python
"""
Generate network for NFS server and clients

See README.md on this directory for instructions on how to install!

Author Jose Vicente Nunez (kodegeek.com@protonmail.com)
"""
import argparse
import shutil

from diagrams import Cluster, Diagram
from diagrams.generic.os import RedHat
from diagrams.generic.os import Raspbian

if not shutil.which("dot"):
    raise NotImplementedError("Please make sure Graphviz 'dot' is on the path")


def diagram(diagram_name: str):
    with Diagram("NFS server and clients", filename=diagram_name, show=False):
        with Cluster("Servers"):
            servers = [
                Raspbian("Raspberry PI 4 - /suricatalog"),
                Raspbian("Orange PI 5 - /data")
            ]
        client = RedHat("Dmaf5 AMD")
        servers << client


if __name__ == "__main__":

    PARSER = argparse.ArgumentParser(
        description=__doc__,
        prog=__file__
    )
    PARSER.add_argument(
        'diagram',
        action='store',
        help="Name of the network diagram to generate"
    )
    ARGS = PARSER.parse_args()
    diagram(ARGS.diagram)
