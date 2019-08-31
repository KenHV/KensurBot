# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
""" Userbot module containing userid, chatid and log commands"""

from time import sleep
from userbot import CMD_HELP, BOTLOG, BOTLOG_CHATID, bot
from userbot.events import register, errors_handler
from userbot.modules.admin import get_user_from_event


@register(outgoing=True, pattern="^.userid$")
@errors_handler
async def useridgetter(target):
    """ For .userid command, returns the ID of the target user. """
    message = await target.get_reply_message()
    if message:
        if not message.forward:
            user_id = message.sender.id
            if message.sender.username:
                name = "@" + message.sender.username
            else:
                name = "**" + message.sender.first_name + "**"
        else:
            user_id = message.forward.sender.id
            if message.forward.sender.username:
                name = "@" + message.forward.sender.username
            else:
                name = "*" + message.forward.sender.first_name + "*"
        await target.edit("**Name:** {} \n**User ID:** `{}`".format(
            name, user_id))


@register(outgoing=True, pattern="^.mention(?: |$)(.*)")
@errors_handler
async def permalink(mention):
    """ For .mention command, generates a link to the user's PM with a custom text. """
    user, custom = await get_user_from_event(mention)
    if not user:
        await mention.edit("`User not found.`")
        return
    if custom:
        await mention.edit(f"[{custom}](tg://user?id={user.id})")
    else:
        tag = user.first_name.replace("\u2060",
                                      "") if user.first_name else user.username
        await mention.edit(f"[{tag}](tg://user?id={user.id})")


@register(outgoing=True, pattern="^.chatid$")
@errors_handler
async def chatidgetter(chat):
    """ For .chatid, returns the ID of the chat you are in at that moment. """
    await chat.edit("Chat ID: `" + str(chat.chat_id) + "`")


@register(outgoing=True, pattern=r"^.log(?: |$)([\s\S]*)")
@errors_handler
async def log(log_text):
    """ For .log command, forwards a message or the command argument to the bot logs group """
    if BOTLOG:
        if log_text.reply_to_msg_id:
            reply_msg = await log_text.get_reply_message()
            await reply_msg.forward_to(BOTLOG_CHATID)
        elif log_text.pattern_match.group(1):
            user = f"#LOG / Chat ID: {log_text.chat_id}\n\n"
            textx = user + log_text.pattern_match.group(1)
            await bot.send_message(BOTLOG_CHATID, textx)
        else:
            await log_text.edit("`What am I supposed to log?`")
            return
        await log_text.edit("`Logged Successfully`")
    else:
        await log_text.edit("`This feature requires Logging to be enabled!`")
    sleep(2)
    await log_text.delete()


@register(outgoing=True, pattern="^.kickme$")
@errors_handler
async def kickme(leave):
    """ Basically it's .kickme command """
    await leave.edit("Nope, no, no, I go away")
    await leave.client.kick_participant(leave.chat_id, 'me')


@register(outgoing=True, pattern="^.unmutechat$")
@errors_handler
async def unmute_chat(unm_e):
    """ For .unmutechat command, unmute a muted chat. """
    try:
        from userbot.modules.sql_helper.keep_read_sql import unkread
    except AttributeError:
        await unm_e.edit('`Running on Non-SQL Mode!`')
        return
    unkread(str(unm_e.chat_id))
    await unm_e.edit("```Unmuted this chat Successfully```")
    sleep(2)
    await unm_e.delete()


@register(outgoing=True, pattern="^.mutechat$")
@errors_handler
async def mute_chat(mute_e):
    """ For .mutechat command, mute any chat. """
    try:
        from userbot.modules.sql_helper.keep_read_sql import kread
    except AttributeError:
        await mute_e.edit("`Running on Non-SQL mode!`")
        return
    await mute_e.edit(str(mute_e.chat_id))
    kread(str(mute_e.chat_id))
    await mute_e.edit("`Shush! This chat will be silenced!`")
    sleep(2)
    await mute_e.delete()
    if BOTLOG:
        await mute_e.client.send_message(
            BOTLOG_CHATID,
            str(mute_e.chat_id) + " was silenced.")


@register(incoming=True)
@errors_handler
async def keep_read(message):
    """ The mute logic. """
    try:
        from userbot.modules.sql_helper.keep_read_sql import is_kread
    except AttributeError:
        return
    kread = is_kread()
    if kread:
        for i in kread:
            if i.groupid == str(message.chat_id):
                await message.client.send_read_acknowledge(message.chat_id)


CMD_HELP.update({
    "chat":
    ".chatid\
\nUsage: Fetches the current chat's ID\
\n\n.userid\
\nUsage: Fetches the ID of the user in reply, if its a forwarded message, finds the ID for the source.\
\n\n.log\
\nUsage: Forwards the message you've replied to in your bot logs group.\
\n\n.kickme\
\nUsage: Leave from a targeted group.\
\n\n.unmutechat\
\nUsage: Unmutes a muted chat.\
\n\n.mutechat\
\nUsage: Allows you to mute any chat.\
\n\n.mention <reply/tag> <optional text>\
\nUsage: Generate a permanent link to the user's profile with optional custom text."
})
