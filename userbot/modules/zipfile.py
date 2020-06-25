# Copyright (C) 2020 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
#
# Port from UniBorg to Userbot by yincen17

import asyncio
import zipfile
from userbot.events import register
from datetime import date
import time
import os
from userbot import TEMP_DOWNLOAD_DIRECTORY, ZIP_DOWNLOAD_DIRECTORY, bot, CMD_HELP
from userbot.utils import progress

# ====================
today = date.today()
# ====================

@register(outgoing=True, pattern=r"^\.compress(?: |$)(.*)")
async def _(event):
    #Prevent Channel Bug to use update
    if event.is_channel and not event.is_group:
        await event.edit("`Compress Command isn't permitted on channels`")
        return
    if event.fwd_from:
        return
    if not event.is_reply:
        await event.edit("`Reply to a file to compress it.`")
        return
    mone = await event.edit("`Processing ...`")
    if not os.path.isdir(TEMP_DOWNLOAD_DIRECTORY):
        os.makedirs(TEMP_DOWNLOAD_DIRECTORY)
    if event.reply_to_msg_id:
        reply_message = await event.get_reply_message()
        try:
            c_time = time.time()
            downloaded_file_name = await bot.download_media(
                reply_message,
                TEMP_DOWNLOAD_DIRECTORY,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(d, t, mone, c_time, "`Trying to download`")
                )
            )
            directory_name = downloaded_file_name
            await event.edit(downloaded_file_name)
        except Exception as e:  # pylint:disable=C0103,W0703
            await mone.edit(str(e))
    zipfile.ZipFile(directory_name + '.zip', 'w', zipfile.ZIP_DEFLATED).write(directory_name)
    await bot.send_file(
        event.chat_id,
        directory_name + ".zip",
        force_document=True,
        allow_cache=False,
        reply_to=event.message.id,
    )
    await event.edit("`DONE!!!`")
    await asyncio.sleep(7)
    await event.delete()


@register(outgoing=True, pattern=r"^\.addzip(?: |$)(.*)")
async def addzip(add):
    """ Copyright (c) 2020 azrim @github"""
    #Prevent Channel Bug to use update
    if add.is_channel and not add.is_group:
        await add.edit("`Command isn't permitted on channels`")
        return
    if add.fwd_from:
        return
    if not add.is_reply:
        await add.edit("`Reply to a file to compress it.`")
        return
    mone = await add.edit("`Processing ...`")
    if not os.path.isdir(ZIP_DOWNLOAD_DIRECTORY):
        os.makedirs(ZIP_DOWNLOAD_DIRECTORY)
    if add.reply_to_msg_id:
        reply_message = await add.get_reply_message()
        try:
            c_time = time.time()
            downloaded_file_name = await bot.download_media(
                reply_message,
                ZIP_DOWNLOAD_DIRECTORY,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(d, t, mone, c_time, "`Trying to download`")
                )
            )
            success = str(downloaded_file_name).replace("./zips/", "")
            await add.edit(f"`{success} Successfully added to list`")
        except Exception as e:  # pylint:disable=C0103,W0703
            await mone.edit(str(e))
            return


@register(outgoing=True, pattern=r"^\.upzip(?: |$)(.*)")
async def upload_zip(up):
    if not os.path.isdir(ZIP_DOWNLOAD_DIRECTORY):
        await up.edit(f"`Files not found`")
        return
    await up.edit(f"`Uploading.......`")
    input_str = up.pattern_match.group(1)
    curdate = today.strftime("%m%d%y")
    title = str(input_str) if input_str else "zipfile" + f"{curdate}"
    zipf = zipfile.ZipFile(title + '.zip', 'w', zipfile.ZIP_DEFLATED)
    zipdir(ZIP_DOWNLOAD_DIRECTORY, zipf)
    zipf.close()
    await bot.send_file(
        up.chat_id,
        title + ".zip",
        force_document=True,
        allow_cache=False,
        reply_to=up.message.id,
    )
    os.rmdir(ZIP_DOWNLOAD_DIRECTORY)
    await up.delete()

@register(outgoing=True, pattern=r"^\.rmzip(?: |$)(.*)")
async def remove_dir(rm):
    if not os.path.isdir(ZIP_DOWNLOAD_DIRECTORY):
        await rm.edit(f"`Directory not found`")
        return
    os.rmdir(ZIP_DOWNLOAD_DIRECTORY)
    await rm.edit("`Zip list removed`")


def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, _, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))
            os.remove(os.path.join(root, file))


CMD_HELP.update({
        "zipfile":
        ".compress **[optional: <reply to file>]**\
            \nUsage: make files to zip.\
            \n.addzip **<reply to file>**\
            \nUsage: add files to zip list.\
            \n.upzip **[optional: <zip title>]**\
            \nUsage: upload zip list.\
            \n.rmzip **[optional: <zip title>]**\
            \nUsage: clear zip list."
})
