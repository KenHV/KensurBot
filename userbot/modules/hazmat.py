import datetime
from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.functions.account import UpdateNotifySettingsRequest
from userbot import bot, CMD_HELP
from userbot.events import register

@register(outgoing=True, pattern="^\.hz(?: |$)(.*)")
async def hazmat(event):
    if event.fwd_from:
        return
    if not event.reply_to_msg_id:
       await event.edit("`WoWoWo Capt!, we are not going suit a ghost!...`")
       return
    reply_message = await event.get_reply_message()
    if not reply_message.media:
       await event.edit("`Word can destroy anything Capt!...`")
       return
    chat = "@hazmat_suit_bot"
    await event.edit("```Suit Up Capt!, We are going to purge some virus...```")
    async with bot.conversation("@hazmat_suit_bot") as conv:
          try:
              response = conv.wait_event(events.NewMessage(incoming=True,from_users=905164246))
              await bot.forward_messages(chat, reply_message)
              response = await response
          except YouBlockedUserError:
              await event.reply("```Unblock @hazmat_suit_bot plox```")
              return
          else:
             file = response
             await event.delete()
             await event.client.send_message(event.chat_id, response.message, reply_to=event.message.reply_to_msg_id)
                            
CMD_HELP.update({
"hazmat":
".hz \
\nUsage: Reply to a image / sticker to suit up!"})
