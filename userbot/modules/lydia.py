# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
# credit goes to @snapdragon and @devpatel_73 for making it work on this userbot.
#
"""
Userbot module to help you manage a group
"""

import coffeehouse
import asyncio
from userbot import LYDIA_API_KEY
from userbot.events import register
from telethon import events

# Non-SQL Mode
ACC_LYDIA = {}
SESSION_ID = {}

if LYDIA_API_KEY:
    api_key = LYDIA_API_KEY
    api_client = coffeehouse.API(api_key)

@register(outgoing=True, pattern="^.repcf$")
async def repcf(event):
    if event.fwd_from:
        return
    await event.edit("Processing...")
    try:
        session = api_client.create_session()
        session_id = session.id
        reply = await event.get_reply_message()
        msg = reply.text
        text_rep = session.think_thought((session_id, msg))
        await event.edit("**Lydia says**: {0}".format(text_rep))
    except Exception as e:
        await event.edit(str(e))

@register(outgoing=True, pattern="^.addcf$")
async def addcf(event):
    if event.fwd_from:
        return
    await event.edit("Running on SQL mode for now...")
    await asyncio.sleep(4)
    await event.edit("Processing...")
    reply_msg = await event.get_reply_message()
    if reply_msg:
        session = api_client.create_session()
        session_id = session.id
        ACC_LYDIA.update({str(event.chat_id) + " " + str(reply_msg.from_id): session})
        SESSION_ID.update({str(event.chat_id) + " " + str(reply_msg.from_id): session_id})
        await event.edit("Lydia successfully enabled for user: {} in chat: {}".format(str(reply_msg.from_id), str(event.chat_id)))
    else:
        await event.edit("Reply to a user to activate Lydia AI on them")

@register(outgoing=True, pattern="^.remcf$")
async def remcf(event):
    if event.fwd_from:
        return
    await event.edit("Running on SQL mode for now...")
    await asyncio.sleep(4)
    await event.edit("Processing...")
    reply_msg = await event.get_reply_message()
    try:
        del ACC_LYDIA[str(event.chat_id) + " " + str(reply_msg.from_id)]
        del SESSION_ID[str(event.chat_id) + " " + str(reply_msg.from_id)]
        await event.edit("Lydia successfully disabled for user: {} in chat: {}".format(str(reply_msg.from_id), str(event.chat_id)))
    except KeyError:
        await event.edit("This person does not have Lydia activated on him/her.")

@register(incoming=True, disable_edited=True)
async def user(event):
    user_text = event.text
    try:
        session = ACC_LYDIA[str(event.chat_id) + " " + str(event.from_id)]
        session_id = SESSION_ID[str(event.chat_id) + " " + str(event.from_id)]
        msg = event.text
        async with event.client.action(event.chat_id, "typing"):
            text_rep = session.think_thought((session_id, msg))
            wait_time = 0
            for i in range(len(text_rep)):
                wait_time = wait_time + 0.1
            await asyncio.sleep(wait_time)
            await event.reply(text_rep)
    except KeyError:
        return

    
"""CMD_HELP.update({
    "lydia":
    ".addcf <username/reply>\
\nUsage: add's lydia auto chat request in the chat.\
\n\n.remcf <username/reply>\
\nUsage: remove's lydia auto chat request in the chat.\
\n\n.repcf <username/reply>\
\nUsage: starts lydia repling to perticular person in the chat."
})
"""
