# Copyright (C) 2020 GengKapak and AnggaR96s.
# All rights reserved.

import requests
import json
import os
from userbot import CMD_HELP, TEMP_DOWNLOAD_DIRECTORY
from userbot.events import register


@register(outgoing=True, pattern=r"^\.ts (.*)")
async def torrent(event):
    await event.edit("`Searching...`")
    query = event.pattern_match.group(1)
    response = requests.get(
        f"https://sjprojectsapi.herokuapp.com/torrent/?query={query}")
    ts = json.loads(response.text)
    if ts != response.json():
        await event.edit("`Error: Try again later.`")
        return
    listdata = ""
    run = 0
    while True:
        try:
            run += 1
            r1 = ts[run]
            list1 = "<-----{}----->\nName: {}\nSeeders: {}\nSize: {}\nAge: {}\n<--Magnet Below-->\n{}\n\n\n".format(
                run, r1['name'], r1['seeder'], r1['size'], r1['age'], r1['magnet'])
            listdata += list1
        except:
            break

    if not listdata:
        return await event.edit("`Error: No results found`")

    await event.edit("`Uploading results...`")
    tsfileloc = f"{TEMP_DOWNLOAD_DIRECTORY}/{query}.txt"
    with open(tsfileloc, "w+", encoding="utf8") as out_file:
        out_file.write(str(listdata))
    caption = f"Torrents for:` {query}`"
    await event.client.send_file(
        event.chat_id,
        tsfileloc,
        caption=caption,
        force_document=False)
    os.remove(tsfileloc)
    await event.delete()


CMD_HELP.update({
    "torrent":
    ">`.ts` <query>"
    "\nUsage: Search for torrents of given query"
})
