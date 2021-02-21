# port to userbot by @MoveAngel

from asyncio.exceptions import TimeoutError

from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError

from userbot import CMD_HELP, bot
from userbot.events import register


@register(outgoing=True, pattern=r"^\.q$")
async def _(event):
    if event.fwd_from:
        return
    if not event.reply_to_msg_id:
        return await event.edit("**Reply to a text message.**")
    reply_message = await event.get_reply_message()
    if not reply_message.text:
        return await event.edit("**Reply to a text message.**")
    chat = "@QuotLyBot"
    await event.edit("**Processing...**")

    try:
        async with bot.conversation(chat) as conv:
            try:
                response = conv.wait_event(
                    events.NewMessage(incoming=True, from_users=1031952739)
                )
                await bot.forward_messages(chat, reply_message)
                response = await response
                await bot.send_read_acknowledge(conv.chat_id)

            except YouBlockedUserError:
                return await event.reply("**Please unblock @QuotLyBot and try again**")

            if response.text.startswith("Hi!"):
                await event.edit(
                    "**Can you kindly disable your forward privacy settings for good?**"
                )
            else:
                await event.delete()
                await bot.forward_messages(event.chat_id, response.message)

    except TimeoutError:
        return await event.edit("**Error: **@QuotLyBot** is not responding.**")


CMD_HELP.update(
    {
        "quote": ">`.q`"
        "\nUsage: Reply to a text message to convert to sticker using Quotly bot."
    }
)
