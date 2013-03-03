import argparse

argparser = argparse.ArgumentParser(description="Flatten directory structure")
argparser.add_argument("--no-unpack", action="store_true", default=False, help="If set, no archive unpacking will be performed")
argparser.add_argument("--no-flatten", action="store_true", default=False, help="If set, no flattening will be performed")
argparser.add_argument("--remove-empty-dirs", action="store_true", default=False, help="If set, empty directories will be removed during flattening")
argparser.add_argument("--always", action="store_true", default=False, help="If set, all actions are performed without confirmation")
argparser.add_argument("--default-yes", action="store_true", default=False, help="If set, the default option is 'Yes' instead of 'No' in confirmation dialogs")
argparser.add_argument("--follow-symlinks", action="store_true", default=False, help="If set, symlinks will be resolved")
argparser.add_argument("--traverse-mount-points", action="store_true", default=False, help="If set, subdirectories will be handled even if from a different filesystem")
argparser.add_argument("--depth", type=int, default=-1, help="Search depth")
argparser.add_argument("rootdir", default='.', nargs='?', help="The root directory")

def parse():
	globals().update(argparser.parse_args().__dict__)
