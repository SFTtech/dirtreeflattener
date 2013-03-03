import argparse
import os
import subprocess
import shutil

from dirtreeflattener import args, util, unpack, flatten

def main():
	#parse arguments
	args.parse()

	#check the root directory
	if not os.path.isdir(args.rootdir):
		util.fatal(args.rootdir + " is not a directory")
	rootdir_mount_point = util.find_mount_point(args.rootdir)

	#unpack archives in root directory structure
	if not args.no_unpack:
		util.walk(args.rootdir, unpack.unpack_dir, traverse_mount_points = args.traverse_mount_points, follow_symlinks = args.follow_symlinks, depth = args.depth)

	#flatten root directory structure
	if not args.no_flatten:
		util.walk(args.rootdir, flatten.flatten_dir, traverse_mount_points = args.traverse_mount_points, follow_symlinks = args.follow_symlinks, depth = args.depth)
