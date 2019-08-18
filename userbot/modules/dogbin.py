# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.b (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module containing commands for interacting with dogbin(https://del.dog)"""

from requests import get, post, exceptions
import asyncio
import os
from userbot import BOTLOG, BOTLOG_CHATID, CMD_HELP, LOGS, TEMP_DOWNLOAD_DIRECTORY
from userbot.events import register

DOGBIN_URL = "https://del.dog/"

@register(outgoing=True, pattern=r"^.paste(?: |$)([\s\S]*)")
async def paste(pstl):
    """ For .paste command, pastes the text directly to dogbin. """
    if not pstl.text[0].isalpha() and pstl.text[0] not in ("/", "#", "@", "!"):
        dogbin_final_url = ""
        match = pstl.pattern_match.group(1).strip()
        reply_id = pstl.reply_to_msg_id

        if not match and not reply_id:
            await pstl.edit("Elon Musk said I cannot paste void.")
            return

        if match:
            message = match
        elif reply_id:
            message = (await pstl.get_reply_message())
            if message.media:
                downloaded_file_name = await pstl.client.download_media(
                    message,
                    TEMP_DOWNLOAD_DIRECTORY,
                )
                m_list = None
                with open(downloaded_file_name, "rb") as fd:
                    m_list = fd.readlines()
                message = ""
                for m in m_list:
                    message += m.decode("UTF-8") + "\r"
                os.remove(downloaded_file_name)
            else:
                message = message.message

        # Dogbin
        await pstl.edit("`Pasting text . . .`")
        resp = post(DOGBIN_URL + "documents", data=message.encode('utf-8'))

        if resp.status_code == 200:
            response = resp.json()
            key = response['key']
            dogbin_final_url = DOGBIN_URL + key

            if response['isUrl']:
                reply_text = (
                    "`Pasted successfully!`\n\n"
                    f"`Shortened URL:` {dogbin_final_url}\n\n"
                    "`Original(non-shortened) URLs`\n"
                    f"`Dogbin URL`: {DOGBIN_URL}v/{key}\n")
            else:
                reply_text = (
                    "`Pasted successfully!`\n\n"
                    f"`Dogbin URL`: {dogbin_final_url}")
        else:
            reply_text = (
                "`Failed to reach Dogbin`")

        await pstl.edit(reply_text)
        if BOTLOG:
            await pstl.client.send_message(
                BOTLOG_CHATID,
                f"Paste query was executed successfully",
            )


@register(outgoing=True, pattern="^.getpaste(?: |$)(.*)")
async def get_dogbin_content(dog_url):
    """ For .getpaste command, fetches the content of a dogbin URL. """
    if not dog_url.text[0].isalpha() and dog_url.text[0] not in ("/", "#", "@", "!"):
        textx = await dog_url.get_reply_message()
        message = dog_url.pattern_match.group(1)
        await dog_url.edit("`Getting dogbin content . . .`")

        if textx:
            message = str(textx.message)

        format_normal = f'{DOGBIN_URL}'
        format_view = f'{DOGBIN_URL}v/'

        if message.startswith(format_view):
            message = message[len(format_view):]
        elif message.startswith(format_normal):
            message = message[len(format_normal):]
        elif message.startswith("del.dog/"):
            message = message[len("del.dog/"):]
        else:
            await dog_url.edit("`Is that even a dogbin url?`")
            return

        resp = get(f'{DOGBIN_URL}raw/{message}')

        try:
            resp.raise_for_status()
        except exceptions.HTTPError as HTTPErr:
            await dog_url.edit("Request returned an unsuccessful status code.\n\n" + str(HTTPErr))
            return
        except exceptions.Timeout as TimeoutErr:
            await dog_url.edit("Request timed out."+ str(TimeoutErr))
            return
        except exceptions.TooManyRedirects as RedirectsErr:
            await dog_url.edit("Request exceeded the configured number of maximum redirections." + str(RedirectsErr))
            return

        reply_text = "`Fetched dogbin URL content successfully!`\n\n`Content:` " + resp.text

        await dog_url.edit(reply_text)
        if BOTLOG:
            await dog_url.client.send_message(
                BOTLOG_CHATID,
                "Get dogbin content query was executed successfully",
            )

CMD_HELP.update({
    "dogbin": ".paste <text/reply>\
\nUsage: Create a paste or a shortened url using dogbin (https://del.dog/)\
\n\n.getpaste\
\nUsage: Gets the content of a paste or shortened url from dogbin (https://del.dog/)"
})
