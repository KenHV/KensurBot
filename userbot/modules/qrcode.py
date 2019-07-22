# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.b (the "License");
# you may not use this file except in compliance with the License.
#
# The entire source code is OSSRPL except 'makeqr and getqr' which is MPL
# License: MPL and OSSRPL

""" Userbot module containing commands related to QR Codes. """

import os
import asyncio
from datetime import datetime

import qrcode
from bs4 import BeautifulSoup

from userbot import CMD_HELP
from userbot.events import register


@register(pattern=r"^.getqr$", outgoing=True)
async def parseqr(qr_e):
    """ For .getqr command, get QR Code content from the replied photo. """
    if not qr_e.text[0].isalpha() and qr_e.text[0] not in ("/", "#", "@", "!"):
        if qr_e.fwd_from:
            return
        start = datetime.now()
        downloaded_file_name = await qr_e.client.download_media(
            await qr_e.get_reply_message()
        )
        # parse the Official ZXing webpage to decode the QRCode
        command_to_exec = [
            "curl",
            "-X", "POST",
            "-F", "f=@" + downloaded_file_name + "",
            "https://zxing.org/w/decode"
        ]
        process = await asyncio.create_subprocess_exec(
            *command_to_exec,
            # stdout must a pipe to be accessible as process.stdout
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        # Wait for the subprocess to finish
        stdout, stderr = await process.communicate()
        e_response = stderr.decode().strip()
        t_response = stdout.decode().strip()
        os.remove(downloaded_file_name)
        if not t_response:
            logger.info(e_response)
            logger.info(t_response)
            await qr_e.edit("@oo0pps .. something wrongings. Failed to decode QRCode")
            return
        soup = BeautifulSoup(t_response, "html.parser")
        qr_contents = soup.find_all("pre")[0].text
        end = datetime.now()
        duration = (end - start).seconds
        await qr_e.edit(
            "Obtained QRCode contents in {} seconds.\n{}".format(duration, qr_contents)
        )
        await asyncio.sleep(5)
        await qr_e.edit(qr_contents)


@register(pattern=r".makeqr(?: |$)([\s\S]*)", outgoing=True)
async def make_qr(makeqr):
    """ For .makeqr command, make a QR Code containing the given content. """
    if not makeqr.text[0].isalpha() and makeqr.text[0] not in (
            "/", "#", "@", "!"):
        if makeqr.fwd_from:
            return
        start = datetime.now()
        input_str = makeqr.pattern_match.group(1)
        message = "SYNTAX: `.makeqr <long text to include>`"
        reply_msg_id = None
        if input_str:
            message = input_str
        elif makeqr.reply_to_msg_id:
            previous_message = await makeqr.get_reply_message()
            reply_msg_id = previous_message.id
            if previous_message.media:
                downloaded_file_name = await makeqr.client.download_media(
                    previous_message
                )
                m_list = None
                with open(downloaded_file_name, "rb") as file:
                    m_list = file.readlines()
                message = ""
                for media in m_list:
                    message += media.decode("UTF-8") + "\r\n"
                os.remove(downloaded_file_name)
            else:
                message = previous_message.message

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(message)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save("img_file.webp", "PNG")
        await makeqr.client.send_file(
            makeqr.chat_id,
            "img_file.webp",
            reply_to=reply_msg_id
        )
        os.remove("img_file.webp")
        duration = (datetime.now() - start).seconds
        await makeqr.edit("Created QRCode in {} seconds".format(duration))
        await asyncio.sleep(5)
        await makeqr.delete()


CMD_HELP.update({
    'getqr': ".getqr\
\nUsage: Get the QR Code content from the replied QR Code."
})

CMD_HELP.update({
    'makeqr': ".makeqr <content>)\
\nUsage: Make a QR Code from the given content.\
\nExample: .makeqr www.google.com"
})
