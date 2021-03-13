# Ported by Aidil Aryanto

import os
from asyncio.exceptions import TimeoutError

from telethon.errors.rpcerrorlist import YouBlockedUserError

from userbot import CMD_HELP, TEMP_DOWNLOAD_DIRECTORY, bot
from userbot.events import register


@register(outgoing=True, pattern=r"^\.spotnow$")
async def _(event):
    if event.fwd_from:
        return
    chat = "@SpotifyNowBot"
    now = "/now"
    await event.edit("**Processing...**")
    try:
        async with event.client.conversation(chat) as conv:
            try:
                msg = await conv.send_message(now)
                response = await conv.get_response()
                """ - don't spam notif - """
                await bot.send_read_acknowledge(conv.chat_id)
            except YouBlockedUserError:
                await event.reply("**Please unblock** @SpotifyNowBot**.**")
                return
            if response.text.startswith("You're"):
                await event.edit(
                    "**You're not listening to anything on Spotify at the moment.**"
                )
                return
            downloaded_file_name = await event.client.download_media(
                response.media, TEMP_DOWNLOAD_DIRECTORY
            )
            link = response.reply_markup.rows[0].buttons[0].url
            await event.client.send_file(
                event.chat_id,
                downloaded_file_name,
                force_document=False,
                caption=f"[Play on Spotify]({link})",
            )
            """ - cleanup chat after completed - """
            await event.client.delete_messages(conv.chat_id, [msg.id, response.id])
    except TimeoutError:
        return await event.edit("**Error:** @SpotifyNowBot **is not responding.**")
    await event.delete()
    return os.remove(downloaded_file_name)


CMD_HELP.update(
    {
        "spotifynow": ">`.spotnow`"
        "\nUsage: Show what you're listening on spotify."
        "\n@SpotifyNowBot"
    }
)
