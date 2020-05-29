# Copyright (C) 2020 Aidil Aryanto.
# All rights reserved.

import datetime
import asyncio
from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.functions.account import UpdateNotifySettingsRequest
from userbot import bot, CMD_HELP
from userbot.events import register

@register(outgoing=True, pattern="^.netease(?: |$)(.*)")
async def _(event):
    if event.fwd_from:
        return
    song = event.pattern_match.group(1)
    chat = "@WooMaiBot"
    link = f"/netease {song}"
    await event.edit("```Getting Your Music```")
    async with bot.conversation(chat) as conv:
          await asyncio.sleep(2)
          await event.edit("`Downloading...Please wait`")
          try:
              r = conv.wait_event(events.NewMessage(incoming=True,from_users=573173175))
              msg = await bot.send_message(chat, link)
              await r
              response = conv.wait_event(events.NewMessage(incoming=True,from_users=573173175))
              respond = await response
              """ - don't spam notif - """
              await bot.send_read_acknowledge(conv.chat_id)
          except YouBlockedUserError:
              await event.reply("```Please unblock @WooMaiBot and try again```")
              return
          await event.edit("`Sending Your Music...`")
          await asyncio.sleep(5)
          await bot.forward_messages(event.chat_id, respond.message)
    await event.client.delete_messages(conv.chat_id,
                                       [msg.id, respond.id])
    await event.delete()

@register(outgoing=True, pattern="^.sdd(?: |$)(.*)")
async def _(event):
    if event.fwd_from:
        return
    d_link = event.pattern_match.group(1)
    if ".com" not in d_link:
        await event.edit("` I need a link to download something pro.`**(._.)**")
    else:
        await event.edit("**Initiating Download!**")
    chat = "@DeezLoadBot"
    async with bot.conversation(chat) as conv:
          try:
              msg = await conv.send_message(d_link)
              details = await conv.get_response()
              msg_details = await bot.send_message(event.chat_id, details)
              song = await conv.get_response()
              """ - don't spam notif - """
              await bot.send_read_acknowledge(conv.chat_id)
              await bot.send_file(event.chat_id, song)
              await event.client.delete_messages(conv.chat_id,
                                                 [msg.id, msg_details.id, details.id, song.id])
              await event.delete()
          except YouBlockedUserError:
              await event.edit("**Error:** `unblock` @DeezLoadBot `and retry!`")
              return

@register(outgoing=True, pattern="^.smd(?: |$)(.*)")
async def _(event):
    if event.fwd_from:
        return
    link = event.pattern_match.group(1)
    chat = "@SpotifyMusicDownloaderBot"
    await event.edit("```Getting Your Music```")
    async with bot.conversation(chat) as conv:
          await asyncio.sleep(2)
          await event.edit("`Downloading music taking some times,  Stay Tuned.....`")
          try:
              response = conv.wait_event(events.NewMessage(incoming=True,from_users=752979930))
              msg = await bot.send_message(chat, link)
              respond = await response
              res = conv.wait_event(events.NewMessage(incoming=True,from_users=752979930))
              r = await res
              """ - don't spam notif - """
              await bot.send_read_acknowledge(conv.chat_id)
          except YouBlockedUserError:
              await event.reply("```Please unblock @SpotifyMusicDownloaderBot and try again```")
              return
          await bot.forward_messages(event.chat_id, respond.message)
    await event.client.delete_messages(conv.chat_id,
                                       [msg.id, r.id, respond.id])
    await event.delete()

CMD_HELP.update({
    "getmusic":
    ">`.netease <Artist - Song Title>`"
    "\nUsage: Download music with @WooMaiBot"
    "\n\n>`.sdd <Spotify/Deezer Link>`"
    "\nUsage: Download music from Spotify or Deezer"
    "\n\n>`.smd <Artist - Song Title>`"
    "\nUsage: Download music from Spotify"
})
