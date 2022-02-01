# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Init file which loads all of the modules """
from userbot import LOGS, MODULES_EXCLUDE_LIST


def __list_all_modules():
    import glob
    from os.path import basename, dirname, isfile

    mod_paths = glob.glob(dirname(__file__) + "/*.py")
    return [
        basename(f)[:-3]
        for f in mod_paths
        if isfile(f) and f.endswith(".py") and not f.endswith("__init__.py")
    ]


MODULES = sorted(__list_all_modules())

if MODULES_EXCLUDE_LIST:
    ALL_MODULES = []
    for i in MODULES:
        if i not in MODULES_EXCLUDE_LIST:
            ALL_MODULES.append(i)
else:
    ALL_MODULES = MODULES


LOGS.info("Modules to load: %s", str(ALL_MODULES))
__all__ = ALL_MODULES + ["ALL_MODULES"]
