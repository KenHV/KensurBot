# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
# You can find misc modules, which dont fit in anything xD
#
# Edited module from oub to sayhi by @akuajiz
""" Userbot module for other small commands. """
import sys
from userbot import CMD_HELP
from userbot.events import register

@register(outgoing=True, pattern="^.sayhi$")
async def shalom(e):
    await e.edit(
        "\n💰💰💰💰💰💰💰💰💰"
        "\n💰🔷🔷🔷🔷🔷🔷🔷💰"
        "\n💰💰💰💰🔷💰💰💰💰"
        "\n💰💰💰💰🔷💰💰💰💰"
        "\n💰💰💰💰🔷💰💰💰💰"
        "\n💰🔷🔷🔷🔷️🔷🔷🔷💰"
        "\n💰💰💰💰💰💰💰💰💰"
        "\n💰💰💰💰💰💰💰💰💰"
        "\n💰🔷💰💰️💰💰💰🔷💰"
        "\n💰🔷🔷🔷🔷🔷🔷🔷💰"
        "\n💰🔷🔷🔷🔷🔷🔷️🔷💰"
        "\n💰🔷💰💰💰💰️💰🔷💰"
        "\n💰💰💰💰💰💰💰💰💰")
        
    
    CMD_HELP.update({
    'sayhi':
    '.sayhi\
\nUsage: Say hi to everyone as output.'
})




