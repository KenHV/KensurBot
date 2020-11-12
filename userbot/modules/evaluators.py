# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module for executing code and terminal commands from Telegram. """

import asyncio
from os import remove
from sys import executable

from userbot import BOTLOG, BOTLOG_CHATID, CMD_HELP, TERM_ALIAS
from userbot.events import register


@register(outgoing=True, pattern=r"^\.eval(?: |$|\n)(.*)")
async def evaluate(query):
    """ For .eval command, evaluates the given Python expression. """
    if query.is_channel and not query.is_group:
        return await query.edit("`Eval isn't permitted on channels`")

    if query.pattern_match.group(1):
        expression = query.pattern_match.group(1)
    else:
        return await query.edit("``` Give an expression to evaluate. ```")

    if expression in ("userbot.session", "config.env"):
        return await query.edit("`That's a dangerous operation! Not Permitted!`")

    try:
        evaluation = str(eval(expression))
        if evaluation:
            if isinstance(evaluation, str):
                if len(evaluation) >= 4096:
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

    if BOTLOG:
        await query.client.send_message(
            BOTLOG_CHATID, f"Eval query {expression} was executed successfully."
        )


@register(outgoing=True, pattern=r"^\.exec(?: |$|\n)([\s\S]*)")
async def run(run_q):
    """ For .exec command, which executes the dynamically created program """
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
            clines[0] +
            "\n" +
            clines[1] +
            "\n" +
            clines[2] +
            "\n" +
            clines[3] +
            "...")

    command = "".join(f"\n {l}" for l in code.split("\n.strip()"))
    process = await asyncio.create_subprocess_exec(
        executable,
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

    if BOTLOG:
        await run_q.client.send_message(
            BOTLOG_CHATID, "Exec query " + codepre + " was executed successfully."
        )


@register(outgoing=True, pattern=r"^\.term(?: |$|\n)(.*)")
async def terminal_runner(term):
    """ For .term command, runs bash commands and scripts on your server. """
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

    if command in ("userbot.session", "config.env", "env", "$", "$*", "echo"):
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

    if BOTLOG:
        await term.client.send_message(
            BOTLOG_CHATID, "Terminal command " + command + " was executed sucessfully.",
        )


CMD_HELP.update({"eval": ">`.eval 2 + 3`"
                 "\nUsage: Evalute mini-expressions.",
                 "exec": ">`.exec print('hello')`"
                 "\nUsage: Execute small python scripts.",
                 "term": ">`.term <cmd>`"
                 "\nUsage: Run bash commands and scripts on your server.",
                 })
