# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.

import asyncio
from asyncio import sleep

from userbot import CMD_HELP
from userbot.events import register


@register(outgoing=True, pattern=r"^\.cspam (.+)")
async def tmeme(e):
    cspam = str(e.pattern_match.group(1))
    message = cspam.replace(" ", "")
    await e.delete()
    for letter in message:
        await e.respond(letter)


@register(outgoing=True, pattern=r"^\.wspam (.+)")
async def t_meme(e):
    wspam = str(e.pattern_match.group(1))
    message = wspam.split()
    await e.delete()
    for word in message:
        await e.respond(word)


@register(outgoing=True, pattern=r"^\.spam (\d+) (.+)")
async def spammers(e):
    counter = int(e.pattern_match.group(1))
    spam_message = str(e.pattern_match.group(2))
    await e.delete()
    await asyncio.wait([e.respond(spam_message) for i in range(counter)])


@register(outgoing=True, pattern=r"^\.picspam (\d+) (.+)")
async def tiny_pic_spam(e):
    counter = int(e.pattern_match.group(1))
    link = str(e.pattern_match.group(2))
    await e.delete()
    for _ in range(1, counter):
        await e.client.send_file(e.chat_id, link)


@register(outgoing=True, pattern=r"^\.delayspam (\d+) (\d+) (.+)")
async def spammer(e):
    spamDelay = float(e.pattern_match.group(1))
    counter = int(e.pattern_match.group(2))
    spam_message = str(e.pattern_match.group(3))
    await e.delete()
    for _ in range(1, counter):
        await e.respond(spam_message)
        await sleep(spamDelay)


CMD_HELP.update(
    {
        "spam": ">`.cspam <text>`"
        "\nUsage: Spam the text letter by letter."
        "\n\n>`.spam <count> <text>`"
        "\nUsage: Floods text in the chat!"
        "\n\n>`.wspam <text>`"
        "\nUsage: Spam the text word by word."
        "\n\n>`.picspam <count> <link to image/gif>`"
        "\nUsage: As if text spam was not enough!"
        "\n\n>`.delayspam <delay> <count> <text>`"
        "\nUsage: .spam but with custom delay."
        "\n\n\n**NOTE: Spam at your own risk!**"
    }
)
