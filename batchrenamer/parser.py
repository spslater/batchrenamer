"""Parsers for batchrenamer"""
__all__ = ["generate_parser"]

import re
from argparse import ArgumentError, ArgumentParser, RawDescriptionHelpFormatter
from shlex import split


class ShlexArgumentParser(ArgumentParser):
    """Argument Parser that splits lines based on the split method from shlex package"""

    def __init__(self, *args, **kwargs):
        self._error = None
        super().__init__(*args, **kwargs)

    def convert_arg_line_to_args(self, arg_line):
        if arg_line and not re.match(r"\s*#", arg_line):
            return split(arg_line)
        return []

    def error(self, message):
        raise ArgumentError(None, message)


# pylint: disable=too-many-locals
def generate_parser(renamer):
    """Create parser that will read user input"""
    confirm_args = ["-c", "--confirm"]
    confirm_kwargs = {
        "dest": "confirm",
        "action": "store_true",
        "default": False,
    }

    parser = ShlexArgumentParser(
        formatter_class=RawDescriptionHelpFormatter,
        prog="brp",
        usage="cmd [args ...]",
        add_help=False,
        exit_on_error=False,
    )
    subparsers = parser.add_subparsers(
        title="commands",
        description="actions to take on the filenames",
    )

    help_parser = subparsers.add_parser(
        "help",
        aliases=["h", "?"],
        prog="help",
        help="display help message",
        add_help=False,
        exit_on_error=False,
    )
    help_parser.set_defaults(func=renamer.print_help)
    help_parser.add_argument("subparsers", nargs="*")
    help_parser.add_argument(
        "-s",
        "--small",
        dest="small",
        action="store_true",
        default=False,
    )

    quit_parser = subparsers.add_parser(
        "quit",
        aliases=["q", "exit"],
        prog="quit",
        help="quit program, don't apply unsaved changes",
        add_help=False,
        exit_on_error=False,
    )
    quit_parser.set_defaults(func=renamer.quit_app)
    quit_parser.add_argument(*confirm_args, **confirm_kwargs)

    automate_parser = subparsers.add_parser(
        "automate",
        aliases=["a", "auto"],
        help="automate some commands in order to speed up repetative tasks",
        exit_on_error=False,
    )
    automate_parser.set_defaults(func=renamer.automate_manual)
    automate_parser.add_argument("filenames", nargs="*")

    append_parser = subparsers.add_parser(
        "end",
        aliases=["e"],
        help="pattern and value to append to each file that matches, can be automated with a file",
        exit_on_error=False,
    )
    append_parser.set_defaults(func=renamer.append)
    append_parser.add_argument("find", nargs="?")
    append_parser.add_argument("replace", nargs="?")
    append_parser.add_argument("-f", "--filenames", dest="filenames", nargs="+")
    append_parser.add_argument("-p", "--padding", dest="padding", default=" ")

    extension_parser = subparsers.add_parser(
        "extension",
        aliases=["x", "ext"],
        help="change the extension on all files or files that match pattern",
        exit_on_error=False,
    )
    extension_parser.set_defaults(func=renamer.change_ext)
    extension_parser.add_argument("ext", nargs="?")
    extension_parser.add_argument("pattern", nargs="?")

    prepend_parser = subparsers.add_parser(
        "front",
        aliases=["f", "fr"],
        help="tsv with pattern and value to prepend to each file that matches",
        exit_on_error=False,
    )
    prepend_parser.set_defaults(func=renamer.prepend)
    prepend_parser.add_argument("find", nargs="?")
    prepend_parser.add_argument("replace", nargs="?")
    prepend_parser.add_argument("-f", "--filenames", dest="filenames", nargs="+")
    prepend_parser.add_argument("-p", "--padding", dest="padding", default=" ")

    insert_parser = subparsers.add_parser(
        "insert",
        aliases=["i"],
        help="insert string, positive from begining, negative from ending",
        exit_on_error=False,
    )
    insert_parser.set_defaults(func=renamer.insert_string)
    insert_parser.add_argument(*confirm_args, **confirm_kwargs)
    insert_parser.add_argument("value", nargs="?")
    insert_parser.add_argument("index", nargs="?", type=int)

    print_parser = subparsers.add_parser(
        "list",
        aliases=["l"],
        help="lists current files being modified",
        exit_on_error=False,
    )
    print_parser.set_defaults(func=renamer.list_file_changes)

    find_replace_parser = subparsers.add_parser(
        "replace",
        aliases=["r", "re", "regex"],
        prog="replace",
        help="find and replace based on a regex",
        exit_on_error=False,
    )
    find_replace_parser.set_defaults(func=renamer.find_and_replace)
    find_replace_parser.add_argument("find", nargs="?", help="pattern to find")
    find_replace_parser.add_argument("replace", nargs="?", help="pattern to insert")

    save_parser = subparsers.add_parser(
        "save",
        aliases=["s"],
        help="save files with current changes",
        exit_on_error=False,
    )
    save_parser.set_defaults(func=renamer.save)
    save_parser.add_argument(*confirm_args, **confirm_kwargs)

    undo_parser = subparsers.add_parser(
        "undo",
        aliases=["u"],
        help="undo last change made",
        exit_on_error=False,
    )
    undo_parser.set_defaults(func=renamer.undo)
    undo_parser.add_argument("number", nargs="?", type=int, default=1)

    save_quit_parser = subparsers.add_parser(
        "write",
        aliases=["w"],
        help="write changes and quit program, same as save then quit",
        exit_on_error=False,
    )
    save_quit_parser.set_defaults(func=renamer.save_and_quit)
    save_quit_parser.add_argument(*confirm_args, **confirm_kwargs)

    return parser
