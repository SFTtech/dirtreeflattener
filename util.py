#!/usr/bin/python3
import os
import sys
import shutil
import readline
import types
import subprocess

def ansicolseq(colcode = ""):
	return "\x1b[" + str(colcode) + "m"

def colored(msg, colcode):
	return ansicolseq(colcode) + msg + ansicolseq()

def colprint(msg, colcode):
	print(colored(msg, colcode))

def redprint(msg):
	colprint(msg, 31)

def yellowprint(msg):
	colprint(msg, 33)

def cyanprint(msg):
	colprint(msg, 36)

def fatal(msg):
	redprint(msg)
	print_nonfatals("Nonfatal errors before this error:")
	sys.exit(1)

def nonfatal(msg):
	yellowprint(msg)
	nonfatals.append(msg)

def info(msg):
	cyanprint(msg)

#store all non-fatal errors
nonfatals = []
def print_nonfatals(msg = "Nonfatal errors"):
	if len(nonfatals) > 0:
		print(msg)
		for nonfatal in nonfatals:
			print(nonfatal)

def _pre_input_func(default):
	readline.insert_text(default)
	readline.redisplay()
	sys.stdout.flush()

def surround_ansi_escapes(prompt, start = "\x01", end = "\x02"):
	escaped = False
	result = ""

	for c in prompt:
		if c == "\x1b" and not escaped:
			result += start + c
			escaped = True
		elif c.isalpha() and escaped:
			result += c + end
			escaped = False
		else:
			result += c

	return result

def get_line(prompt = "> ", default = "", completer = None):
	readline.parse_and_bind("tab: complete")
	readline.set_completer(completer)
	readline.set_completer_delims("/")
	readline.set_pre_input_hook(lambda: _pre_input_func(default))
	line = input(surround_ansi_escapes(prompt))
	readline.set_pre_input_hook()
	return line

class filename_completer():
	def completer(self, text, state):
		if state == 0:
			try:
				dirname = os.path.dirname(readline.get_line_buffer())
				self.complist = list(filter(lambda fname: fname.startswith(text), map(lambda fname: os.path.isdir(dirname + '/' + fname) and fname + '/' or fname, os.listdir(dirname))))
			except Exception as e:
				self.complist = []

		try:
			return self.complist[state]
		except:
			return None

