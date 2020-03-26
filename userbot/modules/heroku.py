# Copyright (C) 2020 Adek Maulana.
# All rights reserved.
"""
   Heroku manager for your userbot
"""

import os
import heroku3
import asyncio

from asyncio import create_subprocess_shell as asyncSubprocess
from asyncio.subprocess import PIPE as asyncPIPE

from userbot import CMD_HELP, LOGS, HEROKU_APP_NAME, HEROKU_API_KEY
from userbot.events import register

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


@register(outgoing=True, pattern=r"^.(set|get) var(?: |$)(.*)(?: |$)")
async def variable(var):
    if HEROKU_APP_NAME is not None:
        app = Heroku.app(HEROKU_APP_NAME)
    else:
        var.edit("`[HEROKU]:\nPlease setup your` **HEROKU_APP_NAME**")
    exe = var.pattern_match.group(1)
    heroku_var = app.config()
    if exe == "get":
        await var.edit("`Getting information...`")
        with open('configs.txt', 'w+') as variables:
            for config, value in heroku_var:
                variables.write(f"{config}: {value}" + "\n")
        result = open('configs.txt').read()
        if len(result) >= 4096:
            await var.client.send_file(
                var.chat_id,
                "configs.txt",
                reply_to=var.id,
                caption="`Output configs is too large, sending it as file...`",
            )
        else:
            var.edit("`[HEROKU]`:\n"
                     "================================"
                     f"    **{HEROKU_APP_NAME}**  configs are:"
                     "================================"
                     f"\n\n```{result}```"
                     )
        result.close()
        os.remove('configs.txt')
        return
    else:
        await var.edit("`Setting information...`")
        val = var.pattern_match.group(2).split()
        heroku_var[val[0]] = val[1]
        await asyncio.sleep(3)
        if val[0] in heroku_var:
            await var.edit(f"**{val[0]}**  `successfully changed to`  **{val[1]}**")
        else:
            await var.edit(f"**{val[0]}**  `successfully added with value: **{val[1]}**")
        return


@register(outgoing=True, pattern=r"^.heroku(?: |$)")
async def heroku_manager(heroku):
    await heroku.edit("`Processing...`")
    await asyncio.sleep(3)
    conf = heroku.pattern_match.group(1)
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
})
