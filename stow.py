#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""
An implementation of stow in Python.

This program assumes that the dotfiles folder is located at
$HOME/dotfiles.

It will by default create symlinked folders instead of symlinking just files.

TODO:
* Make an option to disable symlinked folder creation
"""

__author__ = "curious"

import argparse
import os
import pathlib
import shutil
import textwrap

from sys import exit

# Globals
ignore = [".git"]

parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent("""\
                A symlinking script for handling dotfiles in a similar manner to stow.

                WARNING: This script may crush your dreams (and files) if you are
                not careful. Read the prompts carefully."""))

# parser.add_argument("-v", "--verbose", dest="verbose", action="store_true", default=False,
#                     help="verbose mode")

confirm = parser.add_mutually_exclusive_group()
confirm.add_argument("-s", "--skip", dest="skip", action="store_true", default=False,
                     help="skip any conflicts")
confirm.add_argument("-N", "--NO", dest="no", action="store_true", default=False,
                     help="don't perform any actions, just print the results.")
confirm.add_argument("-Y", "--YES", dest="yes", action="store_true", default=False,
                     help="say yes to all prompts")

modes = parser.add_mutually_exclusive_group()
modes.add_argument("-r", "--remove", dest="remove", action="store_true", default=False,
                   help="remove all existing files (you will be prompted)")
modes.add_argument("-R", "--replace", dest="replace", action="store_true", default=False,
                   help="replace all existing files (you will be prompted)")
args = parser.parse_args()

if args.yes or args.no:
    args.verbose = True


class Colour:
    RED = "\033[1;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[0;33m"
    BLUE = "\033[1;34m"
    CYAN = "\033[1;36m"
    RESET = "\033[0;0m"
    BOLD = "\033[;1m"
    REVERSE = "\033[;7m"


def symlink(origin, target):
    if args.no:
        return

    if args.yes:  # or args.verbose:
        print_ln(origin, target)

    if args.remove:
        if pathlib.Path.home() != pathlib.Path(*target.parts[:3]):
            print(warning_colour("Skipping '%s'. It is outside of home folder." %
                                 str(target)))
            return

        if target.is_file() or target.is_symlink():
            if args.yes or prompt(origin, target, "remove"):
                target.unlink()
                return

        elif target.is_dir():
            shutil.rmtree(str(target))  # very scary
            return

    else:
        if target.exists():
            if args.skip:
                print("Skipping '%s', already exists..." % str(target))
                return

            if args.replace or args.yes or prompt(origin, target, "replace"):
                if pathlib.Path.home() != pathlib.Path(*target.parts[:3]):
                    print(warning_colour("Skipping '%s'. It is outside of home folder." %
                                         str(target)))
                    return

                if target.is_file() or target.is_symlink():
                    target.unlink()

                elif target.is_dir():
                    shutil.rmtree(str(target))  # very scary

                target.symlink_to(origin, origin.is_dir())
                return
        else:
            if args.yes or prompt(origin, target):
                target.symlink_to(origin, origin.is_dir())


def traverse_subdirs(origin):
    global ignore
    for subdir, dirs, files in os.walk(origin, topdown=True):
        # https://stackoverflow.com/questions/19859840/excluding-directories-in-os-walk
        [dirs.remove(d) for d in list(dirs) if d in ignore]
        subdir = pathlib.Path(subdir)
        target = target_path(subdir)

        # Symlink folders if target is empty or already a symlink
        if not target.exists():
            symlink(subdir, target)
            continue

        if target.is_symlink():
            symlink(subdir, target)
            continue

        # if sum([1 for d in subdir.iterdir()]) == 0:  # if directory is empty
        #    symlink(subdir, target)
        #    continue

        for f in files:
            f = pathlib.Path(str(subdir) + "/" + f)
            target = target_path(f)
            symlink(f, target)
            # if [f.stem == x.stem for x in (origin.glob("*.*"))]:  # if file exists


def target_path(origin):
    if "etc" in origin.parts:
        target = "/" / pathlib.Path(*origin.parts[4:])
    else:
        target = pathlib.Path.home() / pathlib.Path(*origin.parts[5:])
    return target


def prompt(origin, target, action="symlink"):
    colour = Colour()
    text = colour.BOLD + action.capitalize() + colour.RESET
    if action == "remove":
        text += " '%s'?" % highlight_colour(str(target))
    elif action == "replace":
        text += " '%s' with '%s'?" % \
                (highlight_colour(str(origin)), highlight_colour(str(target)))
    else:
        text += " '%s' to '%s'?" % \
                (highlight_colour(str(origin)), highlight_colour(str(target)))
    text += "\n[y(es) / n(o); Y(ES) (to all) / N(O) (to all)]: "

    if target.is_dir() and (action == "replace" or action == "remove"):
        text = text.replace(": ", "") + \
                error_colour("\nWARNING: This will delete all contents in the directory: ")
    elif target.is_file() and (action == "replace" or action == "remove"):
        text = text.replace(": ", "") + \
                error_colour("\nWARNING: This will delete the target file: ")

    while True:
        inp = input(text)
        if len(inp) == 0:
            return True
        elif inp.startswith("y"):
            return True
        elif inp.startswith("n"):
            return False
        elif inp.startswith("Y"):
            args.yes = True
            return True
        elif inp.startswith("N"):
            exit("Exiting.")
            args.no = True
            return False


def print_ln(origin, target):
    if args.remove:
        print("unlink %s" % str(target))
    elif args.replace:
        print("unlink %s" % str(target))
        print("ln -s %s %s" % (str(origin), str(target)))

    else:
        print("ln -s %s %s" % (str(origin), str(target)))


def warning_colour(s):
    colour = Colour()
    return colour.YELLOW + s + colour.RESET


def error_colour(s):
    colour = Colour()
    return colour.RED + s + colour.RESET


def highlight_colour(s):
    colour = Colour()
    return colour.CYAN + s + colour.RESET



if __name__ == "__main__":
    colour = Colour()
    dotfiles_dir = pathlib.Path(pathlib.Path.home() / "dotfiles")

    if not dotfiles_dir.is_dir():
        exit(colour.RED + "ERROR: '%s' is not a directory."
             % str(dotfiles_dir) + colour.RESET)

    for path in dotfiles_dir.iterdir():
        if path.is_dir() and path.stem not in ignore:
            try:
                traverse_subdirs(path)
            except PermissionError:
                exit(error_colour("ERROR: Permission denied. Please run the script as root if you want to symlink outside of home folder"))


