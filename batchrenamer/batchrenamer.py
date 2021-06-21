"""Batch Rename Program"""
import re
import sys
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from shlex import split

from .filehistory import FileHistory

__all__ = ["BatchRenamer"]

CONFIM = [True, "y", "yes"]
DENY = [False, "n", "no"]
BACK = ["b", "back", "q", "quit"]


class ShlexArgumentParser(ArgumentParser):
    """Argument Parser that splits lines based on the split method from shlex package"""

    def convert_arg_line_to_args(self, arg_line):
        if arg_line and not re.match(r"\s*#", arg_line):
            return split(arg_line)
        return []


class BatchRenamer:
    """Renaming thing"""

    def __init__(self, *filenames, autofiles=None):
        self.parser = self.generate_parser()
        self.files = [FileHistory(filename) for filename in filenames]
        self.autofiles = autofiles or []

    @staticmethod
    def _user_answer(message):
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
            with open(autofile) as fp:
                for line in fp.readlines():
                    split_args = self.parser.convert_arg_line_to_args(line)
                    if split_args:
                        args = self.parser.parse_args(split_args)
                        setattr(args, "automated", True)
                        args.func(args)

    def append_episode_names(self, args):
        """Add tv episode title to end of file name"""
        filenames = args.filenames or split(input("Filepath(s): "))
        if not isinstance(filenames, list):
            filenames = [filenames]
        display_changes = True
        for filename in filenames:
            try:
                with open(filename, "r") as fp:
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

    def help_message(self, _):
        """Display help message"""
        self.parser.print_help()

    def insert_string(self, args):
        """Insert value in specific position"""
        val = args.value or input("Insert: ")
        test_file = self.files[0].rename.name
        while True:
            try:
                num = args.index or int(self._user_answer("Index: "))
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
                good = args.confirm or self._user_answer("Right index? ")
                if good in CONFIM:
                    break
                if good in BACK:
                    return
                if good in DENY:
                    args.index = None
            except ValueError:
                print("Please enter a positive or negative integer.")
            print()
        setattr(args, "find", find)
        setattr(args, "replace", repl)
        self.find_and_replace(args)

    def list_file_changes(self, _):
        """List the current changes to the files"""
        self._print_file_changes()

    def quit_app(self, args):
        """Exit program"""
        really = args.confirm or self._user_answer("Are you sure you want to quit? ")
        while True:
            if really in CONFIM:
                print("Thanks for using!")
                sys.exit()
            if really in DENY:
                break
            really = self._user_answer("Yes or No? ")

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
        really = args.confirm or self._user_answer(
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
            really = self._user_answer("Yes or No? ")

    def prepend_track_numbers(self, args):
        """Add track number for music to beginging"""
        filenames = args.filenames or split(input("Filepath(s): "))
        if not isinstance(filenames, list):
            filenames = [filenames]
        for filename in filenames:
            try:
                with open(filename) as fp:
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
            really = self._user_answer("Yes or No? ")

    # pylint: disable=too-many-locals
    def generate_parser(self):
        """Create parser that will read user input"""
        confirm_args = ["-c", "--confirm"]
        confirm_kwargs = {
            "dest": "confirm",
            "action": "store_true",
            "default": False,
        }

        parser = ShlexArgumentParser(
            formatter_class=ArgumentDefaultsHelpFormatter,
            add_help=False,
            usage="brp filename [filename ...]",
        )
        subparsers = parser.add_subparsers()

        automate_parser = subparsers.add_parser(
            "automate",
            aliases=["a", "auto"],
            help="automate some commands in order to speed up repetative tasks",
        )
        automate_parser.set_defaults(func=self.manual_automate)
        automate_parser.add_argument("filenames", nargs="?")

        episode_parser = subparsers.add_parser(
            "episodes",
            aliases=["e", "ep"],
            help="load files with episode number and titles",
        )
        episode_parser.set_defaults(func=self.append_episode_names)
        episode_parser.add_argument("filenames", nargs="?")

        extension_parser = subparsers.add_parser(
            "extension",
            aliases=["x", "ext"],
            help="change the extension on all files or files that match pattern",
        )
        extension_parser.set_defaults(func=self.change_ext)
        extension_parser.add_argument("ext", nargs="?")
        extension_parser.add_argument("pattern", nargs="?")

        help_parser = subparsers.add_parser(
            "help",
            aliases=["h", "?"],
            help="display help message",
        )
        help_parser.set_defaults(func=self.help_message)

        insert_parser = subparsers.add_parser(
            "insert",
            aliases=["i"],
            help="insert string, positive from begining, negative from ending",
        )
        insert_parser.set_defaults(func=self.insert_string)
        insert_parser.add_argument(*confirm_args, **confirm_kwargs)
        insert_parser.add_argument("value", nargs="?")
        insert_parser.add_argument("index", nargs="?", type=int)

        print_parser = subparsers.add_parser(
            "list",
            aliases=["l"],
            help="lists current files being modified",
        )
        print_parser.set_defaults(func=self.list_file_changes)

        quit_parser = subparsers.add_parser(
            "quit",
            aliases=["q"],
            help="quit program, don't apply unsaved changes",
        )
        quit_parser.set_defaults(func=self.quit_app)
        quit_parser.add_argument(*confirm_args, **confirm_kwargs)

        find_replace_parser = subparsers.add_parser(
            "replace",
            aliases=["r", "re"],
            help="find and replace based on a regex",
        )
        find_replace_parser.set_defaults(func=self.find_and_replace)
        find_replace_parser.add_argument("find", nargs="?")
        find_replace_parser.add_argument("replace", nargs="?")

        save_parser = subparsers.add_parser(
            "save",
            aliases=["s"],
            help="save files with current changes",
        )
        save_parser.set_defaults(func=self.save)
        save_parser.add_argument(*confirm_args, **confirm_kwargs)

        track_parser = subparsers.add_parser(
            "tracks",
            aliases=["t", "tr"],
            help="load file with track number and song titles",
        )
        track_parser.set_defaults(func=self.prepend_track_numbers)
        track_parser.add_argument("filenames", nargs="?")

        undo_parser = subparsers.add_parser(
            "undo",
            aliases=["u"],
            help="undo last change made",
        )
        undo_parser.set_defaults(func=self.undo)
        undo_parser.add_argument("number", nargs="?", type=int, default=1)

        save_quit_parser = subparsers.add_parser(
            "write",
            aliases=["w"],
            help="write changes and quit program, same as save then quit",
        )
        save_quit_parser.set_defaults(func=self.save_and_quit)
        save_quit_parser.add_argument(*confirm_args, **confirm_kwargs)

        return parser

    def run(self):
        """Go thru renaming things"""
        if self.autofiles:
            self.automate(*self.autofiles)

        while True:
            response = self._user_answer("Action: ")
            resp_args = self.parser.parse_args(split(response))
            resp_args.func(resp_args)
