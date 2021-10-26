"""Batch Rename Program"""
__all__ = ["BatchRenamer"]

import re
import sys
from argparse import ArgumentError, Namespace
from copy import deepcopy
from shlex import split

try:
    # pylint: disable=unused-import
    import readline
except ModuleNotFoundError:
    print("History not available")

from .filehistory import FileHistory
from .parser import generate_parser

CONFIRM = [True, "y", "yes"]
DENY = [False, "n", "no"]
BACK = ["b", "back", "q", "quit"]


class BatchRenamer:
    """Renaming thing"""

    def __init__(self, *filenames, autofiles=None):
        self.parser, help_list = generate_parser(self)

        _help_dic = {}
        for _help in help_list:
            _help_dic.update(_help.cmds)

        self._help_dic = _help_dic
        self._help_text = "\n".join([h.help for h in help_list])
        self._help_small = "\n".join([f"   {h.usage}" for h in help_list])

        self.files = [FileHistory(filename) for filename in filenames]
        self.autofiles = autofiles or []



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

    def _print_file_changes(self, args=None):
        if getattr(args, "automated", False):
            return
        for file_ in self.files:
            file_.print_changes()
        print("-" * 20)

    def automate_manual(self, args):
        """Pass in manual automation filenames"""
        filenames = args.filenames or split(input("Filepath(s): "))
        self.automate(*filenames)

    def automate(self, *autofiles):
        """Take file with list of commands and make those changes"""
        for autofile in autofiles:
            try:
                with open(autofile, "r", encoding="utf-8") as fp:
                    lines = fp.readlines()
            except FileNotFoundError:
                print(
                    f"Unable to open {autofile}; moving to next file provided (if any)"
                )
            else:
                for line in lines:
                    split_args = self.parser.convert_arg_line_to_args(line)
                    if split_args:
                        args = self.parser.parse_args(split_args)
                        setattr(args, "automated", True)
                        args.func(args)

    def change_case(self, args):
        """Change the case of the filenames"""
        styles = args.styles or split(input("Styles?: "))
        for file_ in self.files:
            file_.change_case(styles)
        self._print_file_changes(args)

    def append(self, args):
        """Append value to filenames either from a file or manually provided"""
        setattr(args, "replace", args.append)
        self._pend(args, self._append_file, self._append_manual)

    def prepend(self, args):
        """Prepend value to filenames either from a file or manually provided"""
        setattr(args, "replace", args.prepend)
        self._pend(args, self._prepend_file, self._prepend_manual)

    def _pend(self, args, auto, manual):
        """Add value to begining or end of filename from a file or manaully provided"""
        prev_auto = getattr(args, "automated", False)
        setattr(args, "automated", True)
        if not args.filenames and not args.find and not args.replace:
            do_files = self._low_input("Load from files? Yes or No?: ")
            if do_files in CONFIRM:
                auto(args)
        elif args.filenames:
            auto(args)
        if args.find or args.replace or not args.filenames:
            manual(args)
        setattr(args, "automated", prev_auto)
        self._print_file_changes(args)

    def _append_manual(self, og_args):
        """Append a value to filenames that match given pattern"""
        args = deepcopy(og_args)
        find = args.find or input("Find: ")
        repl = args.replace or input("Append: ")
        setattr(args, "find", find)
        setattr(args, "replace", f"{args.padding}{repl}")
        setattr(args, "side", r"$")
        self._pend_manual(args)

    def _append_file(self, og_args):
        """Add value to ending of filenames that match pattern from file"""
        args = deepcopy(og_args)
        setattr(args, "side", r"$")
        return self._pend_file(args)

    def _prepend_manual(self, og_args):
        """Prepend a value to filenames that match given pattern"""
        args = deepcopy(og_args)
        find = args.find or input("Find: ")
        repl = args.replace or input("Prepend: ")
        setattr(args, "find", find)
        setattr(args, "replace", f"{repl}{args.padding}")
        setattr(args, "side", r"^")
        self._pend_manual(args)

    def _prepend_file(self, og_args):
        """Add value to beginging of filenames that match pattern from file"""
        args = deepcopy(og_args)
        setattr(args, "side", r"^")
        return self._pend_file(args)

    def _pend_file(self, og_args):
        """Add value to begining or end of filename from file"""
        args = deepcopy(og_args)
        filenames = args.filenames or split(input("Filepath(s): "))
        if not isinstance(filenames, list):
            filenames = [filenames]
        for filename in filenames:
            try:
                with open(filename, "r", encoding="utf-8") as fp:
                    lines = fp.readlines()
            except FileNotFoundError:
                print(
                    f"Unable to open {filename}; moving to next file provided (if any)"
                )
            else:
                for line in lines:
                    try:
                        find, repl = split(line)[:2]
                    except ValueError:
                        continue
                    setattr(args, "find", find)
                    setattr(args, "replace", repl)
                    self._pend_manual(args)
        self._print_file_changes(args)

    def _pend_manual(self, og_args):
        """Add value to begining or end of filename"""
        args = deepcopy(og_args)
        for file_ in self.files:
            file_.replace(args.side, args.replace)
        self._print_file_changes(args)

    def change_ext(self, args):
        """Change file extension for files"""
        repl = args.ext or input("New Ext: ")
        pattern = args.pattern or input("Match Pattern (Leave blank for no pattern): ")
        for file_ in self.files:
            file_.change_ext(repl, pattern)
        self._print_file_changes(args)

    def print_help(self, args=None):
        """Display help message"""
        if args is None or getattr(args, "small", False):
            print(self._help_small)
            return
        commands = [s for s in getattr(args, "commands", []) if s in self._help_dic]
        if not commands:
            print(self._help_text)
            return
        for sub in args.commands:
            print(self._help_dic[sub].help)

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
                if good in CONFIRM:
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

    def history(self, args):
        """Print history of file changes"""
        if args.peak:
            self.files[0].print_history()
            return
        for file_ in self.files:
            file_.print_history()
        print("-" * 20)

    def reset(self, args):
        """Reset filenames"""
        really = args.confirm or self._low_input("Really reset? No undoing this action. ")
        while True:
            if really in CONFIRM:
                for file_ in self.files:
                    file_.reset()
                break
            if really in DENY:
                break
            really = self._low_input("Yes or No? ")

    def quit_app(self, args):
        """Exit program"""
        really = args.confirm or self._low_input("Are you sure you want to quit? ")
        while True:
            if really in CONFIRM:
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
        self._print_file_changes(args)

    def save(self, args):
        """Save name changes"""
        really = args.confirm or self._low_input(
            "Are you sure you want to save new names? "
        )
        while True:
            if really in CONFIRM:
                for file_ in self.files:
                    file_.save()
                print("Files renamed.")
                break
            if really in DENY:
                print("No files renamed.")
                break
            really = self._low_input("Yes or No? ")

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
            if really in CONFIRM:
                args.confirm = True
                self.save(args)
                self.quit_app(args)
            if really in DENY:
                return
            really = self._low_input("Yes or No? ")
