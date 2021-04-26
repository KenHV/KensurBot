# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module for changing your Telegram profile details. """

import os

from telethon.errors import ImageProcessFailedError, PhotoCropSizeSmallError
from telethon.errors.rpcerrorlist import PhotoExtInvalidError, UsernameOccupiedError
from telethon.tl.functions.account import UpdateProfileRequest, UpdateUsernameRequest
from telethon.tl.functions.channels import GetAdminedPublicChannelsRequest
from telethon.tl.functions.photos import (
    DeletePhotosRequest,
    GetUserPhotosRequest,
    UploadProfilePhotoRequest,
)
from telethon.tl.types import Channel, Chat, InputPhoto, MessageMediaPhoto, User

from userbot import CMD_HELP, bot
from userbot.events import register

# ====================== CONSTANT ===============================
INVALID_MEDIA = "**The extension of the media entity is invalid.**"
PP_CHANGED = "**Profile picture changed successfully.**"
PP_TOO_SMOL = "**This image is too small, use a bigger image.**"
PP_ERROR = "**Failure occured while processing image.**"

BIO_SUCCESS = "**Successfully edited Bio.**"

NAME_OK = "**Your name was succesfully changed.**"
USERNAME_SUCCESS = "**Your username was succesfully changed.**"
USERNAME_TAKEN = "**This username is already taken.**"
# ===============================================================


@register(outgoing=True, pattern=r"^\.reserved$")
async def mine(event):
    """For .reserved command, get a list of your reserved usernames."""
    result = await bot(GetAdminedPublicChannelsRequest())
    output_str = "".join(
        f"{channel_obj.title}\n@{channel_obj.username}\n\n"
        for channel_obj in result.chats
    )

    await event.edit(output_str)


@register(outgoing=True, pattern=r"^\.name")
async def update_name(name):
    """For .name command, change your name in Telegram."""
    newname = name.text[6:]
    if " " not in newname:
        firstname = newname
        lastname = ""
    else:
        namesplit = newname.split(" ", 1)
        firstname = namesplit[0]
        lastname = namesplit[1]

    await name.client(UpdateProfileRequest(first_name=firstname, last_name=lastname))
    await name.edit(NAME_OK)


@register(outgoing=True, pattern=r"^\.setpfp$")
async def set_profilepic(propic):
    """For .profilepic command, change your profile picture in Telegram."""
    replymsg = await propic.get_reply_message()
    photo = None
    if replymsg.media:
        if isinstance(replymsg.media, MessageMediaPhoto):
            photo = await propic.client.download_media(message=replymsg.photo)
        elif "image" in replymsg.media.document.mime_type.split("/"):
            photo = await propic.client.download_file(replymsg.media.document)
        else:
            await propic.edit(INVALID_MEDIA)

    if photo:
        try:
            await propic.client(
                UploadProfilePhotoRequest(await propic.client.upload_file(photo))
            )
            os.remove(photo)
            await propic.edit(PP_CHANGED)
        except PhotoCropSizeSmallError:
            await propic.edit(PP_TOO_SMOL)
        except ImageProcessFailedError:
            await propic.edit(PP_ERROR)
        except PhotoExtInvalidError:
            await propic.edit(INVALID_MEDIA)


@register(outgoing=True, pattern=r"^\.setbio (.*)")
async def set_biograph(setbio):
    """For .setbio command, set a new bio for your profile in Telegram."""
    newbio = setbio.pattern_match.group(1)
    await setbio.client(UpdateProfileRequest(about=newbio))
    await setbio.edit(BIO_SUCCESS)


@register(outgoing=True, pattern=r"^\.username (.*)")
async def update_username(username):
    """For .username command, set a new username in Telegram."""
    newusername = username.pattern_match.group(1)
    try:
        await username.client(UpdateUsernameRequest(newusername))
        await username.edit(USERNAME_SUCCESS)
    except UsernameOccupiedError:
        await username.edit(USERNAME_TAKEN)


@register(outgoing=True, pattern=r"^\.count$")
async def count(event):
    """For .count command, get profile stats."""
    u = 0
    g = 0
    c = 0
    bc = 0
    b = 0
    result = ""
    await event.edit("**Processing...**")
    dialogs = await bot.get_dialogs(limit=None, ignore_migrated=True)
    for d in dialogs:
        currrent_entity = d.entity
        if isinstance(currrent_entity, User):
            if currrent_entity.bot:
                b += 1
            else:
                u += 1
        elif isinstance(currrent_entity, Chat):
            g += 1
        elif isinstance(currrent_entity, Channel):
            if currrent_entity.broadcast:
                bc += 1
            else:
                c += 1
        else:
            print(d)

    result += f"**Users:**\t`{u}`\n"
    result += f"**Groups:**\t`{g}`\n"
    result += f"**Supergroups:**\t`{c}`\n"
    result += f"**Channels:**\t`{bc}`\n"
    result += f"**Bots:**\t`{b}`"

    await event.edit(result)


@register(outgoing=True, pattern=r"^\.delpfp")
async def remove_profilepic(delpfp):
    """For .delpfp command, delete your current profile picture in Telegram."""
    group = delpfp.text[8:]
    if group == "all":
        lim = 0
    elif group.isdigit():
        lim = int(group)
    else:
        lim = 1

    pfplist = await delpfp.client(
        GetUserPhotosRequest(user_id=delpfp.sender_id, offset=0, max_id=0, limit=lim)
    )
    input_photos = [
        InputPhoto(
            id=sep.id,
            access_hash=sep.access_hash,
            file_reference=sep.file_reference,
        )
        for sep in pfplist.photos
    ]
    await delpfp.client(DeletePhotosRequest(id=input_photos))
    await delpfp.edit(
        f"**Successfully deleted** `{len(input_photos)}` **profile picture(s).**"
    )


CMD_HELP.update(
    {
        "profile": ">`.username <new_username>`"
        "\nUsage: Changes your Telegram username."
        "\n\n>`.name <firstname>` or >`.name <firstname> <lastname>`"
        "\nUsage: Changes your Telegram name.(First and last name will get split by the first space)"
        "\n\n>`.setpfp`"
        "\nUsage: Reply with .setpfp to an image to change your Telegram profie picture."
        "\n\n>`.setbio <new_bio>`"
        "\nUsage: Changes your Telegram bio."
        "\n\n>`.delpfp` or >`.delpfp <number>/<all>`"
        "\nUsage: Deletes your Telegram profile picture(s)."
        "\n\n>`.reserved`"
        "\nUsage: Shows usernames reserved by you."
        "\n\n>`.count`"
        "\nUsage: Counts your groups, chats, bots etc..."
    }
)
