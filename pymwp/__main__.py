#!/usr/bin/env python3

"""Provides command line interface with arguments"""

import argparse
import sys
import logging
from typing import List, Optional

from .analysis import Analysis
from .version import __version__
from .file_io import default_file_out


def main():
    """Implementation of MWP analysis on C code in Python."""
    parser = argparse.ArgumentParser(prog='pymwp', description=main.__doc__)
    args = _parse_args(parser)

    if not args.file:
        parser.print_help()
        sys.exit(1)

    log_level = 40
    log_filename = args.logfile
    setup_logger(logging.FATAL - log_level, log_filename=log_filename)
    file_out = args.out or default_file_out(args.file)

    Analysis.run(args.file, file_out, args.no_save,
                 not args.no_cpp, args.cpp, args.cpp_args)


def _parse_args(
        parser: argparse.ArgumentParser,
        args: Optional[List] = None) -> argparse.Namespace:
    """Setup available program arguments."""
    parser.add_argument(
        "file",
        help="Path to C source code file",
        nargs="?"
    )
    parser.add_argument(
        "--outfile",
        action="store",
        dest="out",
        help="file for storing analysis result",
    )
    parser.add_argument(
        "--logfile",
        action="store",
        help="save log messages into a file",
    )
    parser.add_argument(
        "--no-save",
        action='store_true',
        help="skip writing result to file"
    )
    parser.add_argument(
        "--no-cpp",
        action='store_true',
        help="disable execution of C pre-processor on the input file"
    )
    parser.add_argument(
        '--cpp',
        action='store',
        default='gcc',
        help='path to C pre-processor on your system (default: gcc)',
    )
    parser.add_argument(
        '--cpp-args',
        action='store',
        default='-E',
        help='arguments to pass to C pre-processor (default: -E)',
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s " + __version__,
    )
    return parser.parse_args(args)


def setup_logger(
        level: int = logging.ERROR,
        log_filename: Optional[str] = None) -> None:
    """Create a configured instance of logger.

    Arguments:
        level: Describe the severity level of the logs to handle.
            see: https://docs.python.org/3/library/logging.html#levels
        log_filename: Write logging info to a file
    """
    fmt = "[%(asctime)s] %(levelname)s (%(module)s): %(message)s"
    date_fmt = "%H:%M:%S"
    formatter = logging.Formatter(fmt, datefmt=date_fmt)

    logger = logging.getLogger("pymwp")
    logger.setLevel(level)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if log_filename is not None:
        file_handler = logging.FileHandler(log_filename)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


if __name__ == '__main__':
    main()
