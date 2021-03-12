# Kanged from UniBorg
# Modified by AnggaR96s

import asyncio
import json
import os

from userbot import CMD_HELP, TEMP_DOWNLOAD_DIRECTORY
from userbot.events import register


@register(
    outgoing=True,
    pattern=r"^\.web ?(.+?|) (anonfiles|transfer|filebin|anonymousfiles|megaupload|bayfiles|letsupload|0x0)",
)
async def webupload(event):
    await event.edit("**Processing...**")
    input_str = event.pattern_match.group(1)
    selected_transfer = event.pattern_match.group(2)
    if input_str:
        file_name = input_str
    else:
        reply = await event.get_reply_message()
        file_name = await event.client.download_media(
            reply.media, TEMP_DOWNLOAD_DIRECTORY
        )

    CMD_WEB = {
        "anonfiles": 'curl -F "file=@{full_file_path}" https://anonfiles.com/api/upload',
        "transfer": 'curl --upload-file "{full_file_path}" https://transfer.sh/{bare_local_name}',
        "filebin": 'curl -X POST --data-binary "@{full_file_path}" -H "filename: {bare_local_name}" "https://filebin.net"',
        "anonymousfiles": 'curl -F file="@{full_file_path}" https://api.anonymousfiles.io/',
        "megaupload": 'curl -F "file=@{full_file_path}" https://megaupload.is/api/upload',
        "bayfiles": 'curl -F "file=@{full_file_path}" https://bayfiles.com/api/upload',
        "letsupload": 'curl -F "file=@{full_file_path}" https://api.letsupload.cc/upload',
        "0x0": 'curl -F "file=@{full_file_path}" https://0x0.st',
    }
    filename = os.path.basename(file_name)
    try:
        selected_one = CMD_WEB[selected_transfer].format(
            full_file_path=file_name, bare_local_name=filename
        )
    except KeyError:
        await event.edit("**Invalid selction.**")
        return
    cmd = selected_one
    # start the subprocess $SHELL
    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    stderr.decode().strip()
    t_response = stdout.decode().strip()
    if t_response:
        try:
            t_response = json.dumps(json.loads(t_response), sort_keys=True, indent=4)
        except Exception:
            pass  # some sites don't return valid JSONs
        # assuming, the return values won't be longer than 4096 characters
        await event.edit(t_response)


CMD_HELP.update(
    {
        "webupload": ">`.web` <server>"
        "\nServer List: anonfiles|transfer|filebin|anonymousfiles|megaupload|bayfiles|lestupload|0x0"
        "\nUsage: Reply to a file to upload it to one of the above servers."
    }
)
