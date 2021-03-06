#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""
An implementation of stow in Python.

This program assumes that the dotfiles folder is located at
$HOME/dotfiles.

It will by default create symlinked folders instead of symlinking just files.

TODO:
* Make copy-ing work.
* Make it possible to pass a directory as an argument
* Replacing doesn't work for directories
* Recode replace_symlink()
* Fix script creating bad symlinks and removing things it should not.
"""

import argparse
import os
import pathlib
import re
import shutil
import sys
import textwrap

# Globals
IGNORE = [".git"]
PATTERN = re.compile(r"\\{1,2}x1b.*?m")

parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent("""\
                A symlinking script for handling dotfiles in a similar manner to stow.

                WARNING: This script may crush your dreams (and files) if you are
                not careful. Read the prompts carefully."""))


parser.add_argument("--root", dest="root", action="store_true", default=False,
                    help="when running as root, symlink to your home directory as well")

file_actions = parser.add_mutually_exclusive_group()
file_actions.add_argument("-f", "--files", dest="files", action="store_true", default=False,
                          help="only symlink to files")
file_actions.add_argument("-c", "--copy", dest="copy", action="store_true", default=False,
                          help="copy instead of symlink")

confirm = parser.add_mutually_exclusive_group()
confirm.add_argument("-s", "--skip", dest="skip", action="store_true", default=False,
                     help="skip any conflicts")
confirm.add_argument("-N", "--NO", dest="no", action="store_true", default=False,
                     help="do nothing")
confirm.add_argument("-Y", "--YES", dest="yes", action="store_true", default=False,
                     help="say yes to all prompts")

modes = parser.add_mutually_exclusive_group()
modes.add_argument("-r", "--remove", dest="remove", action="store_true", default=False,
                   help="remove all existing files (you will be prompted)")
modes.add_argument("-R", "--replace", dest="replace", action="store_true", default=False,
                   help="replace all existing files (you will be prompted)")

args = parser.parse_args()

# Ensure that only files are symlinked when in root
if args.root:
    args.files = True


class Colour:
    def __init__(self):
        if supports_color():
            self.RED = "\033[1;31m"
            self.GREEN = "\033[0;32m"
            self.YELLOW = "\033[0;33m"
            self.BLUE = "\033[1;34m"
            self.CYAN = "\033[1;36m"
            self.RESET = "\033[0;0m"
            self.BOLD = "\033[;1m"
            self.REVERSE = "\033[;7m"
        else:
            self.RED = ""
            self.GREEN = ""
            self.YELLOW = ""
            self.BLUE = ""
            self.CYAN = ""
            self.RESET = ""
            self.BOLD = ""
            self.REVERSE = ""

    def colours(self):
        return list(self.__dict__.values())


class StopTraversing(Exception):
    def __init__(self, message):
        super().__init__(message)


# https://github.com/django/django/blob/master/django/core/management/color.py
def supports_color():
    """
    Return True if the running system's terminal supports color,
    and False otherwise.
    """
    plat = sys.platform
    supported_platform = plat != 'Pocket PC' and \
        (plat != 'win32' or 'ANSICON' in os.environ)

    is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    if not supported_platform or not is_a_tty:
        return False
    return True


def symlink(origin, target):
    """
    Control function that takes the correct action depending on arguments
    """
    # Skip anything in the home directory if the user is admin
    if user_is_admin() and not args.root and check_contain_home_dir(target):
        print(highlight_colour("'%s'") % str(target) +
              warning_colour(" is inside of home folder. Skipping..."))
        raise StopTraversing("Skipping.")

    # Check for a broken symlink, if true: prompt for replacement.
    # This is done to avoid having any broken symlinks lingering.
    if is_broken_symlink(target):
        if args.yes or prompt(origin, target, "remove"):
            target.unlink()
        else:
            return

    if args.replace:
        replace_symlink(origin, target)
    elif args.remove:
        remove_symlink(origin, target)
    else:
        create_symlink(origin, target)


def create_symlink(origin, target):
    try:
        if target.exists() or target.is_symlink():
            print(highlight_colour("'%s'") % str(target) +
                  warning_colour(" already exists. Skipping..."))
            raise StopTraversing("Skipping.")

        elif args.yes or prompt(origin, target):
            target.symlink_to(origin, origin.is_dir())

    except PermissionError as e:
        print(error_colour("ERROR: Permission denied when attempting to access " +
                           "'%s'" % highlight_colour(str(origin)) +
                           error_colour(" and ") +
                           "'%s'" % highlight_colour(str(target))))


def replace_symlink(origin, target):
    if target.exists() or target.is_symlink():
        if args.skip or not args.replace:
            if home != pathlib.Path(*target.parts[:3]):
                print(reverse_highlight("'%s'") % str(target) +
                      warning_colour(" already exists. Skipping..."))
                raise StopTraversing("Skipping.")
            else:
                print(highlight_colour("'%s'") % str(target) +
                      warning_colour(" already exists. Skipping..."))
                raise StopTraversing("Skipping.")

        if target is more_recent(origin, target):
            if args.yes or prompt(origin, target, "replace"):
                # TODO: replacing doesn't work for directories
                if target.is_dir():
                    shutil.rmtree(str(target))
                else:
                    target.replace(origin)
                target.symlink_to(origin, origin.is_dir())
                return

        if args.yes or prompt(origin, target, "replace"):
            if not args.root and home != pathlib.Path(*target.parts[:3]):
                print(highlight_colour("'%s'") % str(target) +
                      warning_colour(" is outside of home folder. Skipping..."))

                raise StopTraversing("Skipping.")

            if target.is_file() or target.is_symlink():
                target.unlink()

            elif target.is_dir():
                shutil.rmtree(str(target))  # very scary

            target.symlink_to(origin, origin.is_dir())


def remove_symlink(origin, target):
    if args.remove:
        if not args.root and home != pathlib.Path(*target.parts[:3]):
            print(highlight_colour("'%s'") % str(target) +
                  warning_colour(" is outside of home folder. Skipping..."))
            return

        if args.yes or prompt(origin, target, "remove"):
            if target.is_file() or target.is_symlink():
                target.unlink()

            elif target.is_dir():
                shutil.rmtree(str(target))  # very scary


def is_broken_symlink(path):
    # https://stackoverflow.com/questions/20794/find-broken-symlinks-with-python
    return os.path.islink(str(path)) and not os.path.exists(str(path))


def more_recent(origin, target):
    if origin.exists() and target.exists():
        if target.stat().st_mtime > origin.stat().st_mtime:
            return target
        return origin
    return None


def check_contain_home_dir(path):
    return str(get_home()) in str(path)


def prompt(origin, target, action="symlink"):
    colour = Colour()
    text = colour.BOLD + action.capitalize() + colour.RESET

    if action == "remove":
        text += " '%s'?" % highlight_colour(str(target))
    elif action == "replace":
        text += " '%s' with '%s'?" % \
                (highlight_colour(str(target)), highlight_colour(str(origin)))
    else:
        text += " '%s' to '%s'?" % \
                (highlight_colour(str(origin)), highlight_colour(str(target)))
    if not args.no or not args.yes:
        text += "\n[y(es) / n(o); Y(ES) (to all) / N(O) (to all)]: "

        if is_broken_symlink(target) and (action == "remove"):
            text = text.replace(": ", "") + \
                    error_colour("\nWARNING: Target symlink is broken (removal recommended): ")
        elif target.is_dir() and (action == "replace" or action == "remove"):
            text = text.replace(": ", "") + error_colour(
                    "\nWARNING: This will delete all contents in the target directory: ")
        elif target is more_recent(origin, target) and action == "replace":
            text = text.replace(": ", "") + error_colour(
                    "\nWARNING: Target file is newer than the one you are \
    trying to symlink. Would you like the replace the older file with the newer and symlink?: ")
        elif target.is_file() and (action == "replace" or action == "remove"):
            text = text.replace(": ", "") + \
                    error_colour("\nWARNING: This will delete the existing target file: ")

    if args.no or args.yes:
        print(text)
        return args.yes

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
            sys.exit("Exiting...")


def print_ln(origin, target):
    if args.remove:
        print("unlink %s" % str(target))
    elif args.replace:
        print("unlink %s" % str(target))
        print("ln -s %s %s" % (str(origin), str(target)))
    else:
        print("ln -s %s %s" % (str(origin), str(target)))


def remove_colour_chars(s):
    global PATTERN
    return bytes(re.sub(PATTERN, r"", repr(s))[1:-1], "utf-8").decode("unicode_escape")


def get_colour(s):
    global PATTERN
    colour = Colour()
    res = re.findall(PATTERN, repr(s))
    if res:
        return bytes(res[0], "utf-8").decode("unicode_escape")
    return bytes(colour.RESET.strip("'\""), "utf-8").decode("unicode_escape")


def warning_colour(s):
    colour = Colour()
    prev_colour = get_colour(s)
    return colour.YELLOW + remove_colour_chars(s) + prev_colour


def error_colour(s):
    colour = Colour()
    prev_colour = get_colour(s)
    return colour.RED + remove_colour_chars(s) + prev_colour


def highlight_colour(s):
    colour = Colour()
    prev_colour = get_colour(s)
    return colour.CYAN + remove_colour_chars(s) + prev_colour


def reverse_highlight(s):
    colour = Colour()
    prev_colour = get_colour(s)
    return colour.REVERSE + colour.CYAN + remove_colour_chars(s) + prev_colour


def traverse_subdirs(origin):
    global IGNORE
    for subdir, dirs, files in os.walk(str(origin), topdown=True):
        # https://stackoverflow.com/questions/19859840/excluding-directories-in-os-walk
        [dirs.remove(d) for d in list(dirs) if d in IGNORE]
        subdir = pathlib.Path(subdir)
        target = target_path(subdir)

        if not args.files or not args.copy:
            if target.is_symlink() or not target.exists():
                try:
                    symlink(subdir, target)
                except StopTraversing:
                    pass
                continue

        for f in files:
            f = pathlib.Path(str(subdir) + "/" + f)
            target = target_path(f)
            try:
                symlink(f, target)
            except StopTraversing:
                continue


def target_path(origin):
    # Remove home path / dotfiles / <this dir> /
    pattern = re.compile(str(get_home() / "dotfiles") + "/[^/]*")
    target = pathlib.Path(re.sub(pattern, "", str(origin)))
    if "etc" in origin.parts:
        return pathlib.Path("/etc" + str(target))
    else:
        return pathlib.Path(str(get_home()) + str(target))


def user_is_admin():
    # Windows
    if os.name == "nt":
        import ctypes
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            print(warning_colour("ERROR: Admin check failed, assuming non-admin user."))
            return False

    # unix
    elif os.name == "posix":
        return os.getuid() == 0


def get_home():
    # Assumes if the user is running the script as admin,
    # that the script is located in the user's home folder
    if user_is_admin():
        return pathlib.Path(*pathlib.Path(os.path.abspath(sys.argv[0])).parts[0:3])
    else:
        return pathlib.Path(os.path.expanduser('~'))  # pathlib.Path.Home() only works in 3.5 onwards


if __name__ == "__main__":
    colour = Colour()
    if user_is_admin():
        print(warning_colour("WARNING: You are running this program as root. \
Any symlinks created outside of your home directory may pose a security risk to \
your system, proceed with great caution."))
        home = get_home()
        while True:
            text = "Is '%s' your home directory? (y/n): " % highlight_colour(str(home))
            inp = input(text)
            if inp == "" or inp == "y":
                break
            elif inp == "n":
                while True:
                    home = input("Please specify your home directory: ")
                    home = pathlib.Path(home)
                    break
    else:
        home = get_home()

    dotfiles_dir = home / "dotfiles"

    if not dotfiles_dir.is_dir():
        sys.exit(error_colour("ERROR: ") + highlight_colour("'%s'" % str(dotfiles_dir)) +
                 error_colour(" is not a directory."))

    for path in dotfiles_dir.iterdir():
        if path.is_dir() and path.stem not in IGNORE:
            for sub_path in path.iterdir():
                traverse_subdirs(sub_path)

