#!/usr/bin/env python3

from os import path, rename
from sys import argv

import re
try:
	import readline
except:
	print("Readline not available")


CONFIM = ["y", "Y", "yes", "Yes"]
DENY = ["n", "N", "no", "No"]
BACK = ["b", "B", "back", "Back"]

def userInput(message):
	return input(message).lower()


class Renamer:
	def __init__(self, names=[]):
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
		]
		self.HELP_PAD = self._calcHelpPadding()
		self.files = []
		for name in names: 
			self.files.append(FileRename(name))

	def _todo(self):
		print("NEED TO IMPLAMENT")

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
		for action in self.actions:
			print("\t" + action["help_opt"].ljust(self.HELP_PAD) + " : " + action["message"])
		print()

	def save(self, r=None):
		really = userInput("Are you sure you want to save new names? ") if r is None else r
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

	def quit(self, r=None):
		really = userInput("Are you sure you want to quit? ") if r is None else r
		while True:
			if really in CONFIM: 
				print("Thanks for using!")
				exit()
			elif really in DENY:
				return
			else:
				really = userInput("Yes or No? ")

	def saveAndQuit(self):
		really = userInput("Are you sure you want to save and quit? ")
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

	def findAndReplace(self, f=None, r=None):
		find = input("Find: ") if f is None else f
		repl = input("Repl: ") if r is None else r
		for f in self.files:
			f.replace(find, repl)
		self.printFileChanges()

	def changeExt(self):
		repl = input("New Ext: ")
		for f in self.files:
			f.ext = repl if repl[0] == "." else "." + repl

	def insertString(self):
		val = input("Insert: ")
		num = 0
		while True:
			try:
				num = int(userInput("Index: "))
				orig = test = self.files[0].rename
				if num > 0:
					if num < len(test):
						idx = num
					else:
						idx = len(test)
					find = "^(.{"+str(idx)+"})(.*)"
				elif num <= 0:
					if num > -1 * len(test):
						idx = -1 * num
					else:
						idx = 0
					find = "(.*?)(.{"+str(idx)+"})$"
				repl = r'\1' + val + r'\2'
				test = re.sub(find, repl, test)
				print("Example:\n" + test)
				good = userInput("Right index? ")
				if good in CONFIM: break
				if good in BACK: return
			except ValueError:
				print("Please enter an int.")
		self.findAndReplace(find, repl)

	def appendEpisodeNames(self):
		tsv = input("Filepath: ")
		with open(tsv) as f:
			for ep in f:
				num = ep.split('\t')[0].strip()
				title = ep.split('\t')[1].strip()
				for f in self.files:
					if re.search("- " + str(num) + " -", f.rename) is not None:
						f.replace('$', title)
						break
		self.printFileChanges()

	def prependTrackNumbers(self):
		tsv = input("Filepath: ")
		with open(tsv) as f:
			for track in f:
				num = track.split('\t')[0].strip()
				title = track.split('\t')[1].strip()
				for f in self.files:
					if re.search("^" + re.escape(title) + "$", f.rename) is not None:
						f.replace('^', str(num) + " ")
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
		return "\n\tFull: " + self.full + "\n\tRename: " + self.rename

	def fullname(self):
		return self.directory + "/" + self.rename + self.ext

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
		old = self.directory + "/" + self.name   + self.ext
		new = self.directory + "/" + self.rename + self.ext
		rename(old, new)

	def printChanges(self):
		print(self.name + self.ext + "\n" + self.rename + self.ext + "\n")


def main():
	if len(argv) == 1:
		print("Usage: rename <file> ...")
		exit()

	Renamer(argv[1:]).run()


if __name__ == "__main__":
	main()
