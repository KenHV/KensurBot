from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.functions.messages import EditChatDefaultBannedRightsRequest
from telethon.tl.types import ChatBannedRights

from asyncio import sleep
from userbot import CMD_HELP
from userbot.events import register, errors_handler


@register(outgoing=True, pattern=r"^.lock ?(.*)")
@errors_handler
async def locks(event):
    if not event.text[0].isalpha() and event.text[0] not in (
            "/", "#", "@", "!"):
        input_str = event.pattern_match.group(1)
        peer_id = event.chat_id
        msg = None
        media = None
        sticker = None
        gif = None
        gamee = None
        ainline = None
        gpoll = None
        adduser = None
        cpin = None
        changeinfo = None
        if input_str is "msg":
            msg = True
            what = "messages"
        if input_str is "media":
            media = True
            what = "media"
        if input_str is "sticker":
            sticker = True
            what = "stickers"
        if input_str is "gif":
            gif = True
            what = "GIFs"
        if input_str is "game":
            gamee = True
            what = "games"
        if input_str is "inline":
            ainline = True
            what = "inline bots"
        if input_str is "poll":
            gpoll = True
            what = "polls"
        if input_str is "invite":
            adduser = True
            what = "invites"
        if input_str is "pin":
            cpin = True
            what = "pins"
        if input_str is "info":
            changeinfo = True
            what = "chat info"
        if input_str is "all":
            msg = True
            media = True
            sticker = True
            gif = True
            gamee = True
            ainline = True
            gpoll = True
            adduser = True
            cpin = True
            changeinfo = True
            what = "everything"

        banned_rights = ChatBannedRights(
            until_date=None,
            send_messages=msg,
            send_media=media,
            send_stickers=sticker,
            send_gifs=gif,
            send_games=gamee,
            send_inline=ainline,
            send_polls=gpoll,
            invite_users=adduser,
            pin_messages=cpin,
            change_info=changeinfo,
        )
        try:
            result = await event.client(EditChatDefaultBannedRightsRequest(
                peer=peer_id,
                banned_rights=banned_rights
            ))
        except BaseException:
            await event.edit("`Do I have proper rights fot that ??`")
        else:
            await event.edit(f"`Locked {what} for this chat !!`")
            await sleep(3)
            await event.delete()


@register(outgoing=True, pattern=r"^.unlock ?(.*)")
@errors_handler
async def rem_locks(event):
    if not event.text[0].isalpha() and event.text[0] not in (
            "/", "#", "@", "!"):
        input_str = event.pattern_match.group(1)
        peer_id = event.chat_id
        msg = None
        media = None
        sticker = None
        gif = None
        gamee = None
        ainline = None
        gpoll = None
        adduser = None
        cpin = None
        changeinfo = None
        if input_str is "msg":
            msg = False
            what = "messages"
        if input_str is "media":
            media = False
            what = "media"
        if input_str is "sticker":
            sticker = False
            what = "stickers"
        if input_str is "gif":
            gif = False
            what = "GIFs"
        if input_str is "game":
            gamee = False
            what = "games"
        if input_str is "inline":
            ainline = False
            what = "inline bots"
        if input_str is "poll":
            gpoll = False
            what = "polls"
        if input_str is "invite":
            adduser = False
            what = "invites"
        if input_str is "pin":
            cpin = False
            what = "pins"
        if input_str is "info":
            changeinfo = False
            what = "chat info"
        if input_str is "all":
            msg = False
            media = False
            sticker = False
            gif = False
            gamee = False
            ainline = False
            gpoll = False
            adduser = False
            cpin = False
            changeinfo = False
            what = "everything"

        banned_rights = ChatBannedRights(
            until_date=None,
            send_messages=msg,
            send_media=media,
            send_stickers=sticker,
            send_gifs=gif,
            send_games=gamee,
            send_inline=ainline,
            send_polls=gpoll,
            invite_users=adduser,
            pin_messages=cpin,
            change_info=changeinfo,
        )
        try:
            result = await event.client(EditChatDefaultBannedRightsRequest(
                peer=peer_id,
                banned_rights=banned_rights
            ))
        except BaseException:
            await event.edit("`Do I have proper rights fot that ??`")
        else:
            await event.edit(f"`Unlocked {what} for this chat !!`")
            await sleep(3)
            await event.delete()

CMD_HELP.update({
    "locks": ".lock <all (or) type(s)> or .unlock <all (or) type(s)>\
\nUsage: Allows you to lock/unlock some common message types in the chat.\
[NOTE: Requires proper admin rights in the chat !!]\
\n\nAvailable message types to lock/unlock are: \
\n`all, msg, media, sticker, gif, game, inline, poll, invite, pin, info`\
"})
