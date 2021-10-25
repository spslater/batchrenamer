"""Run the batchrenamer as one"""
from argparse import ArgumentParser

from batchrenamer import BatchRenamer, __version__


def main():
    """Run when called from the command line"""
    parser = ArgumentParser(
        prog="brp",
        description="rename batches of files at one time",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
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
    renamer = BatchRenamer(*cli_args.filename, autofiles=cli_args.autofiles)
    renamer()


if __name__ == "__main__":
    main()
