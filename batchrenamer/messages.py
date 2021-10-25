"""Help message texts"""
__all__ = ["ALL", "MESSAGES", "SMALL"]

HELP = """\
help (h, ?) [-s] [cmd ...]
    display help message

    -s, --small  display short help text
    cmd          name or abbreviation of command you want help info about
"""
QUIT = """\
quit (q, exit) [-c]
    quit program, don't apply unsaved changes

    -c, --confirm  quit without confirmation
"""
AUTOMATE = """\
automate (a, auto) [filename ...]
    automate some commands in order to speed up repetative tasks

    filename  relative path to file to load auto commands from
"""
END = """\
end (e) [filename ...]
    tsv with pattern and value to append to each file that matches

    filename  relative path to file to load patterns from
"""
EXTENSION = """\
extension (x, ext) [ext [pattern]]
    change the extension on all files or files that match pattern

    ext      extension to change to
    pattern  pattern to match for filename change
"""
FRONT = """\
front (f, fr) [filename ...]
    tsv with pattern and value to prepend to each file that matches

    filename  filename  relative path to file to load patterns from
"""
INSERT = """\
insert (i) [value [index]]
    insert string, positive from begining, negative from ending

    value  value to insert
    index  index starting from 0 to instert value into filename
"""
LIST = """\
list (l)
    lists current files being modified
"""
REPLACE = """\
replace (r, re, regex) [find [replace]]
    find and replace based on a regex

    find     pattern to search for
    replace  value to replace with (can use groups matched in find)
"""
SAVE = """\
save (s) [-c]
    save files with current changes

    -c, --confirm  save without confirmation
"""
UNDO = """\
undo (u)
    undo last change made
"""
WRITE = """\
write (w) [-c]
    write changes and quit program, same as save then quit

    -c, --confirm  save and quit without confirmation
"""

_commands = [
    HELP,
    QUIT,
    AUTOMATE,
    END,
    EXTENSION,
    FRONT,
    INSERT,
    LIST,
    REPLACE,
    SAVE,
    UNDO,
    WRITE,
]
ALL = "\n".join(_commands)
SMALL = "\n".join([f"    {c.splitlines()[0]}" for c in _commands]) + "\n"
MESSAGES = {
    "help": HELP,
    "h": HELP,
    "?": HELP,
    "quit": QUIT,
    "q": QUIT,
    "exit": QUIT,
    "automate": AUTOMATE,
    "a": AUTOMATE,
    "auto": AUTOMATE,
    "end": END,
    "e": END,
    "extension": EXTENSION,
    "x": EXTENSION,
    "ext": EXTENSION,
    "front": FRONT,
    "f": FRONT,
    "fr": FRONT,
    "insert": INSERT,
    "i": INSERT,
    "list": LIST,
    "l": LIST,
    "replace": REPLACE,
    "r": REPLACE,
    "re": REPLACE,
    "regex": REPLACE,
    "save": SAVE,
    "s": SAVE,
    "undo": UNDO,
    "u": UNDO,
    "write": WRITE,
    "w": WRITE,
}
