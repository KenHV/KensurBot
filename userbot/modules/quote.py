# Copyright (C) 2018-2019 Friendly Telegram
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
#
# Port to UserBot by @MoveAngel

import requests
import base64
import json
import telethon

from logging import Logger as logger
from PIL import Image
from io import BytesIO
from userbot import bot, CMD_HELP, QUOTES_API_TOKEN
from userbot.events import register


if 1 == 1:
    strings = {
        "name": "Quotes",
        "api_token_cfg_doc": "API Key/Token for Quotes.",
        "api_url_cfg_doc": "API URL for Quotes.",
        "colors_cfg_doc": "Username colors",
        "default_username_color_cfg_doc": "Default color for the username.",
        "no_reply": "<b>You didn't reply to a message.</b>",
        "no_template": "<b>You didn't specify the template.</b>",
        "delimiter": "</code>, <code>",
        "server_error": "<b>Server error. Please report to developer.</b>",
        "invalid_token": "<b>You've set an invalid token, get it from `http://antiddos.systems`.</b>",
        "unauthorized": "<b>You're unauthorized to do this.</b>",
        "not_enough_permissions": "<b>Wrong template. You can use only the default one.</b>",
        "templates": "<b>Available Templates:</b> <code>{}</code>",
        "cannot_send_stickers": "<b>You cannot send stickers in this chat.</b>",
        "admin": "admin",
        "creator": "creator",
        "hidden": "hidden",
        "channel": "Channel"
    }

config = dict({"api_url": "http://api.antiddos.systems",
               "username_colors": ["#fb6169", "#faa357", "#b48bf2", "#85de85",
                                   "#62d4e3", "#65bdf3", "#ff5694"],
               "default_username_color": "#b48bf2"})

