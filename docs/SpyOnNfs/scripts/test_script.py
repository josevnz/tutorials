#!/usr/bin/env python
"""
Simple script to simulate light activity on NFS drives
Author Jose Vicente Nunez (kodegeek.com@protonmail.com)
"""
import concurrent
import os
import time
from concurrent.futures import ThreadPoolExecutor, ALL_COMPLETED
from pathlib import Path
from argparse import ArgumentParser
import logging

logging.basicConfig(format='%(asctime)s %(message)s', encoding='utf-8', level=logging.DEBUG)


def forever_read(the_file: Path, verbose: bool = False):
    for line in continuous_read(the_file=the_file):
        if verbose:
            logging.warning(line.strip())


def continuous_read(the_file: Path):
    """
    Continuously read the contents of file
    :param the_file:
    :return:
    """
    with open(the_file, 'r') as file_data:
        file_data.seek(0, os.SEEK_END)
        while True:
            line = file_data.readline()
            if not line:
                time.sleep(0.1)
                continue
            yield line


def quick_read(the_file: Path, verbose: bool = False):
    """
    Red the whole file and close it once done
    :param verbose:
    :param the_file:
    :return:
    """
    with open(the_file, 'r') as file_data:
        for line in file_data:
            if verbose:
                logging.warning(line.strip())


if __name__ == "__main__":
    PARSER = ArgumentParser(description=__doc__)
    PARSER.add_argument(
        '--verbose',
        action='store_true',
        default=False,
        help='Enable verbose mode'
    )
    PARSER.add_argument(
        '--quick_read',
        type=Path,
        required=True,
        help='Read a file once'
    )
    PARSER.add_argument(
        '--follow',
        type=Path,
        required=True,
        help='Read a file continuously'
    )
    OPTIONS = PARSER.parse_args()
    try:
        with ThreadPoolExecutor(max_workers=3) as tpe:
            futures = [
                tpe.submit(forever_read, OPTIONS.follow, OPTIONS.verbose),
                tpe.submit(quick_read, OPTIONS.quick_read, OPTIONS.verbose)
            ]
            concurrent.futures.wait(futures, return_when=ALL_COMPLETED)
    except KeyboardInterrupt:
        pass