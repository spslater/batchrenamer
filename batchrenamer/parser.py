"""Parsers for batchrenamer"""
__all__ = ["generate_parser"]

import re
from argparse import ArgumentError, ArgumentParser, RawDescriptionHelpFormatter
from dataclasses import dataclass
from shlex import split


@dataclass
class SubparserHelp:
    """Clean help messags for the subparsers"""

    def __init__(self, cmds, usage, help_):
        usage = usage.replace("usage: ", "").strip()
        alts = f"{cmds[0]} ({', '.join(cmds[1:])})" if cmds[1:] else cmds[0]
        self.usage = re.sub(r"^" + cmds[0], alts, usage)

        args = [f"   {l}" for l in help_.splitlines()[1:] if l.strip()]
        msg = "\n".join(args)
        self.help = f"{self.usage}\n{msg}\n"

        self.cmds = {}
        for cmd in cmds:
            self.cmds[cmd] = self


class ShlexArgumentParser(ArgumentParser):
    """Argument Parser that splits lines based on the split method from shlex package"""

    def convert_arg_line_to_args(self, arg_line):
        if arg_line.strip() and not re.match(r"\s*#", arg_line):
            return split(arg_line)
        return []

    def error(self, message):
        raise ArgumentError(None, message)


CONFIRM_ARGS = ["-c", "--confirm"]
CONFIRM_KWARGS = {
    "dest": "confirm",
    "action": "store_true",
    "default": False,
    "help": "automatically confirm action",
}


def _parser(cmds, subparsers):
    return subparsers.add_parser(
        cmds[0],
        aliases=cmds[1:],
        prog=cmds[0],
        add_help=False,
        exit_on_error=False,
    )


def _help_parser(cmds, subparsers, renamer):
    """Help Command"""
    _help = _parser(cmds, subparsers)
    _help.description = "display help message"
    _help.set_defaults(func=renamer.print_help)
    _help.add_argument("commands", nargs="*", help="name to get specific info on")
    _help.add_argument(
        "-s",
        "--small",
        dest="small",
        action="store_true",
        default=False,
        help="display just the usage messages",
    )
    return SubparserHelp(cmds, _help.format_usage(), _help.format_help())


def _quit_parser(cmds, subparsers, renamer):
    """Quit Command"""
    _quit = _parser(cmds, subparsers)
    _quit.description = "quit program, don't apply unsaved changes"
    _quit.set_defaults(func=renamer.quit_app)
    _quit.add_argument(*CONFIRM_ARGS, **CONFIRM_KWARGS)
    return SubparserHelp(cmds, _quit.format_usage(), _quit.format_help())


def _automate_parser(cmds, subparsers, renamer):
    """Automate Command"""
    _automate = _parser(cmds, subparsers)
    _automate.description = "automate commands in order to speed up repetative tasks"
    _automate.set_defaults(func=renamer.automate_manual)
    _automate.add_argument("filenames", nargs="*")
    return SubparserHelp(cmds, _automate.format_usage(), _automate.format_help())


def _case_parser(cmds, subparsers, renamer):
    """Case Command"""
    _case = _parser(cmds, subparsers)
    _case.exit_on_error = False
    _case.description = "change the case (title, upper, lower) of files"
    _case.set_defaults(func=renamer.change_case)
    _case.add_argument(
        "styles",
        type=str,
        nargs="*",
        help="type of case style (lower, upper, title, camel, kebab, ect) to switch to",
    )
    return SubparserHelp(cmds, _case.format_usage(), _case.format_help())


def _append_parser(cmds, subparsers, renamer):
    """Append Command"""
    _append = _parser(cmds, subparsers)
    _append.description = (
        "pattern and value to append to each file that matches,"
        "can be automated with a file"
    )
    _append.set_defaults(func=renamer.append)
    _append.add_argument(
        "find",
        nargs="?",
        help="regex pattern to match against",
    )
    _append.add_argument(
        "append",
        nargs="?",
        help="value to append to filename",
    )
    _append.add_argument(
        "-f",
        "--filenames",
        dest="filenames",
        nargs="+",
        help="file to load patterns from",
    )
    _append.add_argument(
        "-p",
        "--padding",
        dest="padding",
        default=" ",
        help="string to insert between the end of the filename and the value being appended",
    )
    return SubparserHelp(cmds, _append.format_usage(), _append.format_help())


def _extension_parser(cmds, subparsers, renamer):
    """Extension Command"""
    _extension = _parser(cmds, subparsers)
    _extension.description = (
        "change the extension on all files or files that match pattern"
    )
    _extension.set_defaults(func=renamer.change_ext)
    _extension.add_argument(
        "ext",
        nargs="?",
        help="new extension to change to",
    )
    _extension.add_argument(
        "pattern",
        nargs="?",
        help="pattern to match against old extensions",
    )
    return SubparserHelp(cmds, _extension.format_usage(), _extension.format_help())


def _prepend_parser(cmds, subparsers, renamer):
    """Prepend Command"""
    _prepend = _parser(cmds, subparsers)
    _prepend.description = (
        "tsv with pattern and value to prepend to each file that matches"
    )
    _prepend.set_defaults(func=renamer.prepend)
    _prepend.add_argument(
        "find",
        nargs="?",
        help="regex pattern to match against",
    )
    _prepend.add_argument(
        "prepend",
        nargs="?",
        help="value to prepend to filename",
    )
    _prepend.add_argument(
        "-f",
        "--filenames",
        dest="filenames",
        nargs="+",
        help="file to load patterns from",
    )
    _prepend.add_argument(
        "-p",
        "--padding",
        dest="padding",
        default=" ",
        help="string to insert between the value being prepended and the begining of the filename",
    )
    return SubparserHelp(cmds, _prepend.format_usage(), _prepend.format_help())


