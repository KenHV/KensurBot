# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.b (the "License");
# you may not use this file except in compliance with the License.
""" Userbot module containing userid, chatid and log commands"""

from time import sleep

from telethon.tl.functions.channels import LeaveChannelRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import MessageEntityMentionName

from userbot import CMD_HELP, BOTLOG, BOTLOG_CHATID, bot
from userbot.events import register


@register(outgoing=True, pattern="^.userid$")
async def useridgetter(target):
    """ For .userid command, returns the ID of the target user. """
    if not target.text[0].isalpha() and target.text[0] not in ("/", "#", "@", "!"):
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
            await target.edit(
                "**Name:** {} \n**User ID:** `{}`"
                .format(name, user_id)
            )


@register(outgoing=True, pattern="^.chatid$")
async def chatidgetter(chat):
    """ For .chatid, returns the ID of the chat you are in at that moment. """
    if not chat.text[0].isalpha() and chat.text[0] not in ("/", "#", "@", "!"):
        await chat.edit("Chat ID: `" + str(chat.chat_id) + "`")


@register(outgoing=True, pattern="^.mention (.*)")
async def mention(event):
    """ For .chatid, returns the ID of the chat you are in at that moment. """
    if not event.text[0].isalpha() and event.text[0] not in ("/", "#", "@", "!"):
        if event.fwd_from:
            return
        input_str = event.pattern_match.group(1)
        if event.reply_to_msg_id:
            previous_message = await event.get_reply_message()
            if previous_message.forward:
                replied_user = previous_message.forward.from_id
            else:
                replied_user = previous_message.from_id
        else:
            return
        user_id = replied_user
        caption = """<a href='tg://user?id={}'>{}</a>""".format(
            user_id, input_str)
        await event.edit(caption, parse_mode="HTML")


@register(outgoing=True, pattern=r"^.log(?: |$)([\s\S]*)")
async def log(log_text):
    """ For .log command, forwards a message or the command argument to the bot logs group """
    if not log_text.text[0].isalpha() and log_text.text[0] not in ("/", "#", "@", "!"):
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
async def kickme(leave):
    """ Basically it's .kickme command """
    if not leave.text[0].isalpha() and leave.text[0] not in ("/", "#", "@", "!"):
        await leave.edit("`Nope, no, no, I go away`")
        await bot(LeaveChannelRequest(leave.chat_id))


@register(outgoing=True, pattern="^.unmutechat$")
async def unmute_chat(unm_e):
    """ For .unmutechat command, unmute a muted chat. """
    if not unm_e.text[0].isalpha() and unm_e.text[0] not in ("/", "#", "@", "!"):
        try:
            from userbot.modules.sql_helper.keep_read_sql import unkread
        except AttributeError:
            await unm_e.edit('`Running on Non-SQL Mode!`')
            return
        unkread(str(unm_e.chat_id))
        await unm_e.edit("```Unmuted this chat Successfully```")


@register(outgoing=True, pattern="^.mutechat$")
async def mute_chat(mute_e):
    """ For .mutechat command, mute any chat. """
    if not mute_e.text[0].isalpha() and mute_e.text[0] not in ("/", "#", "@", "!"):
        try:
            from userbot.modules.sql_helper.keep_read_sql import kread
        except AttributeError:
            await mute_e.edit("`Running on Non-SQL mode!`")
            return
        await mute_e.edit(str(mute_e.chat_id))
        kread(str(mute_e.chat_id))
        await mute_e.edit("`Shush! This chat will be silenced!`")
        if BOTLOG:
            await mute_e.client.send_message(
                BOTLOG_CHATID,
                str(mute_e.chat_id) + " was silenced.")


@register(incoming=True)
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
    "chat": ".chatid\
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
\n\n.mention <text>\
\nUsage: Reply to generate the user's permanent link with custom text."
})
