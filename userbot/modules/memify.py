# Ported from Userge and refactored by @KenHV
# Copyright (C) UsergeTeam 2020
# Licensed under GPLv3

import asyncio
import os
import shlex
import textwrap
from typing import Optional, Tuple

from PIL import Image, ImageDraw, ImageFont
from userbot import CMD_HELP, LOGS, TEMP_DOWNLOAD_DIRECTORY
from userbot.events import register


@register(outgoing=True, pattern=r"^\.mmf (.*)")
async def memify(event):
    reply_msg = await event.get_reply_message()
    input_str = event.pattern_match.group(1)
    await event.edit("**Processing...**")

    if not reply_msg:
        return await event.edit("**Reply to a message containing media!**")

    if not reply_msg.media:
        return await event.edit("**Reply to an image/sticker/gif/video!**")

    if not os.path.isdir(TEMP_DOWNLOAD_DIRECTORY):
        os.makedirs(TEMP_DOWNLOAD_DIRECTORY)

    dls = await event.client.download_media(reply_msg, TEMP_DOWNLOAD_DIRECTORY)
    dls_path = os.path.join(TEMP_DOWNLOAD_DIRECTORY, os.path.basename(dls))

    if dls_path.endswith(".tgs"):
        await event.edit("**Extracting first frame..**")
        png_file = os.path.join(TEMP_DOWNLOAD_DIRECTORY, "meme.png")
        cmd = f"lottie_convert.py --frame 0 -if lottie -of png {dls_path} {png_file}"
        stdout, stderr = (await runcmd(cmd))[:2]
        os.remove(dls_path)
        if not os.path.lexists(png_file):
            return await event.edit("**Couldn't parse this image.**")
        dls_path = png_file

    elif dls_path.endswith(".mp4"):
        await event.edit("**Extracting first frame..**")
        jpg_file = os.path.join(TEMP_DOWNLOAD_DIRECTORY, "meme.jpg")
        await take_screen_shot(dls_path, 0, jpg_file)
        os.remove(dls_path)
        if not os.path.lexists(jpg_file):
            return await event.edit("**Couldn't parse this video.**")
        dls_path = jpg_file

    await event.edit("**Adding text...**")
    webp_file = await draw_meme_text(dls_path, input_str)
    await event.client.send_file(entity=event.chat.id,
                                 file=webp_file,
                                 force_document=False,
                                 reply_to=reply_msg)
    await event.delete()
    os.remove(webp_file)


async def draw_meme_text(image_path, text):
    img = Image.open(image_path).convert("RGB")
    os.remove(image_path)
    i_width, i_height = img.size
    m_font = ImageFont.truetype("bin/impact.ttf", int((70 / 640) * i_width))
    if ";" in text:
        upper_text, lower_text = text.split(";")
    else:
        upper_text = text
        lower_text = ''
    draw = ImageDraw.Draw(img)
    current_h, pad = 10, 5

    if upper_text:
        for u_text in textwrap.wrap(upper_text, width=15):
            u_width, u_height = draw.textsize(u_text, font=m_font)

            draw.text(xy=(((i_width - u_width) / 2) - 1,
                          int((current_h / 640) * i_width)),
                      text=u_text,
                      font=m_font,
                      fill=(0, 0, 0))
            draw.text(xy=(((i_width - u_width) / 2) + 1,
                          int((current_h / 640) * i_width)),
                      text=u_text,
                      font=m_font,
                      fill=(0, 0, 0))
            draw.text(xy=((i_width - u_width) / 2,
                          int(((current_h / 640) * i_width)) - 1),
                      text=u_text,
                      font=m_font,
                      fill=(0, 0, 0))
            draw.text(xy=(((i_width - u_width) / 2),
                          int(((current_h / 640) * i_width)) + 1),
                      text=u_text,
                      font=m_font,
                      fill=(0, 0, 0))

            draw.text(xy=((i_width - u_width) / 2,
                          int((current_h / 640) * i_width)),
                      text=u_text,
                      font=m_font,
                      fill=(255, 255, 255))
            current_h += u_height + pad

    if lower_text:
        for l_text in textwrap.wrap(lower_text, width=15):
            u_width, u_height = draw.textsize(l_text, font=m_font)

            draw.text(xy=(((i_width - u_width) / 2) - 1,
                          i_height - u_height - int((20 / 640) * i_width)),
                      text=l_text,
                      font=m_font,
                      fill=(0, 0, 0))
            draw.text(xy=(((i_width - u_width) / 2) + 1,
                          i_height - u_height - int((20 / 640) * i_width)),
                      text=l_text,
                      font=m_font,
                      fill=(0, 0, 0))
            draw.text(xy=((i_width - u_width) / 2, (i_height - u_height - int(
                (20 / 640) * i_width)) - 1),
                      text=l_text,
                      font=m_font,
                      fill=(0, 0, 0))
            draw.text(xy=((i_width - u_width) / 2, (i_height - u_height - int(
                (20 / 640) * i_width)) + 1),
                      text=l_text,
                      font=m_font,
                      fill=(0, 0, 0))

            draw.text(xy=((i_width - u_width) / 2, i_height - u_height - int(
                (20 / 640) * i_width)),
                      text=l_text,
                      font=m_font,
                      fill=(255, 255, 255))
            current_h += u_height + pad

    image_name = "memify.webp"
    webp_file = os.path.join(TEMP_DOWNLOAD_DIRECTORY, image_name)
    img.save(webp_file, "webp")
    return webp_file


async def runcmd(cmd: str) -> Tuple[str, str, int, int]:
    """ run command in terminal """
    args = shlex.split(cmd)
    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()
    return (stdout.decode('utf-8', 'replace').strip(),
            stderr.decode('utf-8',
                          'replace').strip(), process.returncode, process.pid)


async def take_screen_shot(video_file: str,
                           duration: int,
                           path: str = '') -> Optional[str]:
    """ take a screenshot """
    ttl = duration // 2
    thumb_image_path = path or os.path.join(
        TEMP_DOWNLOAD_DIRECTORY, f"{os.path.basename(video_file)}.jpg")
    command = f'''ffmpeg -ss {ttl} -i "{video_file}" -vframes 1 "{thumb_image_path}"'''
    err = (await runcmd(command))[1]
    if err:
        LOGS.info(err)
    return thumb_image_path if os.path.exists(thumb_image_path) else None


CMD_HELP.update({
    "memify":
    ">`.mmf <top text>;<bottom text>`"
    "\nUsage: Reply to an image/sticker/gif/video to add text to it."
    "\nIf it's a video, text will be added to the first frame."
})
