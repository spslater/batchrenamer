#!/usr/bin/env python3

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from csv import reader
from os import path, rename
from os.path import join
from sys import argv

import logging
import re
try:
	import readline
except:
	print("Readline not available")


logging.basicConfig(format='[%(levelname)s]\t%(message)s', level=logging.INFO)

CONFIM = ["y", "Y", "yes", "Yes"]
DENY = ["n", "N", "no", "No"]
BACK = ["b", "B", "back", "Back"]

def userInput(message):
	return input(message).lower()


class Renamer:
	def __init__(self, names=[], autofile=None):
		self.actions = [
			{ "opts": ["q", "quit"],
				"help_opt": "q[uit]",
				"message": "Quit program, don't apply unsaved changes.",
				"method": self.quit },
			{ "opts": ["h", "help"],
				"help_opt": "h[elp]",
				"message": "Print help message.",
				"method": self.help },
			{ "opts": ["u", "undo"],
				"help_opt": "u[ndo]",
				"message": "Undo last regex applied.",
				"method": self.undo },
			{ "opts": ["s", "save"],
				"help_opt": "s[ave]",
				"message": "Save files with current changes.",
				"method": self.save },
			{ "opts": ["r", "regex"],
				"help_opt": "r[egex]",
				"message": "Find and replace based on a regex.",
				"method": self.findAndReplace },
			{ "opts": ["l", "list"],
				"help_opt": "l[ist]",
				"message": "Lists current files being modified.",
				"method": self.printFileChanges },
			{ "opts": ["e", "ext"],
				"help_opt": "e[xt]",
				"message": "Change all the extensions on all files.",
				"method": self.changeExt },
			{ "opts": ["i", "insert"],
				"help_opt": "i[nsert]",
				"message": "Insert string, positive from begining, negative from ending",
				"method": self.insertString },
			{ "opts": ["t", "track"],
				"help_opt": "t[rack]",
				"message": "Load tsv file with track number and song titles.",
				"method": self.prependTrackNumbers },
			{ "opts": ["n", "name"],
				"help_opt": "n[ame]",
				"message": "Load tsv file with episode number and titles.",
				"method": self.appendEpisodeNames },
			{ "opts": ["w", "write"],
				"help_opt": "w[rite]",
				"message": "Write changes and quit program, same as save then quit.",
				"method": self.saveAndQuit },
			{ "opts": ["a", "auto"],
				"help_opt": "a[uto]",
				"message": "Automate some commands in order to speed up repetative tasks.",
				"method": self.automate },
		]
		self.files = []
		for name in names:
			self.files.append(FileRename(name))

		if autofile:
			self.automate(autofile)

	def _todo(self):
		logging.warn("NEED TO IMPLAMENT")

	def _calcHelpPadding(self):
		maxLen = 0
		for action in self.actions:
			length = len(action["help_opt"])
			maxLen = length if length > maxLen else maxLen
		return maxLen

	def printFileChanges(self):
		for f in self.files:
			f.printChanges()
		print()

	def run(self):
		while True:
			action = userInput("Action: ")
			for act in self.actions:
				if action in act["opts"]:
					act["method"]()
					break

	def help(self):
		help_pad = self._calcHelpPadding()
		for action in self.actions:
			print("\t" + action["help_opt"].ljust(help_pad) + " : " + action["message"])
		print()

	def save(self, really_in=None):
		really = userInput("Are you sure you want to save new names? ") if really_in is None else really_in
		while True:
			if really in CONFIM:
				for f in self.files:
					f.save()
				print("Files renamed.")
				break
			elif really in DENY:
				print("No files renamed.")
				break
			else:
				really = userInput("Yes or No? ")

	def quit(self, really_in=None):
		really = userInput("Are you sure you want to quit? ") if really_in is None else really_in
		while True:
			if really in CONFIM:
				print("Thanks for using!")
				exit()
			elif really in DENY:
				return
			else:
				really = userInput("Yes or No? ")

	def saveAndQuit(self, really_in=None):
		really = userInput("Are you sure you want to save and quit? ") if really_in is None else really_in
		while True:
			if really in CONFIM:
				self.save("yes")
				self.quit("yes")
				exit()
			elif really in DENY:
				return
			else:
				really = userInput("Yes or No? ")

	def undo(self):
		undoneAll = True
		for f in self.files:
			undoneAll = f.undo() and True
		print(("Last " if undoneAll else "All ") + "change" + (" has" if undoneAll else "s have") + " been undone.")

	def findAndReplace(self, find_in=None, replace_in=None):
		find = input("Find: ") if find_in is None else find_in
		repl = input("Repl: ") if replace_in is None else replace_in
		for f in self.files:
			f.replace(find, repl)
		self.printFileChanges()

	def changeExt(self, repl_in=None):
		repl = input("New Ext: ") if repl_in is None else repl_in
		for f in self.files:
			f.ext = repl if repl[0] == "." else "." + repl

	def insertString(self, val_in=None, num_in=None, good_in=None):
		val = input("Insert: ") if val_in is None else val_in
		num = 0
		while True:
			try:
				num = int(userInput("Index: ")) if num_in is None else int(num_in)
				orig = test = self.files[0].rename
				if num > 0:
					if num < len(test):
						idx = num
					else:
						idx = len(test)
					find = "^(.{{{}}})(.*)".format(idx)
				elif num <= 0:
					if num > -1 * len(test):
						idx = -1 * num
					else:
						idx = 0
					find = "(.*?)(.{{{}}})$".format(idx)
				repl = r'\1' + val + r'\2'
				test = re.sub(find, repl, test)
				print("Example:\n" + test)
				good = userInput("Right index? ") if good_in is None else good_in
				if good in CONFIM: break
				if good in BACK: return
			except ValueError:
				print("Please enter an int.")
		self.findAndReplace(find, repl)

	def appendEpisodeNames(self, tsv_in=None):
		tsv = input("Filepath: ") if tsv_in is None else tsv_in
		with open(tsv, newline='') as tp:
			tsv_reader = reader(tp, delimiter='\t')
			for ep in tsv_reader:
				num = ep[0].strip()
				title = ep[1].strip()
				for f in self.files:
					if re.search("- {} -".format(num), f.rename) is not None:
						f.replace('$', title)
						break
		self.printFileChanges()

	def prependTrackNumbers(self, tsv_in=None):
		tsv = input("Filepath: ") if tsv_in is None else tsv_in
		with open(tsv) as tp:
			tsv_reader = reader(tp, delimiter='\t')
			for track in tsv_reader:
				num = track[0].strip()
				title = track[1].strip()
				for f in self.files:
					if re.search("^{}$".format(re.escape(title)), f.rename) is not None:
						f.replace('^', "{} ".format(num))
						break
		self.printFileChanges()

	def automate(self, tsv_in=None):
		tsv = input("Filepath: ") if tsv_in is None else tsv_in
		with open(tsv) as tp:
			tsv_reader = reader(tp, delimiter='\t')
			for command in tsv_reader:
				opt = command[0]
				args = command[1:]
				for act in self.actions:
					if opt in act["opts"]:
						act["method"](*args)
						break
		self.printFileChanges()


