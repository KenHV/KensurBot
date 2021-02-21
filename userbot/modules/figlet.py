# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
#

import pyfiglet
from emoji import get_emoji_regexp

from userbot import CMD_HELP
from userbot.events import register


@register(outgoing=True, pattern=r"^\.figlet (\w+) (.+)")
async def figlet(event):
    if event.fwd_from:
        return
    style_list = {
        "slant": "slant",
        "3d": "3-d",
        "5line": "5lineoblique",
        "alpha": "alphabet",
        "banner": "banner3-D",
        "doh": "doh",
        "iso": "isometric1",
        "letter": "letters",
        "allig": "alligator",
        "dotm": "dotmatrix",
        "bubble": "bubble",
        "bulb": "bulbhead",
        "digi": "digital",
    }
    style = event.pattern_match.group(1)
    text = event.pattern_match.group(2)
    try:
        font = style_list[style]
    except KeyError:
        return await event.edit(
            "**Invalid style selected, refer to **`.help figlet`**.**"
        )
    result = pyfiglet.figlet_format(deEmojify(text), font=font)
    await event.respond(f"‌‌‎`{result}`")
    await event.delete()


def deEmojify(inputString):
    """ Remove emojis and other non-safe characters from string """
    return get_emoji_regexp().sub("", inputString)


CMD_HELP.update(
    {
        "figlet": ">`.figlet`"
        "\nUsage: Stylizes your text."
        "\n\nExample: `.figlet <style> <your text goes here>`"
        "\nAvailable styles: `slant`, `3d`, `5line`, `alpha`, `banner`, `doh`, `iso`, `letter`, `allig`, `dotm`, `bubble`, `bulb`, `digi`"
    }
)
