# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
#
"""Userbot module for executing code and terminal commands from Telegram."""

import asyncio
import io
import sys
import traceback
from os import remove

from userbot import CMD_HELP, TERM_ALIAS
from userbot.events import register


@register(outgoing=True, pattern=r"^\.eval(?: |$|\n)([\s\S]*)")
async def evaluate(query):
    """For .eval command, evaluates the given Python expression."""
    if query.is_channel and not query.is_group:
        return await query.edit("`Eval isn't permitted on channels`")

    if query.pattern_match.group(1):
        expression = query.pattern_match.group(1)
    else:
        return await query.edit("``` Give an expression to evaluate. ```")

    if expression in ("userbot.session", "config.env"):
        return await query.edit("`That's a dangerous operation! Not Permitted!`")

    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None

    async def aexec(code, event):
        """ execute command """
        head = "async def __aexec(event):\n "
        code = "".join(f"\n {line}" for line in code.split("\n"))
        exec(head + code)  # pylint: disable=exec-used
        return await locals()["__aexec"](event)

    try:
        returned = await aexec(expression, query)
    except Exception:  # pylint: disable=broad-except
        exc = traceback.format_exc()

    stdout = redirected_output.getvalue().strip()
    stderr = redirected_error.getvalue().strip()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = exc or stderr or stdout or returned

    try:
        if evaluation:
            if len(str(evaluation)) >= 4096:
                with open("output.txt", "w+") as file:
                    file.write(evaluation)
                await query.client.send_file(
                    query.chat_id,
                    "output.txt",
                    reply_to=query.id,
                    caption="`Output too large, sending as file`",
                )
                remove("output.txt")
                return
            await query.edit(
                "**Query: **\n`"
                f"{expression}"
                "`\n**Result: **\n`"
                f"{evaluation}"
                "`"
            )
        else:
            await query.edit(
                "**Query: **\n`"
                f"{expression}"
                "`\n**Result: **\n`No Result Returned/False`"
            )
    except Exception as err:
        await query.edit(
            "**Query: **\n`" f"{expression}" "`\n**Exception: **\n" f"`{err}`"
        )


@register(outgoing=True, pattern=r"^\.exec(?: |$|\n)([\s\S]*)")
async def run(run_q):
    """For .exec command, which executes the dynamically created program"""
    code = run_q.pattern_match.group(1)

    if run_q.is_channel and not run_q.is_group:
        return await run_q.edit("`Exec isn't permitted on channels!`")

    if not code:
        return await run_q.edit(
            "``` At least a variable is required to"
            "execute. Use .help exec for an example.```"
        )

    if code in ("userbot.session", "config.env"):
        return await run_q.edit("`That's a dangerous operation! Not Permitted!`")

    if len(code.splitlines()) <= 5:
        codepre = code
    else:
        clines = code.splitlines()
        codepre = (
            clines[0] + "\n" + clines[1] + "\n" + clines[2] + "\n" + clines[3] + "..."
        )

    command = "".join(f"\n {l}" for l in code.split("\n.strip()"))
    process = await asyncio.create_subprocess_exec(
        sys.executable,
        "-c",
        command.strip(),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    result = str(stdout.decode().strip()) + str(stderr.decode().strip())

    if result:
        if len(result) > 4096:
            with open("output.txt", "w+") as file:
                file.write(result)
            await run_q.client.send_file(
                run_q.chat_id,
                "output.txt",
                reply_to=run_q.id,
                caption="`Output too large, sending as file`",
            )
            remove("output.txt")
            return
        await run_q.edit(
            "**Query: **\n`" f"{codepre}" "`\n**Result: **\n`" f"{result}" "`"
        )
    else:
        await run_q.edit(
            "**Query: **\n`" f"{codepre}" "`\n**Result: **\n`No result returned/False`"
        )


@register(outgoing=True, pattern=r"^\.term(?: |$|\n)(.*)")
async def terminal_runner(term):
    """For .term command, runs bash commands and scripts on your server."""
    curruser = TERM_ALIAS
    command = term.pattern_match.group(1)
    try:
        from os import geteuid

        uid = geteuid()
    except ImportError:
        uid = "This ain't it chief!"

    if term.is_channel and not term.is_group:
        return await term.edit("`Term commands aren't permitted on channels!`")

    if not command:
        return await term.edit(
            "``` Give a command or use .help term for an example.```"
        )

    if command in ("userbot.session", "config.env"):
        return await term.edit("`That's a dangerous operation! Not Permitted!`")

    process = await asyncio.create_subprocess_shell(
        command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    result = str(stdout.decode().strip()) + str(stderr.decode().strip())

    if len(result) > 4096:
        with open("output.txt", "w+") as output:
            output.write(result)
        await term.client.send_file(
            term.chat_id,
            "output.txt",
            reply_to=term.id,
            caption="`Output too large, sending as file`",
        )
        remove("output.txt")
        return

    if uid == 0:
        await term.edit("`" f"{curruser}:~# {command}" f"\n{result}" "`")
    else:
        await term.edit("`" f"{curruser}:~$ {command}" f"\n{result}" "`")


CMD_HELP.update(
    {
        "eval": "`.eval <cmd>`\n`.eval return 2 + 3`\n`.eval print(event)`\n"
        "`.eval await event.reply('hii..')`\n\n"
        "Usage: Evaluate Python expressions in the running script args.",
        "exec": "`.exec print('hello')`\nUsage: Execute small python scripts in subprocess.",
        "term": "`.term <cmd>`\nUsage: Run bash commands and scripts on your server.",
    }
)
