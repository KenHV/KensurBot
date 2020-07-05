# Copyright (C) 2020 AnggaR96s.
# All rights reserved.

from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError
from userbot import bot, CMD_HELP
from userbot.events import register

@register(outgoing=True, pattern="^\.ddl(?: |$)(.*)")
async def ddl(event):
    if event.fwd_from:
        return
    if not event.reply_to_msg_id:
       await event.edit("`Sending information..`")
       return
    reply_message = await event.get_reply_message()
    if not reply_message.media:
       await event.edit("`¯\_ (ツ) _/¯`")
       return
    await event.edit("```Generating direct link..```")
    async with bot.conversation("@jnckbot") as conv:
        chat = "@jnckbot"
        try:
            response = conv.wait_event(events.NewMessage(incoming=True,from_users=994325826))
            await bot.forward_messages(chat, reply_message)
            response = await response
            await bot.send_read_acknowledge(conv.chat_id)
        except YouBlockedUserError:
            await event.reply("```Unblock @jnckbot plox```")
            return
        await event.delete()
    await event.client.send_message(event.chat_id, response.message, reply_to=event.message.reply_to_msg_id)

CMD_HELP.update({
"ddl":
">`.ddl` \
\nUsage: Reply to a media to get direct link."})