class FileRename:
	def __init__(self, fullName=""):
		self.full = fullName
		self.directory = path.dirname(self.full) or "."
		self.base = path.basename(self.full)
		self.name = path.splitext(self.base)[0]
		self.ext = path.splitext(self.base)[1]
		self.nameList = []
		self.previous = self.name
		self.rename = self.previous

	def __str__(self):
		return "\n\tFull: {}\n\tRename: {}".format(self.full, self.rename)

	def fullname(self):
		return join(self.directory, self.rename + self.ext)

	def replace(self, find, repl):
		self.nameList.append(self.previous)
		self.previous = self.rename
		self.rename = re.sub(find, repl, self.rename)

	def undo(self):
		if len(self.nameList):
			self.rename = self.previous
			self.previous = self.nameList.pop()
			return True
		else:
			return False

	def save(self):
		self.move()
		self.name = self.rename

	def move(self):
		old = join(self.directory,   self.name + self.ext)
		new = join(self.directory, self.rename + self.ext)
		rename(old, new)

	def printChanges(self):
		print(self.name + self.ext + "\n" + self.rename + self.ext + "\n")


if __name__ == "__main__":
	parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
	parser.add_argument('files', nargs='+',
		help="Files to be renamed.")
	parser.add_argument('-a', '-auto', dest='auto',
		help="Inital automated file to run.", metavar="AUTO")

	args = parser.parse_args()
	Renamer(args.files, autofile=args.auto).run()
