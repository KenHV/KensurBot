# Copyright (C) 2021 KenHV

from sqlalchemy.exc import IntegrityError

from userbot import CMD_HELP
from userbot.events import register


@register(outgoing=True, pattern=r"^\.blacklist (.*)")
async def blacklist(event):
    """Adds given chat to blacklist."""
    try:
        from userbot.modules.sql_helper.blacklist_sql import add_blacklist
    except IntegrityError:
        return await event.edit("**Running on Non-SQL mode!**")

    try:
        chat_id = int(event.pattern_match.group(1))
    except ValueError:
        chat_id = event.pattern_match.group(1)

    try:
        chat_id = await event.client.get_peer_id(chat_id)
    except Exception:
        return await event.edit("**Error: Invalid username/ID provided.**")

    try:
        add_blacklist(str(chat_id))
    except IntegrityError:
        return await event.edit("**Given chat is already blacklisted.**")

    await event.edit("**Blacklisted given chat!**")


@register(outgoing=True, pattern=r"^\.unblacklist (.*)")
async def unblacklist(event):
    """Unblacklists given chat."""
    try:
        from userbot.modules.sql_helper.blacklist_sql import (
            del_blacklist,
            get_blacklist,
        )
    except IntegrityError:
        return await event.edit("**Running on Non-SQL mode!**")

    chat_id = event.pattern_match.group(1)
    try:
        chat_id = str(await event.client.get_peer_id(chat_id))
    except Exception:
        pass  # this way, deleted chats can be unblacklisted

    if chat_id == "all":
        from userbot.modules.sql_helper.blacklist_sql import del_blacklist_all

        del_blacklist_all()
        return await event.edit("**Cleared all blacklists!**")

    id_exists = False
    for i in get_blacklist():
        if chat_id == i.chat_id:
            id_exists = True

    if not id_exists:
        return await event.edit("**This chat isn't blacklisted.**")

    del_blacklist(chat_id)
    await event.edit("**Un-blacklisted given chat!**")


@register(outgoing=True, pattern=r"^\.blacklists$")
async def list_blacklist(event):
    """Lists all blacklisted chats."""
    try:
        from userbot.modules.sql_helper.blacklist_sql import get_blacklist
    except IntegrityError:
        return await event.edit("**Running on Non-SQL mode!**")

    chat_list = get_blacklist()
    if not chat_list:
        return await event.edit("**You haven't blacklisted any chats yet!**")

    msg = "**Blacklisted chats:**\n\n"

    for i in chat_list:
        try:
            chat = await event.client.get_entity(int(i.chat_id))
            chat = f"{chat.title} | `{i.chat_id}`"
        except (TypeError, ValueError):
            chat = f"__Couldn't fetch chat info__ | `{i.chat_id}`"

        msg += f"• {chat}\n"

    await event.edit(msg)


CMD_HELP.update(
    {
        "blacklist": "**Disables all userbot functions on blacklisted groups.**"
        "\n\n`>.blacklist <username/id>`"
        "\nUsage: Blacklists provided chat."
        "\n\n>`.unblacklist <username/id>`"
        "\nUsage: Removes provided chat from blacklist."
        "\n\n>`.unblacklist all`"
        "\nUsage: Removes all chats from blacklist."
        "\n\n>`.blacklists`"
        "\nUsage: Lists all blacklisted chats."
    }
)
