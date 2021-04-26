# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
""" Userbot module containing commands for keeping global notes. """

from sqlalchemy.orm.exc import UnmappedInstanceError

from userbot import BOTLOG_CHATID, CMD_HELP
from userbot.events import register


@register(outgoing=True, pattern=r"^\$\w*", ignore_unsafe=True, disable_errors=True)
async def on_snip(event):
    """Snips logic."""
    try:
        from userbot.modules.sql_helper.snips_sql import get_snip
    except AttributeError:
        return
    name = event.text[1:]
    snip = get_snip(name)
    message_id_to_reply = event.message.reply_to_msg_id
    if not message_id_to_reply:
        message_id_to_reply = None
    if snip:
        if snip.f_mesg_id:
            msg_o = await event.client.get_messages(
                entity=BOTLOG_CHATID, ids=int(snip.f_mesg_id)
            )
            await event.client.send_message(
                event.chat_id,
                msg_o.message,
                reply_to=message_id_to_reply,
                file=msg_o.media,
            )
            await event.delete()
        elif snip.reply:
            await event.client.send_message(
                event.chat_id, snip.reply, reply_to=message_id_to_reply
            )
            await event.delete()


@register(outgoing=True, pattern=r"^\.snip (\w*)")
async def on_snip_save(event):
    """For .snip command, saves snips for future use."""
    try:
        from userbot.modules.sql_helper.snips_sql import add_snip
    except AttributeError:
        return await event.edit("**Running on Non-SQL mode!**")
    keyword = event.pattern_match.group(1)
    string = event.text.partition(keyword)[2]
    msg = await event.get_reply_message()
    msg_id = None
    if msg and msg.media and not string:
        if BOTLOG_CHATID:
            await event.client.send_message(
                BOTLOG_CHATID,
                f"#SNIP\nKEYWORD: {keyword}"
                "\n\nThe following message is saved as the data for the snip, "
                "please do NOT delete it!",
            )
            msg_o = await event.client.forward_messages(
                entity=BOTLOG_CHATID, messages=msg, from_peer=event.chat_id, silent=True
            )
            msg_id = msg_o.id
        else:
            return await event.edit(
                "**Saving snips with media requires the BOTLOG_CHATID to be set.**"
            )
    elif event.reply_to_msg_id and not string:
        rep_msg = await event.get_reply_message()
        string = rep_msg.text
    success = "**Snip {} successfully. Use** `${}` **anywhere to get it**"
    try:
        if add_snip(keyword, string, msg_id) is False:
            await event.edit(success.format("updated", keyword))
        else:
            await event.edit(success.format("saved", keyword))
    except UnmappedInstanceError:
        return await event.edit(f"**Error: Snip** `{keyword}` **already exists.**")


@register(outgoing=True, pattern=r"^\.snips$")
async def on_snip_list(event):
    """For .snips command, lists snips saved by you."""
    try:
        from userbot.modules.sql_helper.snips_sql import get_snips
    except AttributeError:
        return await event.edit("**Running on Non-SQL mode!**")

    message = "**No snips available right now.**"
    all_snips = get_snips()
    for a_snip in all_snips:
        if message == "**No snips available right now.**":
            message = "**Available snips:**\n\n"
        message += f"`${a_snip.snip}`\n"
    await event.edit(message)


@register(outgoing=True, pattern=r"^\.remsnip (\w*)")
async def on_snip_delete(event):
    """For .remsnip command, deletes a snip."""
    try:
        from userbot.modules.sql_helper.snips_sql import remove_snip
    except AttributeError:
        return await event.edit("**Running on Non-SQL mode!**")
    name = event.pattern_match.group(1)
    if remove_snip(name) is True:
        await event.edit(f"**Successfully deleted snip:** `{name}`")
    else:
        await event.edit(f"**Couldn't find snip:** `{name}`")


CMD_HELP.update(
    {
        "snips": ">`$<snip_name>`"
        "\nUsage: Gets the specified snip, anywhere."
        "\n\n>`.snip <name> <data> or reply to a message with .snip <name>`"
        "\nUsage: Saves the message as a snip (global note) with the name."
        " (Works with pics, docs, and stickers too!)"
        "\n\n>`.snips`"
        "\nUsage: Gets all saved snips."
        "\n\n>`.remsnip <snip_name>`"
        "\nUsage: Deletes the specified snip."
    }
)
