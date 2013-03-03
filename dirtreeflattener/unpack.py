import argparse
import os
import subprocess
import shutil

from dirtreeflattener import util, args

def unpack_zip(archive, to):
	print("unzip -o -d'" + to + "' '" + archive + "'")
	return subprocess.call(['unzip', '-o', '-d' + to, '--', archive]) == 0

def test_zip(archive):
	print("unzip -t '" + archive + "'")
	return subprocess.call(['unzip', '-t', '--', archive]) == 0

def unpack_rar(archive, to):
	if not os.path.isdir(to):
		os.makedirs(to)

	print("unrar x -y '" + archive + "' '" + to + "'")
	return subprocess.call(['unrar', 'x', '-y', '--', archive, to]) == 0

def test_rar(archive):
	print("unrar t '" + archive + "'")
	return subprocess.call(['unrar', 't', '--', archive]) == 0

def unpack_tgz(archive, to):
	if not os.path.isdir(to):
		os.makedirs(to)

	print("tar xzv --file='" + archive + "' -C'" + to + "'")
	return subprocess.call(['tar', 'xzv', '--file=' + archive, '-C' + to]) == 0

def test_tgz(archive):
	print("tar tzv --file='" + archive + "'")
	return subprocess.call(['tar', 'tzv', '--file=' + archive]) == 0

def unpack_dir(path, parent, parententry):
	for entry in os.listdir(path):
		name = path + "/" + entry
		if not os.path.isfile(name):
			continue

		funcs = None
		lowername = name.lower()
		if lowername.endswith('.rar'):
			funcs = (unpack_rar, test_rar)
		elif lowername.endswith('.zip'):
			funcs = (unpack_zip, test_zip)
		elif lowername.endswith('.tar.gz') or lowername.endswith('.tgz'):
			funcs = (unpack_tgz, test_tgz)

		if funcs != None:
			to_path = path + '/' + util.find_free_name(path, os.path.splitext(entry)[0])
			def question(to_path):
				result = "unpack '"
				result += path + '/' + util.colored(entry, 36)
				result += "' to '"
				result += util.colored(os.path.relpath(to_path, path), 36) + "/"
				result += "'"
				return result
			def checker(to_path):
				if to_path == "":
					return "Path is empty"
				elif os.path.exists(to_path):
					return "Path exists"
				else:
					return True
			while True:
				to_path = util.confirm(question, default_answer = args.default_yes, path = path, val = to_path, valname = "target directory", valchecker = checker, valcompleter = util.filename_completer(), always_yes = args.always, testfun = lambda: funcs[1](path + '/' + entry))
				if to_path == False:
					break

				to_path = os.path.normpath(to_path)

				if not funcs[0](name, to_path):
					util.nonfatal("Could not unpack '" + name + "' to '" + to_path + "'")
					if args.always:
						break
					else:
						continue

				util.rm(name)

				break
