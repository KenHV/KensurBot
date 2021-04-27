# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module containing commands related to the \
    Information Superhighway (yes, Internet). """

from datetime import datetime

from speedtest import Speedtest
from telethon import functions

from userbot import CMD_HELP
from userbot.events import register
from userbot.utils import humanbytes


@register(outgoing=True, pattern=r"^\.speedtest$")
async def speedtst(event):
    """For .speed command, use SpeedTest to check server speeds."""
    await event.edit("**Running speed test...**")

    test = Speedtest()
    test.get_best_server()
    test.download()
    test.upload()
    test.results.share()
    result = test.results.dict()

    msg = (
        f"**Ping:** `{result['ping']}`\n"
        f"**Upload:** `{humanbytes(result['upload'])}/s`\n"
        f"**Download:** `{humanbytes(result['download'])}/s`\n\n"
        "**Client**\n"
        f"**ISP:** `{result['client']['isp']}`\n"
        f"**Country:** `{result['client']['country']}`\n\n"
        "**Server**\n"
        f"**Name:** `{result['server']['name']}`\n"
        f"**Country:** `{result['server']['country']}`\n"
        f"**Sponsor:** `{result['server']['sponsor']}`\n\n"
    )

    await event.client.send_file(
        event.chat_id,
        result["share"],
        caption=msg,
    )
    await event.delete()


@register(outgoing=True, pattern=r"^\.dc$")
async def neardc(event):
    """For .dc command, get the nearest datacenter information."""
    result = await event.client(functions.help.GetNearestDcRequest())
    await event.edit(
        f"**Country:** `{result.country}`\n"
        f"**Nearest datacenter:** `{result.nearest_dc}`\n"
        f"**This datacenter:** `{result.this_dc}`"
    )


@register(outgoing=True, pattern=r"^\.ping$")
async def pingme(event):
    """For .ping command, ping the userbot from any chat."""
    start = datetime.now()
    await event.edit("**Pong!**")
    end = datetime.now()
    duration = (end - start).microseconds / 1000
    await event.edit("**Pong!\n%sms**" % (duration))


CMD_HELP.update(
    {
        "speedtest": ">`.speedtest`" "\nUsage: Does a speedtest and shows the results.",
        "dc": ">`.dc`" "\nUsage: Finds the nearest datacenter from your server.",
        "ping": ">`.ping`" "\nUsage: Shows how long it takes to ping your bot.",
    }
)
