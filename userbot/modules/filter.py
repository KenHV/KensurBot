# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.b (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module for filter commands """

from asyncio import sleep
from re import fullmatch, IGNORECASE

from userbot import BOTLOG, BOTLOG_CHATID, CMD_HELP
from userbot.events import register


@register(incoming=True, disable_edited=True)
async def filter_incoming_handler(handler):
    """ Checks if the incoming message contains handler of a filter """
    try:
        if not (await handler.get_sender()).bot:
            try:
                from userbot.modules.sql_helper.filter_sql import get_filters
            except AttributeError:
                await handler.edit("`Running on Non-SQL mode!`")
                return
            listes = handler.text.split(" ")
            filters = get_filters(handler.chat_id)
            if not filters:
                return
            for trigger in filters:
                for item in listes:
                    pro = fullmatch(trigger.keyword, item, flags=IGNORECASE)
                    if pro:
                        await handler.reply(trigger.reply)
                        return
    except AttributeError:
        pass


@register(outgoing=True, pattern="^.filter\\s.*")
async def add_new_filter(new_handler):
    """ For .filter command, allows adding new filters in a chat """
    if not new_handler.text[0].isalpha() and new_handler.text[0] not in ("/", "#", "@", "!"):
        try:
            from userbot.modules.sql_helper.filter_sql import add_filter
        except AttributeError:
            await new_handler.edit("`Running on Non-SQL mode!`")
            return
        message = new_handler.text
        keyword = message.split()
        string = ""
        for i in range(2, len(keyword)):
            string = string + " " + str(keyword[i])

        if event.reply_to_msg_id:
            string = " " + (await event.get_reply_message()).text

        msg = "`Filter` **{}** `{} successfully`"

        if add_filter(str(new_handler.chat_id), keyword[1], string[1:]) is True:
            await new_handler.edit(msg.format(keyword[1], 'added'))
        else:
            await new_handler.edit(msg.format(keyword[1], 'updated'))


@register(outgoing=True, pattern="^.stop\\s.*")
async def remove_a_filter(r_handler):
    """ For .stop command, allows you to remove a filter from a chat. """
    if not r_handler.text[0].isalpha() and r_handler.text[0] not in ("/", "#", "@", "!"):
        try:
            from userbot.modules.sql_helper.filter_sql import remove_filter
        except AttributeError:
            await r_handler.edit("`Running on Non-SQL mode!`")
            return
        message = r_handler.text
        kek = message.split(" ")
        remove_filter(r_handler.chat_id, kek[1])
        await r_handler.edit("```Filter removed successfully```")



@register(outgoing=True, pattern="^.rmfilters (.*)")
async def kick_marie_filter(kick):
    """ For .rmfilters command, allows you to kick all \
        Marie(or her clones) filters from a chat. """
    if not kick.text[0].isalpha() and kick.text[0] not in ("/", "#", "@", "!"):
        bot_type = kick.pattern_match.group(1)
        if bot_type not in ["marie", "rose"]:
            await kick.edit("`That bot is not yet supported!`")
            return
        await kick.edit("```Will be kicking away all Filters!```")
        await sleep(3)
        resp = await kick.get_reply_message()
        filters = resp.text.split("-")[1:]
        for i in filters:
            if bot_type == "marie":
                await kick.reply("/stop %s" % (i.strip()))
            if bot_type == "rose":
                i = i.replace('`', '')
                await kick.reply("/stop %s" % (i.strip()))
            await sleep(0.3)
        await kick.respond(
            "```Successfully purged bots filters yaay!```\n Gimme cookies!"
        )
        if BOTLOG:
            await kick.client.send_message(
                BOTLOG_CHATID, "I cleaned all filters at " +
                               str(kick.chat_id)
            )


@register(outgoing=True, pattern="^.filters$")
async def filters_active(event):
    """ For .filters command, lists all of the active filters in a chat. """
    if not event.text[0].isalpha() and event.text[0] not in ("/", "#", "@", "!"):
        try:
            from userbot.modules.sql_helper.filter_sql import get_filters
        except AttributeError:
            await event.edit("`Running on Non-SQL mode!`")
            return
        transact = "`There are no filters in this chat.`"
        filters = get_filters(event.chat_id)
        for filt in filters:
            if transact == "`There are no filters in this chat.`":
                transact = "Active filters in this chat:\n"
                transact += "🔹 **{}** - `{}`\n".format(filt["keyword"],
                                                       filt["msg"])
            else:
                transact += "🔹 **{}** - `{}`\n".format(filt["keyword"],
                                                       filt["msg"])

        await event.edit(transact)


CMD_HELP.update({
    "filters": "\
.filters\
\nUsage: List all active filters in this chat.\
\n\n.filter <keyword> <reply message>\
\nUsage: Add a filter to this chat. \
The bot will now reply that message whenever 'keyword' is mentioned. \
If you reply to sticker with keyword, bot will reply with that sticker.\
\nNOTE: all filter keywords are in lowercase.\
\n\n.stop <filter>\
\nUsage: Stops that filter.\
"
})
