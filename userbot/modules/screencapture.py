# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
# The entire source code is OSSRPL except 'screencapture' which is MPL
# License: MPL and OSSRPL

import io
import traceback
from selenium import webdriver
from asyncio import sleep
from selenium.webdriver.chrome.options import Options
from userbot.events import register, errors_handler
from userbot import GOOGLE_CHROME_BIN, CHROME_DRIVER, CMD_HELP


@register(pattern=r".screencapture (.*)", outgoing=True)
@errors_handler
async def capture(url):
    """ For .screencapture command, capture a website and send the photo. """
    if not url.text[0].isalpha() and url.text[0] not in ("/", "#", "@", "!"):
        if url.fwd_from:
            return
        await url.edit("Processing ...")
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--test-type")
            chrome_options.binary_location = GOOGLE_CHROME_BIN
            chrome_options.add_argument('--ignore-certificate-errors')
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument('--disable-gpu')
            driver = webdriver.Chrome(
                executable_path=CHROME_DRIVER,
                options=chrome_options)
            input_str = url.pattern_match.group(1)
            driver.get(input_str)
            height = driver.execute_script(
                "return Math.max(document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);")
            width = driver.execute_script(
                "return Math.max(document.body.scrollWidth, document.body.offsetWidth, document.documentElement.clientWidth, document.documentElement.scrollWidth, document.documentElement.offsetWidth);")
            driver.set_window_size(width + 125, height + 125)
            await url.edit("`Generating screenshot of the page...`")
            await sleep(5)
            im_png = driver.get_screenshot_as_png()
            # saves screenshot of entire page
            driver.close()
            message_id = url.message.id
            if url.reply_to_msg_id:
                message_id = url.reply_to_msg_id
            with io.BytesIO(im_png) as out_file:
                out_file.name = "screencapture.png"
                await url.edit("`Uploading screenshot as file..`")
                await url.client.send_file(
                    url.chat_id,
                    out_file,
                    caption=input_str,
                    force_document=True,
                    reply_to=message_id
                )

        except Exception:
            await url.edit(traceback.format_exc())

CMD_HELP.update({
    "screencapture": ".screencapture <url>\
    \nUsage: Takes a screenshot of a website and sends the screenshot."
})
