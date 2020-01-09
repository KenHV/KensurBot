# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#

# Original source for the deepfrying code (used under the following license): https://github.com/Ovyerus/deeppyer

# MIT License
#
# Copyright (c) 2017 Ovyerus
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
""" Userbot module for frying stuff. ported by @NeoMatrix90 """

import io
import math
import pkgutil
import cv2
import numpy

from io import BytesIO
from typing import Tuple

from userbot import bot, CMD_HELP
from userbot.events import register

from PIL import Image, ImageEnhance, ImageOps
from telethon.tl.types import DocumentAttributeFilename

from telethon import events


@register(pattern="^.deepfry(?: |$)(.*)", outgoing=True) 
async def deepfryer(event):
    try:
        frycount = int(event.pattern_match.group(1))
        if frycount < 1:
            raise ValueError
    except ValueError:
        frycount = 1

    if event.is_reply:
        reply_message = await event.get_reply_message()
        data = await check_media(reply_message)

        if isinstance(data, bool):
            await event.edit("`I can't deep fry that!`")
            return
    else:
        await event.edit("`Reply to an image or sticker to deep fry it!`")
        return

    # download last photo (highres) as byte array
    await event.edit("`Downloading media…`")
    image = io.BytesIO()
    await event.client.download_media(data, image)
    image = Image.open(image)

    # fry the image
    await event.edit("`Deep frying media…`")
    for _ in range(frycount):
        image = await deepfry(image)

    fried_io = io.BytesIO()
    fried_io.name = "image.jpeg"
    image.save(fried_io, "JPEG")
    fried_io.seek(0)

    await event.reply(file=fried_io)

__all__ = ('Colour', 'ColourTuple', 'DefaultColours', 'deepfry')

Colour = Tuple[int, int, int]
ColourTuple = Tuple[Colour, Colour]


class DefaultColours:
    """Default colours provided for deepfrying"""
    red = ((254, 0, 2), (255, 255, 15))
    blue = ((36, 113, 229), (255,) * 3)


face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
flare_img = Image.open(BytesIO(pkgutil.get_data(__package__, 'flare.png')))

FlarePosition = namedtuple('FlarePosition', ['x', 'y', 'size'])


async def deepfry(img: Image, *, colours: ColourTuple = DefaultColours.red, flares: bool = True) -> Image:
    """
    Deepfry a given image.
    Parameters
    ----------
    img : `Image`
        Image to manipulate.
    colours : `ColourTuple`, optional
        A tuple of the colours to apply on the image.
    flares : `bool`, optional
        Whether or not to try and detect faces for applying lens flares.
    Returns
    -------
    `Image`
        Deepfried image.
    """
    img = img.copy().convert('RGB')
    flare_positions = []

    if flares:
        opencv_img = cv2.cvtColor(numpy.array(img), cv2.COLOR_RGB2GRAY)

        faces = face_cascade.detectMultiScale(
            opencv_img,
            scaleFactor=1.3,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        for (x, y, w, h) in faces:
            face_roi = opencv_img[y:y+h, x:x+w]  # Get region of interest (detected face)

            eyes = eye_cascade.detectMultiScale(face_roi)

            for (ex, ey, ew, eh) in eyes:
                eye_corner = (ex + ew / 2, ey + eh / 2)
                flare_size = eh if eh > ew else ew
                flare_size *= 4
                corners = [math.floor(x) for x in eye_corner]
                eye_corner = FlarePosition(*corners, flare_size)

                flare_positions.append(eye_corner)

    # Crush image to hell and back
    img = img.convert('RGB')
    width, height = img.width, img.height
    img = img.resize((int(width ** .75), int(height ** .75)), resample=Image.LANCZOS)
    img = img.resize((int(width ** .88), int(height ** .88)), resample=Image.BILINEAR)
    img = img.resize((int(width ** .9), int(height ** .9)), resample=Image.BICUBIC)
    img = img.resize((width, height), resample=Image.BICUBIC)
    img = ImageOps.posterize(img, 4)

    # Generate colour overlay
    r = img.split()[0]
    r = ImageEnhance.Contrast(r).enhance(2.0)
    r = ImageEnhance.Brightness(r).enhance(1.5)

    r = ImageOps.colorize(r, colours[0], colours[1])

    # Overlay red and yellow onto main image and sharpen the hell out of it
    img = Image.blend(img, r, 0.75)
    img = ImageEnhance.Sharpness(img).enhance(100.0)

    # Apply flares on any detected eyes
    for flare in flare_positions:
        flare_transformed = flare_img.copy().resize((flare.size,) * 2, resample=Image.BILINEAR)
        img.paste(flare_transformed, (flare.x, flare.y), flare_transformed)

    return img

async def check_media(reply_message):
    if reply_message and reply_message.media:
        if reply_message.photo:
            data = reply_message.photo
        elif reply_message.document:
            if DocumentAttributeFilename(file_name='AnimatedSticker.tgs') in reply_message.media.document.attributes:
                return False
            if reply_message.gif or reply_message.video or reply_message.audio or reply_message.voice:
                return False
            data = reply_message.media.document
        else:
            return False
    else:
        return False

    if not data or data is None:
        return False
    else:
        return data

CMD_HELP.update({
    "deepfry":
    ".deepfry [number]\
    \n Usage: Reply to an image or sticker to deepfry with value, more value more krispy."
})
