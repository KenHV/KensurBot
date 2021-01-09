# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
# The entire source code is OSSRPL except
# 'download, uploadir, uploadas, upload' which is MPL
# License: MPL and OSSRPL
""" Userbot module which contains everything related to
     downloading/uploading from/to the server. """

import asyncio
import math
import os
import subprocess
import time
from datetime import datetime

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from pySmartDL import SmartDL
from telethon.tl.types import DocumentAttributeFilename, DocumentAttributeVideo

from userbot import CMD_HELP, LOGS, TEMP_DOWNLOAD_DIRECTORY
from userbot.events import register
from userbot.utils import humanbytes, progress
from userbot.utils.FastTelethon import download_file, upload_file


@register(pattern=r"\.download(?: |$)(.*)", outgoing=True)
async def download(target_file):
    """ For .download command, download files to the userbot's server. """
    await target_file.edit("**Processing...**")
    input_str = target_file.pattern_match.group(1)
    if not os.path.isdir(TEMP_DOWNLOAD_DIRECTORY):
        os.makedirs(TEMP_DOWNLOAD_DIRECTORY)
    if "|" in input_str:
        url, file_name = input_str.split("|")
        url = url.strip()
        # https://stackoverflow.com/a/761825/4723940
        file_name = file_name.strip()
        head, tail = os.path.split(file_name)
        if head and not os.path.isdir(os.path.join(TEMP_DOWNLOAD_DIRECTORY, head)):
            os.makedirs(os.path.join(TEMP_DOWNLOAD_DIRECTORY, head))
            file_name = os.path.join(head, tail)
        downloaded_file_name = TEMP_DOWNLOAD_DIRECTORY + "" + file_name
        downloader = SmartDL(url, downloaded_file_name, progress_bar=False)
        downloader.start(blocking=False)
        c_time = time.time()
        display_message = None
        while not downloader.isFinished():
            status = downloader.get_status().capitalize()
            total_length = downloader.filesize or None
            downloaded = downloader.get_dl_size()
            now = time.time()
            diff = now - c_time
            percentage = downloader.get_progress() * 100
            speed = downloader.get_speed()
            progress_str = "[{}{}] `{}%`".format(
                "".join("●" for i in range(math.floor(percentage / 10))),
                "".join("○" for i in range(10 - math.floor(percentage / 10))),
                round(percentage, 2),
            )

            estimated_total_time = downloader.get_eta(human=True)
            try:
                current_message = (
                    f"**Name:** `{file_name}`\n"
                    f"\n**{status}...** | {progress_str}"
                    f"\n{humanbytes(downloaded)} of {humanbytes(total_length)}"
                    f" @ {humanbytes(speed)}"
                    f"\n**ETA:** {estimated_total_time}"
                )

                if round(diff % 10.00) == 0 and current_message != display_message:
                    await target_file.edit(current_message)
                    display_message = current_message
            except Exception as e:
                LOGS.info(str(e))
        if downloader.isSuccessful():
            await target_file.edit(
                f"**Downloaded to** `{downloaded_file_name}` **successfully!**"
            )
        else:
            await target_file.edit(f"**Incorrect URL**\n{url}")
    elif target_file.reply_to_msg_id:
        try:
            replied = await target_file.get_reply_message()
            file = replied.document
            attribs = replied.media.document.attributes
            for attr in attribs:
                if isinstance(attr, DocumentAttributeFilename):
                    filename = attr.file_name
            outdir = TEMP_DOWNLOAD_DIRECTORY + filename
            c_time = time.time()
            start_time = datetime.now()
            with open(outdir, "wb") as f:
                result = await download_file(
                    client=target_file.client,
                    location=file,
                    out=f,
                    progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                        progress(d, t, target_file, c_time, "[DOWNLOAD]", input_str)
                    ),
                )
            dl_time = (datetime.now() - start_time).seconds
        except Exception as e:  # pylint:disable=C0103,W0703
            await target_file.edit(str(e))
        else:
            await target_file.edit(
                f"**Downloaded to** `{result.name}` **in** `{dl_time} seconds`**!**"
            )
    else:
        await target_file.edit("**Reply to a message to download to my local server.**")


async def get_video_thumb(file, output=None, width=90):
    """ Get video thumbnail """
    command = f"ffmpeg -i {file} -ss 00:00:01.000 -filter:v scale={width}:-1 -vframes 1 {output}"
    subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    await asyncio.sleep(2.5)
    return output


@register(pattern=r"^\.upload (.*)", outgoing=True)
async def upload(u_event):
    """ For .upload command, allows you to upload a file from the userbot's server """
    await u_event.edit("Processing ...")
    input_str = u_event.pattern_match.group(1)
    if input_str in ("userbot.session", "config.env"):
        return await u_event.edit("`That's a dangerous operation! Not Permitted!`")
    if os.path.exists(input_str):
        file_name = input_str.split("/")[-1]
        c_time = time.time()
        start_time = datetime.now()
        with open(input_str, "rb") as f:
            result = await upload_file(
                client=u_event.client,
                file=f,
                name=file_name,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(d, t, u_event, c_time, "[FILE - UPLOAD]", input_str)
                ),
            )
        up_time = (datetime.now() - start_time).seconds
        if input_str.lower().endswith(("mp4", "mkv", "webm")):
            thumb = await get_video_thumb(input_str, output="thumb_image.jpg")
            metadata = extractMetadata(createParser(input_str))
            duration = 0
            width = 0
            height = 0
            if metadata.has("duration"):
                duration = metadata.get("duration").seconds
            if metadata.has("width"):
                width = metadata.get("width")
            if metadata.has("height"):
                height = metadata.get("height")
            await u_event.client.send_file(
                u_event.chat_id,
                result,
                thumb=thumb,
                caption=file_name,
                force_document=False,
                allow_cache=False,
                reply_to=u_event.message.id,
                attributes=[
                    DocumentAttributeVideo(
                        duration=duration,
                        w=width,
                        h=height,
                        round_message=False,
                        supports_streaming=True,
                    )
                ],
            )
            os.remove(thumb)
            await u_event.edit(f"Uploaded successfully in `{up_time}` seconds.")
        else:
            await u_event.client.send_file(
                u_event.chat_id,
                result,
                caption=file_name,
                force_document=False,
                allow_cache=False,
                reply_to=u_event.message.id,
            )
            await u_event.edit(f"Uploaded successfully in `{up_time}` seconds.")
    else:
        await u_event.edit("`404: File Not Found`")


CMD_HELP.update(
    {
        "download": ">`.download <link|filename> or reply to media`"
        "\nUsage: Downloads file to the server."
        "\n\n>`.upload <path in server>`"
        "\nUsage: Uploads a locally stored file to the chat."
    }
)
