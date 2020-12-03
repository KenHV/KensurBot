# Copyright (C) 2020 AnggaR96s.
# All rights reserved.

from asyncio.exceptions import TimeoutError

from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError

from userbot import CMD_HELP, bot
from userbot.events import register


@register(outgoing=True, pattern=r"^\.ddl(?: |$)(.*)")
async def ddl(event):
    if event.fwd_from:
        return
    if not event.reply_to_msg_id:
        return await event.edit("**Reply to a message containing media!**")
    reply_message = await event.get_reply_message()
    if not reply_message.media:
        return await event.edit("**Reply to a message containing media!**")
    await event.edit("**Generating direct link...**")
    try:
        async with bot.conversation("@jnckbot") as conv:
            chat = "@jnckbot"
            try:
                response = conv.wait_event(
                    events.NewMessage(incoming=True, from_users=994325826))
                await bot.forward_messages(chat, reply_message)
                response = await response
                await bot.send_read_acknowledge(conv.chat_id)
            except YouBlockedUserError:
                await event.reply("**Unblock @jnckbot!**")
                return
            await event.delete()
    except TimeoutError:
        return await event.edit("**Error: @jnckbot is not responding.**")
    await event.client.send_message(event.chat_id,
                                    response.message,
                                    reply_to=event.message.reply_to_msg_id)


CMD_HELP.update(
    {"ddl": ">`.ddl` \
\nUsage: Reply to a media to get direct link."})
