import argparse
import os
import subprocess
import shutil

from dirtreeflattener import args, util

def flatten_dir(path, parent, parententry):
	if parent == None or (args.traverse_mount_points and os.path.ismount(path)):
		return

	nameinparent = parent + "/" + parententry

	files = os.listdir(path)
	if len(files) == 0:
		if args.remove_empty_dirs:
			question = "Remove empty directory '" + path + "'"
			if util.confirm(question, default_answer = args.default_yes, path = parent, always_yes = args.always):
				util.rmdir(nameinparent)

	elif len(files) == 1:
		#move single entry of dir to parent dir, and delete dir
		if util.names_similar(files[0], parententry):
			#filename is similar to parent filename, do not concatenate
			newname = files[0]
		else:
			newname = parententry + " - " + files[0]

		#find a free new name for the file
		newname = parent + "/" + util.find_free_name(parent, newname, [parententry])

		while True:
			def question(newname):
				result = "Move '"
				result += parent + "/" + util.colored(parententry + "/" + files[0], 36)
				result += "' to '"
				result += util.colored(os.path.relpath(newname, parent), 36)
				result += "'"
				return result
			def checker(newname):
				if newname == "":
					return "Path is empty"
				elif os.path.exists(newname) and os.path.normpath(newname) != os.path.normpath(parent + "/" + parententry):
					return "Path exists"
				else:
					return True

			newname = util.confirm(question, default_answer = args.default_yes, path = parent, val = newname, valname = "move to", valchecker = checker, valcompleter = util.filename_completer(), always_yes = args.always)
			if newname == False:
				break
			newname = os.path.normpath(newname)

			#if newname is equal to the dirname, we need to rename the dir first ('mv a b', 'mv b/a a', 'rmdir b')
			if os.path.normpath(parent + '/' + parententry) == newname:
				newparententry = util.find_free_name(parent, parententry)
				util.mv(parent + '/' + parententry, parent + '/' + newparententry)
				parententry = newparententry

			#check whether the file would be moved into a subdirectory of its old location
			if shutil._destinsrc(parent + '/' + parententry, newname):
				print("Can not move file to a subdirectory of its old location")

				if args.always:
					break
				else:
					continue

			#if the parent directory of newname does not exist yet, create it
			newdirname = util.dirname(newname)
			if not os.path.exists(newdirname):
				os.makedirs(newdirname)

			#move
			util.mv(parent + '/' + parententry + '/' + files[0], newname)
			util.rmdir(parent + '/' + parententry)

			break
