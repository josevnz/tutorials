"""
Wrapper around CLI applications that use Textual, now they can also be run as web applications.
"""
from argparse import ArgumentParser
from pathlib import Path

from textual_serve.server import Server

APPLICATIONS = [
    "esru_numbers",
    "esru_outlier",
    "esru_browser"
]
PORT = 8000


def main():
    parser = ArgumentParser(description="Browse user results")
    parser.add_argument(
        "--application",
        action="store",
        choices=APPLICATIONS,
        required=True,
        help=f"Applications that can run in server mode: {APPLICATIONS}"
    )
    parser.add_argument(
        "--port",
        action="store",
        default=PORT,
        help=f"Default port ({PORT})"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Enable debug mode"
    )
    parser.add_argument(
        "results",
        action="store",
        type=Path,
        nargs="*",
        help="Race results."
    )
    options = parser.parse_args()
    if options.results:
        cmd = f"{options.application} {''.join([str(result.resolve()) for result in options.results])}"
    else:
        cmd = f"{options.application}"
    server = Server(
        command=cmd,
        port=PORT
    )
    server.serve(options.debug)
