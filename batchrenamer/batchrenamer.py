"""Batch Rename Program"""
__all__ = ["BatchRenamer"]

import re
import sys
from argparse import ArgumentError, Namespace
from shlex import split

import batchrenamer.messages as messages

try:
    # pylint: disable=unused-import
    import readline
except ModuleNotFoundError:
    print("History not available")

from .filehistory import FileHistory
from .parser import generate_parser

CONFIM = [True, "y", "yes"]
DENY = [False, "n", "no"]
BACK = ["b", "back", "q", "quit"]


class BatchRenamer:
    """Renaming thing"""

    def __init__(self, *filenames, autofiles=None):
        self.parser = generate_parser(self)
        self.files = [FileHistory(filename) for filename in filenames]
        self.autofiles = autofiles or []

        self._help_text = messages.ALL
        self._help_dic = messages.MESSAGES
        self._help_small = messages.SMALL

    def __call__(self):
        """Go thru renaming things"""
        if self.autofiles:
            self.automate(*self.autofiles)

        while True:
            response = input("Action: ")
            args = split(response)
            args[0] = args[0].lower()
            try:
                resp_args = self.parser.parse_args(args)
            except ArgumentError as e:
                error_args = Namespace()
                if e.message.startswith("unrecognized arguments"):
                    print("ERROR: Invalid argument\n")
                    setattr(error_args, "subparsers", [args[0]])
                elif e.message.startswith("invalid choice"):
                    print("ERROR: Unknown command")
                    setattr(error_args, "small", True)
                else:
                    print(e.message)
                self.print_help(error_args)
            else:
                resp_args.func(resp_args)

    @staticmethod
    def _low_input(message):
        """Get user input and lower it"""
        return input(message).lower()

    def _print_file_changes(self):
        for file_ in self.files:
            file_.print_changes()
        print("-" * 20)

    def manual_automate(self, args):
        """pass in manual automation filenames"""
        filenames = args.filenames or split(input("Filepath(s): "))
        self.automate(*filenames)

    def automate(self, *autofiles):
        """Take file with list of commands and make those changes"""
        for autofile in autofiles:
            with open(autofile, "r", encoding="utf-8") as fp:
                for line in fp.readlines():
                    split_args = self.parser.convert_arg_line_to_args(line)
                    if split_args:
                        args = self.parser.parse_args(split_args)
                        setattr(args, "automated", True)
                        args.func(args)

    def append_value(self, args):
        """Add tv episode title to end of file name"""
        filenames = args.filenames or split(input("Filepath(s): "))
        if not isinstance(filenames, list):
            filenames = [filenames]
        display_changes = True
        for filename in filenames:
            try:
                with open(filename, "r", encoding="utf-8") as fp:
                    for line in fp.readlines():
                        episode, title = line.split(maxsplit=1)
                        episode = episode.strip()
                        title = title.strip()
                        for file_ in self.files:
                            if re.search(f"- {episode}" r"[\-\s]*$", file_.rename.name):
                                file_.replace(
                                    f"{episode}" r"[\-\s]*$",
                                    f"{episode} - {title}",
                                )
                                break
            except FileNotFoundError:
                print(
                    f"Unable to open {filename}; moving to next file provided (if any)"
                )
                display_changes = False
            else:
                display_changes = True
        if not getattr(args, "automated", False) and display_changes:
            self._print_file_changes()

    def change_ext(self, args):
        """Change file extension for files"""
        repl = args.ext or input("New Ext: ")
        pattern = args.pattern or input("Match Pattern (Leave blank for no pattern): ")
        for file_ in self.files:
            file_.change_ext(repl, pattern)
        if not getattr(args, "automated", False):
            self._print_file_changes()

    def print_help(self, args=None):
        """Display help message"""
        if args is None or getattr(args, "small", False):
            print(self._help_small)
            return
        subparsers = [s for s in getattr(args, "subparsers", []) if s in self._help_dic]
        if not subparsers:
            print(self._help_text)
            return
        for sub in args.subparsers:
            print(self._help_dic[sub])

    def insert_string(self, args):
        """Insert value in specific position"""
        val = args.value or input("Insert: ")
        test_file = self.files[0].rename.name
        while True:
            try:
                num = args.index or int(input("Index: "))
            except ValueError:
                print("Please enter a positive or negative integer.")
            else:
                test_len = len(test_file)
                if num >= 0:
                    idx = num if num < test_len else test_len
                    find = r"^(.{" f"{idx}" r"})(.*)$"
                elif num < 0:
                    idx = (-1 * num) if num > (-1 * test_len) else 0
                    find = r"^(.*?)(.{" f"{idx}" r"})$"
                repl = r"\1" f"{val}" r"\2"
                test = re.sub(find, repl, test_file)
                print(f"Example: {test}")
                good = args.confirm or self._low_input("Right index? ")
                if good in CONFIM:
                    break
                if good in BACK:
                    return
                if good in DENY:
                    args.index = None
            print()
        setattr(args, "find", find)
        setattr(args, "replace", repl)
        self.find_and_replace(args)

    def list_file_changes(self, _):
        """List the current changes to the files"""
        self._print_file_changes()

    def quit_app(self, args):
        """Exit program"""
        really = args.confirm or self._low_input("Are you sure you want to quit? ")
        while True:
            if really in CONFIM:
                print("Thanks for using!")
                sys.exit()
            if really in DENY:
                break
            really = self._low_input("Yes or No? ")

    def find_and_replace(self, args):
        """Find pattern and replace with new pattern"""
        find = args.find or input("Find: ")
        repl = args.replace or input("Repl: ")
        for file_ in self.files:
            file_.replace(find, repl)
        if not getattr(args, "automated", False):
            self._print_file_changes()

    def save(self, args):
        """Save name changes"""
        really = args.confirm or self._low_input(
            "Are you sure you want to save new names? "
        )
        while True:
            if really in CONFIM:
                for file_ in self.files:
                    file_.save()
                print("Files renamed.")
                break
            if really in DENY:
                print("No files renamed.")
                break
            really = self._low_input("Yes or No? ")

    def prepend_value(self, args):
        """Add track number for music to beginging"""
        filenames = args.filenames or split(input("Filepath(s): "))
        if not isinstance(filenames, list):
            filenames = [filenames]
        for filename in filenames:
            try:
                with open(filename, "r", encoding="utf-8") as fp:
                    for line in fp.readlines():
                        number, track = line.split(maxsplit=1)
                        number = number.strip()
                        track = track.strip()
                        for file_ in self.files:
                            if re.search(f"^{re.escape(track)}$", file_.rename.name):
                                file_.replace("^", f"{number} ")
                                break
            except FileNotFoundError:
                print(
                    f"Unable to open {filename}; moving to next file provided (if any)"
                )
            if not getattr(args, "automated", False):
                self._print_file_changes()

    def undo(self, args):
        """Undo last changes"""
        undone_all = True
        for _ in range(args.number):
            for file_ in self.files:
                undone_all = file_.undo()
                if not undone_all:
                    break
            if not undone_all:
                break
        if undone_all and not getattr(args, "automated", False):
            self._print_file_changes()
        print(
            ("Last " if undone_all else "All ")
            + "change"
            + (" has" if undone_all else "s have")
            + " been undone."
        )

    def save_and_quit(self, args):
        """save changes, exit the program"""
        really = args.confirm or ("Are you sure you want to save and quit? ")
        while True:
            if really in CONFIM:
                args.confirm = True
                self.save(args)
                self.quit_app(args)
            if really in DENY:
                return
            really = self._low_input("Yes or No? ")
