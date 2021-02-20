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
import wget
import os

def humanbytes(size: float) -> str:
    """ humanize size """
    if not size:
        return ""
    power = 1024
    t_n = 0
    power_dict = {0: ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        t_n += 1
    return "{:.2f} {}B".format(size, power_dict[t_n])


@register(outgoing=True, pattern="^.speed$")
async def speedtst(spd):
    """ For .speed command, use SpeedTest to check server speeds. """
    await spd.edit("`Running speed test . . .`")
    test = Speedtest()

    test.get_best_server()
    test.download()
    test.upload()
    test.results.share()
    result = test.results.dict()
    path = wget.download(result["share"])
    output = f"⌛ Started at `{result['timestamp']}`\n\n"
    output += "☁️ Client:\n\n"
    output += f"🖥 ISP: `{result['client']['isp']}`\n"
    output += f"⚙ Country: `{result['client']['country']}`\n\n"
    output += "📬 Server:\n"
    output += f"🌀 Name: `{result['server']['name']}`\n"
    output += f"🏁 Country: `{result['server']['country']}, {result['server']['cc']}`\n"
    output += f"🌐 Sponsor: `{result['server']['sponsor']}`\n\n"
    output += f"📶 Ping: `{result['ping']}`\n"
    output += f"⬆️ Sent: `{humanbytes(result['bytes_sent'])}`\n"
    output += f"⬇️ Received: `{humanbytes(result['bytes_received'])}`\n"
    output += f"🔼 Upload: `{humanbytes(result['upload'] / 8)}/s\n`"
    output += f"🔽 Download: `{humanbytes(result['download'] / 8)}/s`\n"
    await spd.delete()
    await spd.client.send_file(spd.chat_id, path, caption=output, force_document=False)
    os.remove(path)
    
    
def speed_convert(size):
    """
    Hi human, you can't read bytes?
    """
    power = 2**10
    zero = 0
    units = {0: "", 1: "Kb/s", 2: "Mb/s", 3: "Gb/s", 4: "Tb/s"}
    while size > power:
        size /= power
        zero += 1
    return f"{round(size, 2)} {units[zero]}"


@register(outgoing=True, pattern=r"^\.dc$")
async def neardc(event):
    """ For .dc command, get the nearest datacenter information. """
    result = await event.client(functions.help.GetNearestDcRequest())
    await event.edit(f"Country : `{result.country}`\n"
                     f"Nearest Datacenter : `{result.nearest_dc}`\n"
                     f"This Datacenter : `{result.this_dc}`")


@register(outgoing=True, pattern=r"^\.ping$")
async def pingme(pong):
    """ For .ping command, ping the userbot from any chat.  """
    start = datetime.now()
    await pong.edit("`Pong!`")
    end = datetime.now()
    duration = (end - start).microseconds / 1000
    await pong.edit("`Pong!\n%sms`" % (duration))


CMD_HELP.update({
    "speed":
    ">`.speed`"
    "\nUsage: Does a speedtest and shows the results.",
    "dc":
    ">`.dc`"
    "\nUsage: Finds the nearest datacenter from your server.",
    "ping":
    ">`.ping`"
    "\nUsage: Shows how long it takes to ping your bot.",
})