def _insert_parser(cmds, subparsers, renamer):
    """Insert Command"""
    _insert = _parser(cmds, subparsers)
    _insert.description = "insert string, positive from begining, negative from ending"
    _insert.set_defaults(func=renamer.insert_string)
    _insert.add_argument(*CONFIRM_ARGS, **CONFIRM_KWARGS)
    _insert.add_argument(
        "value",
        nargs="?",
        type=str,
        help="value to insert",
    )
    _insert.add_argument(
        "index",
        nargs="?",
        type=int,
        help=(
            "index (starting from 0) to insert at, "
            "negative numbers will insert counting from the end"
        ),
    )
    return SubparserHelp(cmds, _insert.format_usage(), _insert.format_help())


def _print_parser(cmds, subparsers, renamer):
    """Print Command"""
    _print = _parser(cmds, subparsers)
    _print.description = "lists current files being modified"
    _print.set_defaults(func=renamer.list_file_changes)
    return SubparserHelp(cmds, _print.format_usage(), _print.format_help())


def _find_replace_parser(cmds, subparsers, renamer):
    """Find_replace Command"""
    _find_replace = _parser(cmds, subparsers)
    _find_replace.description = "find and replace based on a regex"
    _find_replace.set_defaults(func=renamer.find_and_replace)
    _find_replace.add_argument(
        "find",
        nargs="?",
        help="pattern to find",
    )
    _find_replace.add_argument(
        "replace",
        nargs="?",
        help="pattern to insert",
    )
    return SubparserHelp(
        cmds,
        _find_replace.format_usage(),
        _find_replace.format_help(),
    )


def _save_parser(cmds, subparsers, renamer):
    """Save Command"""
    _save = _parser(cmds, subparsers)
    _save.description = "save files with current changes"
    _save.set_defaults(func=renamer.save)
    _save.add_argument(*CONFIRM_ARGS, **CONFIRM_KWARGS)
    return SubparserHelp(cmds, _save.format_usage(), _save.format_help())


def _undo_parser(cmds, subparsers, renamer):
    """Undo Command"""
    _undo = _parser(cmds, subparsers)
    _undo.description = "undo last change made"
    _undo.set_defaults(func=renamer.undo)
    _undo.add_argument(
        "number",
        nargs="?",
        type=int,
        default=1,
        help="number of changes to undo",
    )
    return SubparserHelp(cmds, _undo.format_usage(), _undo.format_help())


def _save_quit_parser(cmds, subparsers, renamer):
    """Save_quit Command"""
    _save_quit = _parser(cmds, subparsers)
    _save_quit.description = "write changes and quit program, same as save then quit"
    _save_quit.set_defaults(func=renamer.save_and_quit)
    _save_quit.add_argument(*CONFIRM_ARGS, **CONFIRM_KWARGS)
    return SubparserHelp(cmds, _save_quit.format_usage(), _save_quit.format_help())


def _history_parser(cmds, subparsers, renamer):
    """History Command"""
    _history = _parser(cmds, subparsers)
    _history.description = "print history of changes for all files"
    _history.set_defaults(func=renamer.history)
    _history.add_argument(
        "--peak",
        "-p",
        dest="peak",
        action="store_true",
        default=False,
        help="just show single file history",
    )
    return SubparserHelp(cmds, _history.format_usage(), _history.format_help())


def _reset_parser(cmds, subparsers, renamer):
    """Reset Command"""
    _reset = _parser(cmds, subparsers)
    _reset.description = "reset changes to original inputs, no undoing"
    _reset.set_defaults(func=renamer.reset)
    _reset.add_argument(*CONFIRM_ARGS, **CONFIRM_KWARGS)
    return SubparserHelp(cmds, _reset.format_usage(), _reset.format_help())


def generate_parser(renamer):
    """Create parser that will read user input"""
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

    _help = [
        _help_parser(("help", "h", "?"), subparsers, renamer),
        _save_parser(("save", "s"), subparsers, renamer),
        _quit_parser(("quit", "q", "exit"), subparsers, renamer),
        _save_quit_parser(("write", "w"), subparsers, renamer),
        _print_parser(("list", "ls", "l"), subparsers, renamer),
        _history_parser(("history", "hist", "past"), subparsers, renamer),
        _undo_parser(("undo", "u"), subparsers, renamer),
        _reset_parser(("reset", "over", "o"), subparsers, renamer),
        _automate_parser(("automate", "a", "auto"), subparsers, renamer),
        _find_replace_parser(("replace", "r", "re", "reg", "regex"), subparsers, renamer),
        _append_parser(("append", "ap"), subparsers, renamer),
        _prepend_parser(("prepend", "p", "pre"), subparsers, renamer),
        _insert_parser(("insert", "i", "in"), subparsers, renamer),
        _case_parser(("case", "c"), subparsers, renamer),
        _extension_parser(("extension", "x", "ext"), subparsers, renamer),
    ]

    return parser, _help
