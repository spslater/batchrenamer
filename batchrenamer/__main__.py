"""Run the batchrenamer as one"""
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser

from batchrenamer import BatchRenamer


def main():
    """Run when called from the command line"""
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        prog="brp",
    )
    parser.add_argument("filename", nargs="+", help="list of files to rename")
    parser.add_argument(
        "-a",
        "--auto",
        dest="autofiles",
        nargs="*",
        help="automated file to run",
        metavar="FILE",
    )
    cli_args = parser.parse_intermixed_args()
    # pylint: disable=not-callable
    BatchRenamer(*cli_args.filename, autofiles=cli_args.autofiles).run()


if __name__ == "__main__":
    main()
