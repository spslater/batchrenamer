"""Manage file changes"""
__all__ = ["FileInfo", "FileHistory"]

import re
from collections import namedtuple
from os import path, rename
from os.path import join

from .strcase import CASE


class FileInfo(namedtuple("FileInfo", ["directory", "name", "ext"])):
    """Information about a file

    :param directory: location of file
    :type directory: str
    :param name: filename without extension
    :type name: str
    :param ext: file extension (only from last `.`)
    :type ext: str
    """

    __slots__ = ()

    @property
    def fullname(self):
        """Get the fullname of the file"""
        return join(self.directory, f"{self.name}{self.ext}")

    def __str__(self):
        return self.fullname


class FileHistory:
    """Individual file rename info"""

    def __init__(self, fullname):
        directory = path.dirname(fullname) or "."
        base = path.basename(fullname)
        name = path.splitext(base)[0]
        ext = path.splitext(base)[1]
        self.original = FileInfo(directory, name, ext)
        self.current = self.original
        self.name_list = []
        self.previous = self.original
        self.rename = self.previous

    @staticmethod
    def fullname(directory, name, ext):
        """Get full name of file"""
        return join(directory, f"{name}{ext}")

    def change_case(self, cases):
        """Change the case of the name"""
        self.name_list.append(self.previous)
        new_name = self.rename.name
        for case in cases:
            func = CASE.get(case, CASE["default"])
            new_name = func(new_name)
        self.previous = self.rename
        self.rename = self.rename._replace(name=new_name)

    def change_ext(self, new_ext, pattern=None):
        """Change the extension of a file"""
        new_ext = new_ext if new_ext[0] == "." else f".{new_ext}"
        if not pattern or (pattern and re.search(pattern, self.previous.name)):
            new_info = self.previous._replace(ext=new_ext)
        else:
            new_info = self.previous._replace(ext=self.previous.ext)
        self.name_list.append(self.previous)
        self.previous = self.rename
        self.rename = new_info

    def replace(self, find, repl):
        """Find and replace value in filename"""
        self.name_list.append(self.previous)
        new_name = re.sub(find, repl, self.rename.name)
        self.previous = self.rename
        self.rename = self.rename._replace(name=new_name)

    def noop(self):
        """Perform noop for when no action should be taken"""
        self.name_list.append(self.previous)
        self.previous = self.rename

    def undo(self):
        """Undo last filename"""
        length = len(self.name_list)
        if length:
            self.rename = self.previous
            self.previous = self.name_list.pop()
            return True
        return False

    def reset(self):
        """Reset to inital state"""
        self.current = self.original
        self.name_list = []
        self.previous = self.original
        self.rename = self.previous

    def save(self):
        """Save new filename"""
        self.move()
        self.current = self.rename

    def move(self):
        """Rename file"""
        old = self.current.fullname
        new = self.rename.fullname
        rename(old, new)

    def print_changes(self):
        """Print change from original name to current name"""
        print(self.current.fullname + "\n" + self.rename.fullname + "\n")

    def print_history(self):
        """Print file changes up"""
        print(self.current.fullname + "\n" + self.rename.fullname)
        num = len(self.name_list)
        if self.previous.name != self.original.name:
            num += 1
        pad = len(str(num))
        if not num:
            print("   NA\n")
            return
        for name in self.name_list:
            print(f"   {str(num).rjust(pad)}  {name.name}")
            num -= 1
        print(f"   {str(num).rjust(pad)}  {self.previous.name}")
        num -= 1
        print("~"*20)
