# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module for getting information about the server. """

from asyncio import create_subprocess_shell as asyncrunapp
from asyncio.subprocess import PIPE as asyncPIPE
from platform import python_version, uname
from shutil import which
from os import remove
from telethon import version

from userbot import CMD_HELP, ALIVE_NAME
from userbot.events import register, errors_handler


# ================= CONSTANT =================
DEFAULTUSER = str(ALIVE_NAME) if ALIVE_NAME else uname().node
# ============================================


@register(outgoing=True, pattern="^.sysd$")
@errors_handler
async def sysdetails(sysd):
    """ For .sysd command, get system info using neofetch. """
    if not sysd.text[0].isalpha() and sysd.text[0] not in ("/", "#", "@", "!"):
        try:
            neo = "neofetch --stdout"
            fetch = await asyncrunapp(
                neo,
                stdout=asyncPIPE,
                stderr=asyncPIPE,
            )

            stdout, stderr = await fetch.communicate()
            result = str(stdout.decode().strip()) \
                + str(stderr.decode().strip())

            await sysd.edit("`" + result + "`")
        except FileNotFoundError:
            await sysd.edit("`Install neofetch first !!`")


@register(outgoing=True, pattern="^.botver$")
@errors_handler
async def bot_ver(event):
    """ For .botver command, get the bot version. """
    if not event.text[0].isalpha() and event.text[0] not in (
            "/", "#", "@", "!"):
        if which("git") is not None:
            invokever = "git describe --all --long"
            ver = await asyncrunapp(
                invokever,
                stdout=asyncPIPE,
                stderr=asyncPIPE,
            )
            stdout, stderr = await ver.communicate()
            verout = str(stdout.decode().strip()) \
                + str(stderr.decode().strip())

            invokerev = "git rev-list --all --count"
            rev = await asyncrunapp(
                invokerev,
                stdout=asyncPIPE,
                stderr=asyncPIPE,
            )
            stdout, stderr = await rev.communicate()
            revout = str(stdout.decode().strip()) \
                + str(stderr.decode().strip())

            await event.edit(
                "`Userbot Version: "
                f"{verout}"
                "` \n"
                "`Revision: "
                f"{revout}"
                "`"
            )
        else:
            await event.edit(
                "Shame that you don't have git, You're running 4.0 - 'Extended' anyway"
            )


@register(outgoing=True, pattern="^.pip(?: |$)(.*)")
@errors_handler
async def pipcheck(pip):
    """ For .pip command, do a pip search. """
    if not pip.text[0].isalpha() and pip.text[0] not in ("/", "#", "@", "!"):
        pipmodule = pip.pattern_match.group(1)
        if pipmodule:
            await pip.edit("`Searching . . .`")
            invokepip = f"pip3 search {pipmodule}"
            pipc = await asyncrunapp(
                invokepip,
                stdout=asyncPIPE,
                stderr=asyncPIPE,
            )

            stdout, stderr = await pipc.communicate()
            pipout = str(stdout.decode().strip()) \
                + str(stderr.decode().strip())

            if pipout:
                if len(pipout) > 4096:
                    await pip.edit("`Output too large, sending as file`")
                    file = open("output.txt", "w+")
                    file.write(pipout)
                    file.close()
                    await pip.client.send_file(
                        pip.chat_id,
                        "output.txt",
                        reply_to=pip.id,
                    )
                    remove("output.txt")
                    return
                await pip.edit(
                    "**Query: **\n`"
                    f"{invokepip}"
                    "`\n**Result: **\n`"
                    f"{pipout}"
                    "`"
                )
            else:
                await pip.edit(
                    "**Query: **\n`"
                    f"{invokepip}"
                    "`\n**Result: **\n`No Result Returned/False`"
                )
        else:
            await pip.edit("`Use .help pip to see an example`")


@register(outgoing=True, pattern="^.alive$")
@errors_handler
async def amireallyalive(alive):
    """ For .alive command, check if the bot is running.  """
    if not alive.text[0].isalpha() and alive.text[0] not in (
            "/", "#", "@", "!"):
        await alive.edit(
            "`"
            "My bot is running \n\n"
            f"Telethon version: {version.__version__} \n"
            f"Python: {python_version()} \n"
            f"User: {DEFAULTUSER}"
            "`"
        )


@register(outgoing=True, pattern="^.aliveu")
@errors_handler
async def amireallyaliveuser(username):
    """ For .aliveu command, change the username in the .alive command. """
    if not username.text[0].isalpha(
    ) and username.text[0] not in ("/", "#", "@", "!"):
        message = username.text
        output = '.aliveu [new user without brackets] nor can it be empty'
        if not (message == '.aliveu' or message[7:8] != ' '):
            newuser = message[8:]
            global DEFAULTUSER
            DEFAULTUSER = newuser
            output = 'Successfully changed user to ' + newuser + '!'
        await username.edit(
            "`"
            f"{output}"
            "`"
        )


@register(outgoing=True, pattern="^.resetalive$")
@errors_handler
async def amireallyalivereset(ureset):
    """ For .resetalive command, reset the username in the .alive command. """
    if not ureset.text[0].isalpha() and ureset.text[0] not in (
            "/", "#", "@", "!"):
        global DEFAULTUSER
        DEFAULTUSER = str(ALIVE_NAME) if ALIVE_NAME else uname().node
        await ureset.edit(
            "`"
            "Successfully reset user for alive!"
            "`"
        )

CMD_HELP.update({
    "sysd": ".sysd\
    \nUsage: Shows system information using neofetch."
})
CMD_HELP.update({
    "botver": ".botver\
    \nUsage: Shows the userbot version."
})
CMD_HELP.update({
    "pip": ".pip <module(s)>\
    \nUsage: Does a search of pip modules(s)."
})
CMD_HELP.update({
    "alive": ".alive\
    \nUsage: Type .alive to see wether your bot is working or not.\
    \n\n.aliveu <text>\
    \nUsage: Changes the 'user' in alive to the text you want.\
    \n\n.resetalive\
    \nUsage: Resets the user to default."
})
