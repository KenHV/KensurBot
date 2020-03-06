# Copyright (C) 2020 Adek Maulana.
# All rights reserved.
#
# Redistribution and use of this script, with or without modification, is
# permitted provided that the following conditions are met:
#
# 1. Redistributions of this script must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
#  THIS SOFTWARE IS PROVIDED BY THE AUTHOR "AS IS" AND ANY EXPRESS OR IMPLIED
#  WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
#  MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO
#  EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
#  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
#  WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
#  OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
#  ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from asyncio import create_subprocess_shell as asyncSubprocess
from asyncio.subprocess import PIPE as asyncPIPE

import asyncio
import re
import json
import os
import multiprocessing
import errno

from pySmartDL import SmartDL
from urllib.error import HTTPError

from userbot import CMD_HELP, LOGS
from userbot.events import register
from userbot.modules.upload_download import humanbytes


async def subprocess_run(cmd, megadl):
    subproc = await asyncSubprocess(cmd, stdout=asyncPIPE, stderr=asyncPIPE)
    stdout, stderr = await subproc.communicate()
    exitCode = subproc.returncode
    if exitCode != 0:
        await megadl.edit(
            '**An error was detected while running subprocess**\n'
            f'```exit code: {exitCode}\n'
            f'stdout: {stdout.decode().strip()}\n'
            f'stderr: {stderr.decode().strip()}```')
        return exitCode
    return stdout, stderr


@register(outgoing=True, pattern=r"^.mega(?: |$)(.*)")
async def mega_downloader(megadl):
    await megadl.edit("`Processing...`")
    msg_link = await megadl.get_reply_message()
    link = megadl.pattern_match.group(1)
    if link:
        pass
    elif msg_link:
        link = msg_link.text
    else:
        await megadl.edit("Usage: `.mega <mega url>`")
        return
    try:
        link = re.findall(r'\bhttps?://.*mega.*\.nz\S+', link)[0]
    except IndexError:
        await megadl.edit("`No MEGA.nz link found`\n")
        return
    cmd = f'bin/megadown -q -m {link}'
    result = await subprocess_run(cmd, megadl)
    try:
        data = json.loads(result[0].decode().strip())
    except json.JSONDecodeError:
        await megadl.edit("`Error: Can't extract the link`\n")
        return
    except TypeError:
        return
    except IndexError:
        return
    file_name = data["file_name"]
    file_url = data["url"]
    hex_key = data["hex_key"]
    hex_raw_key = data["hex_raw_key"]
    temp_file_name = file_name + ".temp"
    downloaded_file_name = "./" + "" + temp_file_name
    downloader = SmartDL(
        file_url, downloaded_file_name, progress_bar=False)
    display_message = None
    try:
        downloader.start(blocking=False)
    except HTTPError as e:
        await megadl.edit("`" + str(e) + "`")
        return
    while not downloader.isFinished():
        status = downloader.get_status().capitalize()
        total_length = downloader.filesize if downloader.filesize else None
        downloaded = downloader.get_dl_size()
        percentage = int(downloader.get_progress() * 100)
        progress = downloader.get_progress_bar()
        speed = downloader.get_speed(human=True)
        estimated_total_time = downloader.get_eta(human=True)
        try:
            current_message = (
                "File Name:"
                f"\n`{file_name}`\n\n"
                "Status:"
                f"\n**{status}** | {progress} `{percentage}%`"
                f"\n{humanbytes(downloaded)} of {humanbytes(total_length)}"
                f" @ {speed}"
                f"\nETA: {estimated_total_time}"
            )
            if display_message != current_message:
                await megadl.edit(current_message)
                await asyncio.sleep(0.2)
                display_message = current_message
        except Exception:
            pass
        finally:
            if status == "Combining":
                await asyncio.sleep(float(downloader.get_eta()))
    if downloader.isSuccessful():
        download_time = downloader.get_dl_time(human=True)
        try:
            P = multiprocessing.Process(target=await decrypt_file(
                file_name, temp_file_name, hex_key, hex_raw_key, megadl), name="Decrypt_File")
            P.start()
            P.join()
        except FileNotFoundError as e:
            await megadl.edit(str(e))
            return
        else:
            await megadl.edit(f"`{file_name}`\n\n"
                              "Successfully downloaded\n"
                              f"Download took: {download_time}")
    else:
        await megadl.edit("Failed to download, check heroku Log for details")
        for e in downloader.get_errors():
            LOGS.info(str(e))
    return


async def decrypt_file(file_name, temp_file_name,
                       hex_key, hex_raw_key, megadl):
    cmd = ("cat '{}' | openssl enc -d -aes-128-ctr -K {} -iv {} > '{}'"
           .format(temp_file_name, hex_key, hex_raw_key, file_name))
    if await subprocess_run(cmd, megadl):
        os.remove(temp_file_name)
    else:
        raise FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), file_name)
    return


CMD_HELP.update({
    "mega":
    ".mega <mega url>\n"
    "Usage: Reply to a mega link or paste your mega link to\n"
    "download the file into your userbot server\n\n"
    "Only support for *FILE* only."
})