@register(outgoing=True, pattern="^.quote(?: |$)(.*)")
async def quotecmd(message):  # noqa: C901
    """Quote a message.
    Usage: .pch [template]
    If template is missing, possible templates are fetched."""
    if not QUOTES_API_TOKEN:
        return await message.edit(
            "`Error: Quotes API key is missing! Add it to environment variables or config.env.`"
        )
    await message.delete()
    args = message.raw_text.split(" ")[1:]
    if args == []:
        args = ["default"]
    reply = await message.get_reply_message()
    if not reply:
        return await message.respond(strings["no_reply"])
    if not args:
        return await message.respond(strings["no_template"])
    username_color = username = admintitle = user_id = None
    profile_photo_url = reply.from_id
    admintitle = ""
    if isinstance(message.to_id, telethon.tl.types.PeerChannel):
        try:
            user = await bot(telethon.tl.functions.channels.GetParticipantRequest(message.chat_id,
                                                                                  reply.from_id))
            if isinstance(user.participant, telethon.tl.types.ChannelParticipantCreator):
                admintitle = user.participant.rank or strings["creator"]
            elif isinstance(user.participant, telethon.tl.types.ChannelParticipantAdmin):
                admintitle = user.participant.rank or strings["admin"]
            user = user.users[0]
        except telethon.errors.rpcerrorlist.UserNotParticipantError:
            user = await reply.get_sender()
    elif isinstance(message.to_id, telethon.tl.types.PeerChat):
        chat = await bot(telethon.tl.functions.messages.GetFullChatRequest(reply.to_id))
        participants = chat.full_chat.participants.participants
        participant = next(filter(lambda x: x.user_id == reply.from_id, participants), None)
        if isinstance(participant, telethon.tl.types.ChatParticipantCreator):
            admintitle = strings["creator"]
        elif isinstance(participant, telethon.tl.types.ChatParticipantAdmin):
            admintitle = strings["admin"]
        user = await reply.get_sender()
    else:
        user = await reply.get_sender()
    username = telethon.utils.get_display_name(user)
    user_id = reply.from_id

    if reply.fwd_from:
        if reply.fwd_from.saved_from_peer:
            username = telethon.utils.get_display_name(reply.forward.chat)
            profile_photo_url = reply.forward.chat
            admintitle = strings["channel"]
        elif reply.fwd_from.from_name:
            username = reply.fwd_from.from_name
        elif reply.forward.sender:
            username = telethon.utils.get_display_name(reply.forward.sender)
        elif reply.forward.chat:
            username = telethon.utils.get_display_name(reply.forward.chat)

    pfp = await bot.download_profile_photo(profile_photo_url, bytes)
    if pfp is not None:
        profile_photo_url = "data:image/png;base64, " + base64.b64encode(pfp).decode()

    if user_id is not None:
        username_color = config["username_colors"][user_id % 7]
    else:
        username_color = config["default_username_color"]

    request = json.dumps({
        "ProfilePhotoURL": profile_photo_url,
        "usernameColor": username_color,
        "username": username,
        "adminTitle": admintitle,
        "Text": reply.message,
        "Markdown": await get_markdown(reply),
        "Template": args[0],
        "APIKey": QUOTES_API_TOKEN
    })

    resp = requests.post(config["api_url"] + "/api/v2/quote", data=request)
    resp.raise_for_status()
    resp = resp.json()

    if resp["status"] == 500:
        return await message.respond(strings["server_error"])
    elif resp["status"] == 401:
        if resp["message"] == "ERROR_TOKEN_INVALID":
            return await message.respond(strings["invalid_token"])
        else:
            raise ValueError("Invalid response from server", resp)
    elif resp["status"] == 403:
        if resp["message"] == "ERROR_UNAUTHORIZED":
            return await message.respond(strings["unauthorized"])
        else:
            raise ValueError("Invalid response from server", resp)
    elif resp["status"] == 404:
        if resp["message"] == "ERROR_TEMPLATE_NOT_FOUND":
            newreq = requests.post(config["api_url"] + "/api/v1/getalltemplates", data={
                "token": QUOTES_API_TOKEN
            })
            newreq = newreq.json()

            if newreq["status"] == "NOT_ENOUGH_PERMISSIONS":
                return await message.respond(strings["not_enough_permissions"])
            elif newreq["status"] == "SUCCESS":
                templates = strings["delimiter"].join(newreq["message"])
                return await message.respond(strings["templates"].format(templates))
            elif newreq["status"] == "INVALID_TOKEN":
                return await message.respond(strings["invalid_token"])
            else:
                raise ValueError("Invalid response from server", newreq)
        else:
            raise ValueError("Invalid response from server", resp)
    elif resp["status"] != 200:
        raise ValueError("Invalid response from server", resp)
    req = requests.get(config["api_url"] + "/cdn/" + resp["message"])
    req.raise_for_status()
    file = BytesIO(req.content)
    file.seek(0)
    img = Image.open(file)
    with BytesIO() as sticker:
        img.save(sticker, "webp")
        sticker.name = "sticker.webp"
        sticker.seek(0)
        try:
            await reply.reply(file=sticker)
        except telethon.errors.rpcerrorlist.ChatSendStickersForbiddenError:
            await message.respond(strings["cannot_send_stickers"])
        file.close()


async def get_markdown(reply):
    if not reply.entities:
        return []

    markdown = []
    for entity in reply.entities:
        md_item = {
            "Type": None,
            "Start": entity.offset,
            "End": entity.offset + entity.length - 1
        }
        if isinstance(entity, telethon.tl.types.MessageEntityBold):
            md_item["Type"] = "bold"
        elif isinstance(entity, telethon.tl.types.MessageEntityItalic):
            md_item["Type"] = "italic"
        elif isinstance(entity, (telethon.tl.types.MessageEntityMention, telethon.tl.types.MessageEntityTextUrl,
                                 telethon.tl.types.MessageEntityMentionName, telethon.tl.types.MessageEntityHashtag,
                                 telethon.tl.types.MessageEntityCashtag, telethon.tl.types.MessageEntityBotCommand,
                                 telethon.tl.types.MessageEntityUrl)):
            md_item["Type"] = "link"
        elif isinstance(entity, telethon.tl.types.MessageEntityCode):
            md_item["Type"] = "code"
        elif isinstance(entity, telethon.tl.types.MessageEntityStrike):
            md_item["Type"] = "stroke"
        elif isinstance(entity, telethon.tl.types.MessageEntityUnderline):
            md_item["Type"] = "underline"
        else:
            logger.warning("Unknown entity: " + str(entity))

        markdown.append(md_item)
    return markdown


CMD_HELP.update({
    "stickerchat":
    ">`.quote`"
    "\nUsage: Same as quotly, enhance ur text to sticker."
})
