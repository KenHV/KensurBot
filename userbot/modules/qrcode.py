# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
# The entire source code is OSSRPL except 'makeqr and getqr' which is MPL
# License: MPL and OSSRPL
""" Userbot module containing commands related to QR Codes. """

import asyncio
import os

import barcode
import qrcode
from barcode.writer import ImageWriter
from bs4 import BeautifulSoup

from userbot import CMD_HELP, LOGS
from userbot.events import register


@register(pattern=r"^\.decode$", outgoing=True)
async def parseqr(qr_e):
    """ For .decode command, get QR Code/BarCode content from the replied photo. """
    downloaded_file_name = await qr_e.client.download_media(
        await qr_e.get_reply_message())
    # parse the Official ZXing webpage to decode the QRCode
    command_to_exec = [
        "curl",
        "-X",
        "POST",
        "-F",
        "f=@" + downloaded_file_name + "",
        "https://zxing.org/w/decode",
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
        LOGS.info(e_response)
        LOGS.info(t_response)
        return await qr_e.edit("**Failed to decode.**")
    soup = BeautifulSoup(t_response, "html.parser")
    qr_contents = soup.find_all("pre")[0].text
    await qr_e.edit(qr_contents)


@register(pattern=r"\.barcode(?: |$)([\s\S]*)", outgoing=True)
async def bq(event):
    """ For .barcode command, genrate a barcode containing the given content. """
    await event.edit("**Processing...**")
    input_str = event.pattern_match.group(1)
    message = "**Syntax:** `.barcode <long text to include>`"
    reply_msg_id = event.message.id
    if input_str:
        message = input_str
    elif event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        reply_msg_id = previous_message.id
        if previous_message.media:
            downloaded_file_name = await event.client.download_media(
                previous_message)
            m_list = None
            with open(downloaded_file_name, "rb") as fd:
                m_list = fd.readlines()
            message = ""
            for m in m_list:
                message += m.decode("UTF-8") + "\r\n"
            os.remove(downloaded_file_name)
        else:
            message = previous_message.message
    else:
        return event.edit("**Syntax:** `.barcode <long text to include>`")

    bar_code_type = "code128"
    try:
        bar_code_mode_f = barcode.get(bar_code_type,
                                      message,
                                      writer=ImageWriter())
        filename = bar_code_mode_f.save(bar_code_type)
        await event.client.send_file(event.chat_id,
                                     filename,
                                     reply_to=reply_msg_id)
        os.remove(filename)
    except Exception as e:
        return await event.edit(str(e))
    await event.delete()


@register(pattern=r"\.makeqr(?: |$)([\s\S]*)", outgoing=True)
async def make_qr(makeqr):
    """ For .makeqr command, make a QR Code containing the given content. """
    input_str = makeqr.pattern_match.group(1)
    message = "**Syntax:** `.makeqr <long text to include>`"
    reply_msg_id = None
    if input_str:
        message = input_str
    elif makeqr.reply_to_msg_id:
        previous_message = await makeqr.get_reply_message()
        reply_msg_id = previous_message.id
        if previous_message.media:
            downloaded_file_name = await makeqr.client.download_media(
                previous_message)
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
    await makeqr.client.send_file(makeqr.chat_id,
                                  "img_file.webp",
                                  reply_to=reply_msg_id)
    os.remove("img_file.webp")
    await makeqr.delete()


CMD_HELP.update({
    "qr":
    ">`.makeqr <content>`"
    "\nUsage: Make a QR Code from the given content."
    "\nExample: .makeqr www.google.com"
    "\nNote: use `.decode <reply to barcode/qrcode>` to get decoded content.",
    "barcode":
    ">`.barcode <content>`"
    "\nUsage: Make a BarCode from the given content."
    "\nExample: .barcode www.google.com"
    "\nNote: use `.decode <reply to barcode/qrcode>` to get decoded content.",
})
