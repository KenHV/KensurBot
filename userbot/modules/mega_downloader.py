# Copyright (C) 2020 Adek Maulana.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
#

from asyncio import create_subprocess_shell as asyncSubprocess
from asyncio.subprocess import PIPE as asyncPIPE

import asyncio
import re
import json
import os
import multiprocessing
import errno
import math
import time

from pySmartDL import SmartDL
from urllib.error import HTTPError

from userbot import CMD_HELP, LOGS, TEMP_DOWNLOAD_DIRECTORY
from userbot.events import register
from userbot.utils import humanbytes, time_formatter


async def subprocess_run(megadl, cmd):
    subproc = await asyncSubprocess(cmd, stdout=asyncPIPE, stderr=asyncPIPE)
    stdout, stderr = await subproc.communicate()
    exitCode = subproc.returncode
    if exitCode != 0:
        await megadl.edit(
            '**An error was detected while running subprocess.**\n'
            f'exitCode : `{exitCode}`\n'
            f'stdout : `{stdout.decode().strip()}`\n'
            f'stderr : `{stderr.decode().strip()}`')
        return exitCode
    return stdout.decode().strip(), stderr.decode().strip(), exitCode


@register(outgoing=True, pattern=r"^\.mega(?: |$)(.*)")
async def mega_downloader(megadl):
    await megadl.edit("`Collecting information...`")
    if not os.path.isdir(TEMP_DOWNLOAD_DIRECTORY):
        os.makedirs(TEMP_DOWNLOAD_DIRECTORY)
    msg_link = await megadl.get_reply_message()
    link = megadl.pattern_match.group(1)
    if link:
        pass
    elif msg_link:
        link = msg_link.text
    else:
        return await megadl.edit("Usage: `.mega` **<MEGA.nz link>**")
    try:
        link = re.findall(r'\bhttps?://.*mega.*\.nz\S+', link)[0]
        """ - Mega changed their URL again - """
        if "file" in link:
            link = link.replace("#", "!").replace("file/", "#!")
        elif "folder" in link or "#F" in link or "#N" in link:
            await megadl.edit("`folder download support are removed...`")
            return
    except IndexError:
        return await megadl.edit("`MEGA.nz link not found...`")
    cmd = f'bin/megadown -q -m {link}'
    result = await subprocess_run(megadl, cmd)
    try:
        data = json.loads(result[0])
    except json.JSONDecodeError:
        return await megadl.edit("`Err: failed to extract link...`\n")
    except (IndexError, TypeError):
        return
    file_name = data["file_name"]
    file_url = data["url"]
    hex_key = data["hex_key"]
    hex_raw_key = data["hex_raw_key"]
    temp_file_name = file_name + ".temp"
    temp_file_path = TEMP_DOWNLOAD_DIRECTORY + temp_file_name
    file_path = TEMP_DOWNLOAD_DIRECTORY + file_name
    if os.path.isfile(file_path):
        try:
            raise FileExistsError(
                errno.EEXIST, os.strerror(errno.EEXIST), file_path)
        except FileExistsError as e:
            return await megadl.edit(f"`{str(e)}`")
    downloader = SmartDL(
        file_url, temp_file_path, progress_bar=False)
    display_message = None
    try:
        downloader.start(blocking=False)
    except HTTPError as e:
        return await megadl.edit(f"`Err: {str(e)}`")
    start = time.time()
    while not downloader.isFinished():
        status = downloader.get_status().capitalize()
        total_length = downloader.filesize if downloader.filesize else None
        downloaded = downloader.get_dl_size()
        percentage = int(downloader.get_progress() * 100)
        speed = downloader.get_speed(human=True)
        estimated_total_time = round(downloader.get_eta())
        progress_str = "`{0}` | [{1}{2}] `{3}%`".format(
            status,
            ''.join(["▰" for i in range(
                    math.floor(percentage / 10))]),
            ''.join(["▱" for i in range(
                    10 - math.floor(percentage / 10))]),
            round(percentage, 2))
        diff = time.time() - start
        try:
            current_message = (
                f"`{file_name}`\n\n"
                "Status\n"
                f"{progress_str}\n"
                f"`{humanbytes(downloaded)} of {humanbytes(total_length)}"
                f" @ {speed}`\n"
                f"`ETA` -> {time_formatter(estimated_total_time)}\n"
                f"`Duration` -> {time_formatter(round(diff))}"
            )
            if round(diff % 10.00) == 0 and (
                display_message != current_message or total_length == downloaded
            ):
                await megadl.edit(current_message)
                await asyncio.sleep(2)
                display_message = current_message
        except Exception:
            pass
        finally:
            if status == "Combining":
                wait = round(downloader.get_eta())
                await asyncio.sleep(wait)
    if downloader.isSuccessful():
        download_time = round(downloader.get_dl_time() + wait)
        try:
            P = multiprocessing.Process(target=await decrypt_file(megadl,
                                                                  file_path, temp_file_path,
                                                                  hex_key, hex_raw_key),
                                        name="Decrypt_File")
            P.start()
            P.join()
        except FileNotFoundError as e:
            return await megadl.edit(f"`{str(e)}`")
        else:
            return await megadl.edit(
                f"`{file_name}`\n\n"
                f"Successfully downloaded in: `'{file_path}'`.\n"
                f"Download took: {time_formatter(download_time)}.")
    else:
        await megadl.edit("`Failed to download, "
                          "check heroku Logs for more details`.")
        for e in downloader.get_errors():
            LOGS.info(str(e))
    return


async def decrypt_file(megadl, file_path, temp_file_path,
                       hex_key, hex_raw_key):
    cmd = ("cat '{}' | openssl enc -d -aes-128-ctr -K {} -iv {} > '{}'"
           .format(temp_file_path, hex_key, hex_raw_key, file_path))
    if await subprocess_run(megadl, cmd):
        os.remove(temp_file_path)
    else:
        raise FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), file_path)
    return


CMD_HELP.update({
    "mega":
    "`.mega <MEGA.nz link>`"
    "\nUsage: Reply to a MEGA.nz link or paste your MEGA.nz link to "
    "download the file into your userbot server."
})
