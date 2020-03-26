# Copyright (C) 2020 Adek Maulana.
# All rights reserved.
"""
   Heroku manager for your userbot
"""

import heroku3
import asyncio
import os

from asyncio import create_subprocess_shell as asyncSubprocess
from asyncio.subprocess import PIPE as asyncPIPE

from userbot import CMD_HELP, LOGS, HEROKU_APP_NAME, HEROKU_API_KEY
from userbot.events import register
from userbot.prettyjson import prettyjson

Heroku = heroku3.from_key(HEROKU_API_KEY)


async def subprocess_run(cmd, heroku):
    subproc = await asyncSubprocess(cmd, stdout=asyncPIPE, stderr=asyncPIPE)
    stdout, stderr = await subproc.communicate()
    exitCode = subproc.returncode
    if exitCode != 0:
        await heroku.edit(
            '**An error was detected while running subprocess**\n'
            f'```exitCode: {exitCode}\n'
            f'stdout: {stdout.decode().strip()}\n'
            f'stderr: {stderr.decode().strip()}```')
        return exitCode
    return stdout.decode().strip(), stderr.decode().strip(), exitCode


@register(outgoing=True, pattern=r"^.(set|get|del) var(?: |$)(.*)(?: |$)")
async def variable(var):
    if HEROKU_APP_NAME is not None:
        app = Heroku.app(HEROKU_APP_NAME)
    else:
        await var.edit("`[HEROKU]:\nPlease setup your` **HEROKU_APP_NAME**")
        return
    exe = var.pattern_match.group(1)
    heroku_var = app.config()
    if exe == "get":
        await var.edit("`Getting information...`")
        configs = prettyjson(heroku_var.to_dict(), indent=2)
        with open("configs.json", "w") as fp:
            fp.write(configs)
        with open("configs.json", "r") as fp:
            result = fp.read()
            if len(result) >= 4096:
                await var.client.send_file(
                    var.chat_id,
                    "configs.json",
                    reply_to=var.id,
                    caption="`Output too large, sending it as a file`",
                )
            else:
                await var.edit("`[HEROKU]` variables:\n\n"
                               "================================"
                               f"\n```{result}```\n"
                               "================================"
                               )
        os.remove("configs.json")
        return
    elif exe == "set":
        await var.edit("`Setting information...`")
        val = var.pattern_match.group(2).split()
        await asyncio.sleep(3)
        if val[0] in heroku_var:
            await var.edit(f"**{val[0]}**  `successfully changed to`  **{val[1]}**")
        else:
            await var.edit(f"**{val[0]}**  `successfully added with value: **{val[1]}**")
        heroku_var[val[0]] = val[1]
        return
    elif exe == "del":
        await var.edit("`Getting information to deleting vars...`")
        val = var.pattern_match.group(2).split()[0]
        if val in heroku_var:
            await var.edit(f"**{val}**  `successfully deleted`")
            del heroku_var[val]
        else:
            await var.edit(f"**{val}**  `is not exists`")
        return


@register(outgoing=True, pattern=r"^.heroku(?: |$)")
async def heroku_manager(heroku):
    await heroku.edit("`Processing...`")
    await asyncio.sleep(3)
    result = await subprocess_run(f'heroku ps -a {HEROKU_APP_NAME}', heroku)
    if result[2] != 0:
        return
    hours_remaining = result[0]
    await heroku.edit('`' + hours_remaining + '`')
    return


CMD_HELP.update({
    "heroku":
    ".heroku"
    "\nUsage: Check your heroku dyno hours remaining",
    "variable":
    ".set var <NEW VAR> <VALUE>"
    "\nUsage: add new variable or update existing value variable"
    "\n\n.get var"
    "\nUsage: get your existing varibles"
    "\n\n.del var <VAR>"
    "\nUsage: delete existing variable"
})
