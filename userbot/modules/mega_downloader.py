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

from humanize import naturalsize
from subprocess import PIPE, Popen

import re
import json
import wget
import os

from userbot import CMD_HELP
from userbot.events import register


def subprocess_run(cmd):
    subproc = Popen(cmd, stdout=PIPE, stderr=PIPE,
                    shell=True, universal_newlines=True)
    talk = subproc.communicate()
    exitCode = subproc.returncode
    if exitCode != 0:
        print('An error was detected while running the subprocess:\n'
              'exit code: %d\n'
              'stdout: %s\n'
              'stderr: %s' % (exitCode, talk[0], talk[1]))
    return talk


@register(outgoing=True, pattern=r"^.mega(?: |$)(.*)")
async def mega_downloader(event):
    await event.edit("`Processing...`")
    textx = await event.get_reply_message()
    link = event.pattern_match.group(1)
    if link:
        pass
    elif textx:
        link = textx.text
    else:
        await event.edit("`Usage: .mega <mega url>`")
        return
    reply = ''
    if not link:
        reply = "`No MEGA.nz link found!`"
        await event.edit(reply)
    await event.edit("`Downloading...`")
    reply += mega_download(link)
    await event.edit(reply)


def mega_download(url: str) -> str:
    reply = ''
    try:
        link = re.findall(r'\bhttps?://.*mega.*\.nz\S+', url)[0]
    except IndexError:
        reply = "`No MEGA.nz link found`\n"
        return reply
    cmd = f'bin/megadirect {link}'
    result = subprocess_run(cmd)
    try:
        data = json.loads(result[0])
        print(data)
    except json.JSONDecodeError:
        reply += "`Error: Can't extract the link`\n"
        return reply
    file_name = data['file_name']
    file_size = naturalsize(int(data['file_size']))
    file_url = data['url']
    file_hex = data['hex']
    file_raw_hex = data['raw_hex']
    if wget.download(file_url, out=file_name):
        encrypt_file(file_name, file_hex, file_raw_hex)
        reply += (f"`{file_name}`\n"
                  f"Size: {file_size}\n"
                  "\n"
                  "Successfully downloaded...")
    else:
        reply += "Failed to download..."
    return reply


def encrypt_file(file_name, file_hex, file_raw_hex):
    os.rename(file_name, f"old_{file_name}")
    cmd = f"cat old_{file_name} | openssl enc -d -aes-128-ctr -K {file_hex} -iv {file_raw_hex} > {file_name}"
    subprocess_run(cmd)
    os.remove(f"old_{file_name}")
    return


CMD_HELP.update({
    "mega":
    ".mega <mega url>\n"
    "Usage: Reply to a mega link or paste your mega link to\n"
    "download the file into your userbot server\n\n"
    "Only support for *FILE* only.\n"
})
