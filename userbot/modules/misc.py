# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
# You can find misc modules, which dont fit in anything xD

""" Userbot module for other small commands. """

from random import randint
from time import sleep
from os import execl
import sys
import os
import io
import sys
import json
from userbot import BOTLOG, BOTLOG_CHATID, CMD_HELP
from userbot.events import register
from userbot.events import register, errors_handler


@register(outgoing=True, pattern="^.random")
@errors_handler
async def randomise(items):
    """ For .random command, get a random item from the list of items. """
    if not items.text[0].isalpha() and items.text[0] not in (
            "/", "#", "@", "!"):
        itemo = (items.text[8:]).split()
        index = randint(1, len(itemo) - 1)
        await items.edit("**Query: **\n`" + items.text[8:] + "`\n**Output: **\n`" + itemo[index] + "`")


@register(outgoing=True, pattern="^.sleep( [0-9]+)?$")
@errors_handler
async def sleepybot(time):
    """ For .sleep command, let the userbot snooze for a few second. """
    message = time.text
    if not message[0].isalpha() and message[0] not in ("/", "#", "@", "!"):
        if " " not in time.pattern_match.group(1):
            await time.reply("Syntax: `.sleep [seconds]`")
        else:
            counter = int(time.pattern_match.group(1))
            await time.edit("`I am sulking and snoozing....`")
            sleep(2)
            if BOTLOG:
                await time.client.send_message(
                    BOTLOG_CHATID,
                    "You put the bot to sleep for " + str(counter) + " seconds",
                )
            sleep(counter)


@register(outgoing=True, pattern="^.shutdown$")
@errors_handler
async def killdabot(event):
    """ For .shutdown command, shut the bot down."""
    if not event.text[0].isalpha() and event.text[0] not in (
            "/", "#", "@", "!"):
        await event.edit("`Goodbye *Windows XP shutdown sound*....`")
        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#SHUTDOWN \n"
                "Bot shut down")
        await event.client.disconnect()


@register(outgoing=True, pattern="^.restart$")
@errors_handler
async def killdabot(event):
    if not event.text[0].isalpha() and event.text[0] not in (
            "/", "#", "@", "!"):
        await event.edit("`BRB... *PornHub intro*`")
        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#RESTART \n"
                "Bot Restarted")
        await event.client.disconnect()
        # Spin a new instance of bot
        execl(sys.executable, sys.executable, *sys.argv)
        # Shut the existing one down
        exit()


@register(outgoing=True, pattern="^.community$")
@errors_handler
async def bot_community(community):
    """ For .support command, just returns the group link. """
    if not community.text[0].isalpha(
    ) and community.text[0] not in ("/", "#", "@", "!"):
        await community.edit("Join RaphielGang's awesome userbot community: @userbot_support"
                             "\nDo note that Paperplane Extended is an unoficial fork of their "
                             "Paperplane project and it may get limited or no support for bugs.")


@register(outgoing=True, pattern="^.support$")
@errors_handler
async def bot_support(wannahelp):
    """ For .support command, just returns the group link. """
    if not wannahelp.text[0].isalpha(
    ) and wannahelp.text[0] not in ("/", "#", "@", "!"):
        await wannahelp.edit("Join the Paperplane Extended Channel: @PaperplaneExtended")


@register(outgoing=True, pattern="^.creator$")
@errors_handler
async def creator(e):
    if not e.text[0].isalpha() and e.text[0] not in ("/", "#", "@", "!"):
        await e.edit("[AvinashReddy3108](https://t.me/AvinashReddy3108)")


@register(outgoing=True, pattern="^.readme$")
@errors_handler
async def reedme(e):
    if not e.text[0].isalpha() and e.text[0] not in ("/", "#", "@", "!"):
        await e.edit("Here's something for you to read:\n"
                     "\n[Paperplane Extended's README.md file](https://github.com/AvinashReddy3108/PaperplaneExtended/blob/sql-extended/README.md)"
                     "\n[Setup Guide - Basic](https://telegra.ph/How-to-host-a-Telegram-Userbot-07-24)"
                     "\n[Setup Guide - Google Drive](https://telegra.ph/How-To-Setup-GDrive-07-27)"
                     "\n[Setup Guide - LastFM Module](https://telegra.ph/How-to-set-up-LastFM-module-for-Paperplane-userbot-08-10)")


# Copyright (c) Gegham Zakaryan | 2019
@register(outgoing=True, pattern="^.repeat (.*)")
@errors_handler
async def repeat(rep):
    if not rep.text[0].isalpha() and rep.text[0] not in ("/", "#", "@", "!"):
        cnt, txt = rep.pattern_match.group(1).split(' ', 1)
        replyCount = int(cnt)
        toBeRepeated = txt

        replyText = toBeRepeated + "\n"

        for i in range(0, replyCount - 1):
            replyText += toBeRepeated + "\n"

        await rep.edit(replyText)


@register(outgoing=True, pattern="^.repo$")
@errors_handler
async def repo_is_here(wannasee):
    """ For .repo command, just returns the repo URL. """
    if not wannasee.text[0].isalpha(
    ) and wannasee.text[0] not in ("/", "#", "@", "!"):
        await wannasee.edit("Click [here](https://github.com/AvinashReddy3108/PaperplaneExtended) to open Paperplane Extended's GitHub page.")


@register(outgoing=True, pattern="^.json$")
@errors_handler
async def json(event):
    if not event.text[0].isalpha() and event.text[0] not in (
            "/", "#", "@", "!"):
        the_real_message = None
        reply_to_id = None
        if event.reply_to_msg_id:
            previous_message = await event.get_reply_message()
            the_real_message = previous_message.stringify()
            reply_to_id = event.reply_to_msg_id
        else:
            the_real_message = event.stringify()
            reply_to_id = event.message.id

        with io.BytesIO(str.encode(the_real_message)) as out_file:
            out_file.name = "message.json"
            await event.client.send_file(
                event.chat_id,
                out_file,
                force_document=True,
                allow_cache=False,
                reply_to=reply_to_id,
                caption="`Here's the decoded message data !!`"
            )
            await event.delete()

CMD_HELP.update({
    'random': '.random <item1> <item2> ... <itemN>\
\nUsage: Get a random item from the list of items.'
})

CMD_HELP.update({
    'sleep': '.sleep <seconds>\
\nUsage: Userbots get tired too. Let yours snooze for a few seconds.'
})

CMD_HELP.update({
    "shutdown": ".shutdown\
\nUsage: Sometimes you need to shut down your bot. Sometimes you just hope to\
hear Windows XP shutdown sound... but you don't."
})

CMD_HELP.update({
    'support': ".support\
\nUsage: If you need help, use this command."
})

CMD_HELP.update({
    'community': ".community\
\nUsage: Join the awesome Paperplane userbot community !!"
})

CMD_HELP.update({
    'repo': '.repo\
\nUsage: If you are curious what makes the userbot work, this is what you need.'
})

CMD_HELP.update({
    "readme": ".readme\
\nUsage: Provide links to setup the userbot and it's modules."
})

CMD_HELP.update({
    "creator": ".creator\
\nUsage: Know who created this awesome userbot !!"
})

CMD_HELP.update({
    "repeat": ".repeat <no.> <text>\
\nUsage: Repeats the text for a number of times. Don't confuse this with spam tho."
})

CMD_HELP.update({
    "restart": ".restart\
\nUsage: Restart the bot !!"
})

CMD_HELP.update({
    "json": ".json\
\nUsage: Get detailed JSON formatted data about replied message"
})
