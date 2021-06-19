# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module for managing events.
 One of the main components of the userbot. """

from asyncio import create_subprocess_shell as asyncsubshell
from asyncio import subprocess as asyncsub
from os import remove
from sys import exc_info
from time import gmtime, strftime
from traceback import format_exc

from telethon import events

from userbot import BOTLOG_CHATID, LOGS, LOGSPAMMER, bot


def register(**args):
    """Register a new event."""
    pattern = args.get("pattern", None)
    disable_edited = args.get("disable_edited", False)
    ignore_unsafe = args.get("ignore_unsafe", False)
    unsafe_pattern = r"^[^/!#@\$A-Za-z]"
    disable_errors = args.get("disable_errors", False)

    if pattern is not None and not pattern.startswith("(?i)"):
        args["pattern"] = "(?i)" + pattern

    if "disable_edited" in args:
        del args["disable_edited"]

    if "ignore_unsafe" in args:
        del args["ignore_unsafe"]

    if "disable_errors" in args:
        del args["disable_errors"]

    if pattern and not ignore_unsafe:
        args["pattern"] = pattern.replace("^.", unsafe_pattern, 1)

    def decorator(func):
        async def wrapper(check):
            if check.edit_date and check.is_channel and not check.is_group:
                # Messages sent in channels can be edited by other users.
                # Ignore edits that take place in channels.
                return

            try:
                from userbot.modules.sql_helper.blacklist_sql import get_blacklist

                for blacklisted in get_blacklist():
                    if str(check.chat_id) == blacklisted.chat_id:
                        return
            except Exception:
                pass

            if check.via_bot_id and check.out:
                return

            try:
                await func(check)
            # Thanks to @kandnub for this HACK.
            # Raise StopPropagation to Raise StopPropagation
            # This needed for AFK to working properly
            except events.StopPropagation:
                raise events.StopPropagation
            # This is a gay exception and must be passed out. So that it doesnt
            # spam chats
            except KeyboardInterrupt:
                pass
            except BaseException as e:
                # Check if we have to disable error logging.
                if not disable_errors:
                    LOGS.exception(e)  # Log the error in console

                    date = strftime("%Y-%m-%d %H:%M:%S", gmtime())

                    link = "[Support Chat](https://t.me/KensurOT)"
                    text = (
                        "**USERBOT ERROR REPORT**\n"
                        "If you want to, you can report it"
                        f"- just forward this message to {link}.\n"
                        "I won't log anything except the fact of error and date\n"
                    )

                    command = 'git log --pretty=format:"%an: %s" -10'

                    process = await asyncsubshell(
                        command, stdout=asyncsub.PIPE, stderr=asyncsub.PIPE
                    )
                    stdout, stderr = await process.communicate()
                    ftext = (
                        "\nDisclaimer:\nThis file uploaded ONLY here, we "
                        "logged only fact of error and date, we respect your "
                        "privacy, you may not report this error if you've any "
                        "confidential data here, no one will see your data if "
                        "you choose not to do so.\n\n"
                        "--------BEGIN USERBOT TRACEBACK LOG--------"
                        f"\nDate: {date}\nChat ID: {check.chat_id}"
                        f"\nSender ID: {check.sender_id}\n\nEvent Trigger:\n"
                        f"{check.text}\n\nTraceback info:\n{format_exc()}"
                        f"\n\nError text:\n{exc_info()[1]}"
                        "\n\n--------END USERBOT TRACEBACK LOG--------"
                        "\n\n\nLast 10 commits:\n"
                        f"{stdout.decode().strip()}{stderr.decode().strip()}"
                    )

                    with open("error.log", "w+") as file:
                        file.write(ftext)

                    if LOGSPAMMER:
                        await check.client.send_file(
                            BOTLOG_CHATID,
                            "error.log",
                            caption=text,
                        )
                    else:
                        await check.client.send_file(
                            check.chat_id,
                            "error.log",
                            caption=text,
                        )

                    remove("error.log")
            else:
                pass

        if not disable_edited:
            bot.add_event_handler(wrapper, events.MessageEdited(**args))
        bot.add_event_handler(wrapper, events.NewMessage(**args))
        return wrapper

    return decorator
