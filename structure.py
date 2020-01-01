"""Generic structural methods"""

import os, sys
import json
import shutil
import re
import platform
import subprocess
import logging

__author__ = "Arda Kutlu"
__copyright__ = "Copyright 2019, Library Structure Functions"
__credits__ = []
__license__ = "GPL"
__maintainer__ = "Arda Kutlu"
__email__ = "ardakutlu@gmail.com"
__status__ = "Development"

logging.basicConfig()
logger = logging.getLogger('structure')
logger.setLevel(logging.WARNING)


def loadJson(file):
    """Loads the given json file"""
    # TODO : Is it paranoid checking?
    if os.path.isfile(file):
        try:
            with open(file, 'r') as f:
                data = json.load(f)
                return data
        except ValueError:
            msg = "Corrupted JSON file => %s" % file
            logger.error(msg)

    else:
        msg = "File cannot be found => %s" % file
        logger.error(msg)

def dumpJson(data, file):
    """Saves the data to the json file"""
    # this wont work with python 3.x. Either use compatibilty module from tik_manager or remove 'unicode'
    name, ext = os.path.splitext(unicode(file).encode("utf-8"))
    tempFile = ("{0}.tmp".format(name))
    with open(tempFile, "w") as f:
        json.dump(data, f, indent=4)
    shutil.copyfile(tempFile, file)
    os.remove(tempFile)

def copytree(src, dst, symlinks=False, ignore=None):
    """
    Copies entire content of the given directory to the destination recursively
    (Derived directly from  shutil.copytree)
    :param src: (String) source directory path
    :param dst: (String) destination directory path
    :param symlinks: (Boolean) If True, uses resolves symlinks too. Default False
    :param ignore: (Function) use include_patterns function to ignore specific files.

    Example:
    copytree(source, destination, ignore=include_patterns('*.dwg', '*.dxf'))
    :return:
    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    if not os.path.isdir(dst):  # This one line does the trick
        os.makedirs(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                shutil.copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except shutil.Error as err:
            errors.extend(err.args[0])
        except EnvironmentError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        shutil.copystat(src, dst)
    except OSError as why:
        if WindowsError is not None and isinstance(why, WindowsError):
            # Copying file access times may fail on Windows
            pass
        else:
            errors.extend((src, dst, str(why)))
    if errors:
        raise shutil.Error(errors)

def niceName(filepath):
    """Gets the base name of the given filename"""
    basename = os.path.split(filepath)[1]
    return os.path.splitext(basename)[0]

def nameCheck(text, allowSpaces=False, directory=False):
    """
    Checks the text for illegal characters
    :param text: (String) text to be checked
    :param allowSpaces: (Boolean) If True, spaces wont count as a problem
    :param directory: (Boolean) If True, the text will be treated as a directory
    :return: (Boolean) True if passes the check, False if fails
    """
    aSpa = " " if allowSpaces else ""
    dir = "\\\\:" if directory else ""

    pattern = r'^[:/A-Za-z0-9%s%s.A_-]*$' %(dir, aSpa)

    if re.match(pattern, text):
        return True
    else:
        return False

def folderCheck(folderPath):
    """Checks if the folder exists, creates it if doesnt"""
    if not os.path.isdir(os.path.normpath(folderPath)):
        os.makedirs(os.path.normpath(folderPath))
    return folderPath

def showInExplorer(tpath):
    """Opens the path in Windows Explorer(Windows) or Nautilus(Linux)"""
    currentPlatform = platform.system()
    if os.path.isfile(tpath):
        tpath = os.path.dirname(tpath)
    if currentPlatform == "Windows":
        os.startfile(tpath)
    elif currentPlatform == "Linux":
        subprocess.Popen(["xdg-open", tpath])
    else:
        subprocess.Popen(["open", tpath])

