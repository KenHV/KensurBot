# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot help command """

from userbot import CMD_HELP
from userbot.events import register


@register(outgoing=True, pattern=r"^\.help(?: |$)(.*)")
async def help(event):
    """ For .help command,"""
    args = event.pattern_match.group(1).lower()
    if args:
        if args in CMD_HELP:
            await event.edit(str(CMD_HELP[args]))
        else:
            await event.edit("Please specify a valid module name.")
    else:
        unsorted = ""
        sorted = "**"
        for i in CMD_HELP:
            unsorted += str(i) + " "
        unsorted = unsorted.split()
        unsorted.sort()
        for i in unsorted:
            sorted += str(i) + " | "
        help_message = ("To view help for specific module, do `.help` <module_name>"
                f"\nList of available modules:\n\n**{sorted[:-3]}")
        await event.edit(help_message)