class _confirm_class:
	def __init__(self, **kwargs):
		#ultra-lazy version of storing all the parameters
		self.__dict__.update(kwargs)

		if type(self.default_answer) == bool:
			if self.default_answer:
				self.default_answer = "yes"
			else:
				self.default_answer = "no"
		else:
			self.default_answer = str(self.default_answer)

		self.options = []
		#allow the user to reply yes/no. no means returning False, yes means returning val.
		self.options.append(("yes", self.option_yes))
		self.options.append(("no", self.option_no))

		#if a path is passed, allow the user to list it and launch a shell in it
		if self.path != None:
			self.options.append(("ls", self.option_ls))
			self.options.append(("shell", self.option_shell))

		#if a valname is passed, allow the user to change val
		if self.valname != None:
			self.options.append(("change", self.option_change))

		#if a testfun is passed, allow the user to run it
		if self.testfun != None:
			self.options.append(("test", self.option_test))

		#allow the user to quit
		self.options.append(("quit", self.option_quit))

		if self.default_answer not in map(lambda x: x[0], self.options):
			self.default_answer = ""

	def completer(self, text, state):
		if state == 0:
			self.complist = list(filter(lambda on: on.startswith(text), map(lambda o: o[0], self.options)))

		try:
			return self.complist[state]
		except:
			return None

	def option_yes(self):
		return self.val

	def option_no(self):
		return False

	def option_ls(self):
		print("ls -la '" + self.path + "'")
		subprocess.call(["ls", "-la", "--color=auto", "--", self.path])
		return None

	def option_shell(self):
		print("Spawning shell.")
		print("Type 'exit' to return to this prompt.")
		oldpath = os.getcwd()
		os.chdir(self.path)
		os.system("$SHELL")
		os.chdir(oldpath)
		return None

	def option_change(self):
		try:
			newval = get_line(self.valname + ": ", self.val, self.valcompleter)
			if self.valchecker != None:
				newvalckres = self.valchecker(newval)
			else:
				newvalckres = True

			if newvalckres != True:
				print("Illegal value: " + str(newvalckres))
			else:
				self.val = newval

		except KeyboardInterrupt:
			print("")
			pass
		except EOFError:
			print("")
			pass

		return None

	def option_test(self):
		if not self.testfun():
			print("Test failed")

		return None

	def option_quit(self):
		exit(0)
		return None

	def get_prompt(self):
		if type(self.question) == types.FunctionType:
			prompt = self.question(self.val)
		else:
			prompt = str(self.question)

		prompt += " ["
		for optionname, optionfun in self.options:
			initial = optionname[0]
			if optionname == self.default_answer:
				initial = initial.upper()
			prompt += colored(initial, 1) + optionname[1:] + "/"

		prompt = prompt[:-1] + "]? "
		return prompt

	def run(self):
		if self.always_yes:
			return self.val

		while True:
			res = self.run_once()
			if res != None:
				return res

	def run_once(self):
		try:
			answer = get_line(self.get_prompt(), "", self.completer)
		except KeyboardInterrupt:
			answer = "quit"
			print("")
		except EOFError:
			answer = "quit"
			print("")

		if answer[-1:] == '\n':
			answer = answer[:-1]

		if answer == "":
			answer = self.default_answer

		answer = answer.lower()

		for optionname, optionfun in self.options:
			if optionname.startswith(answer):
				return optionfun()

		print("Illegal answer: " + answer)
		return None

def confirm(question, default_answer = True, path = None, val = True, valname = None, valchecker = None, valcompleter = None, always_yes = False, testfun = None):
	cc = _confirm_class(**locals())
	return cc.run()

def find_mount_point(path):
	path = os.path.realpath(path)
	while not os.path.ismount(path):
		path = os.path.dirname(path)
	return path

def walk(path, parent, parententry, func, traverse_mount_points = False, follow_symlinks=False, depth=-1, parents=set()):
	if depth != 0:
		for entry in os.listdir(path):
			newpath = path + '/' + entry
			if os.path.isdir(newpath):
				if os.path.islink(newpath):
					realnewpath = os.path.realpath(newpath)
					if follow_symlinks and (traverse_mount_points or find_mount_point(realnewpath) == rootdir_mount_point):
						if realnewpath in parents:
							info("loop detected: " + newpath + " -> " + realnewpath)
						else:
							walk(realnewpath, path, entry, func, traverse_mount_points, follow_symlinks, depth - 1, parents.union({path}))
				else:
					newpath = os.path.normpath(newpath)
					if traverse_mount_points or not os.path.ismount(newpath):
						walk(newpath, path, entry, func, traverse_mount_points, follow_symlinks, depth - 1, parents.union({path}))
	
	func(path, parent, parententry)

def rmdir(path):
	if os.path.islink(path):
		print("rm '" + path + "'")
		os.remove(path)
	else:
		print("rmdir '" + path + "'")
		os.rmdir(path)

def rm(path):	
	print("rm '" + path + "'")
	os.remove(path)

def mv(frompath, topath):
	print("mv '" + frompath + "' '" + topath + "'")
	shutil.move(frompath, topath)

def names_similar(a, b):
	return a.replace(' ', '').replace('_', '').lower() == b.replace(' ', '').replace('_', '').lower()

def alt_name(path, i):
	return path + "_" + str(i)

#allowed contains a list of names that should be considered free, even if they are not
def find_free_name(path, name, allowed = []):
	if name in allowed or not os.path.exists(path + "/" + name):
		return name
	else:
		i = 0
		while not name in allowed and os.path.exists(path + "/" + alt_name(name, i)):
			i += 1
		return alt_name(name, i)
