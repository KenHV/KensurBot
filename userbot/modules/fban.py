# Copyright (C) 2020 KenHV

from sqlalchemy.exc import IntegrityError

from userbot import CMD_HELP
from userbot.events import register


@register(outgoing=True, pattern=r"^\.fban *(.*)")
async def fban(event):
    """Bans a user from connected federations."""
    try:
        from userbot.modules.sql_helper.fban_sql import get_flist
    except IntegrityError:
        return await event.edit("`Running on Non-SQL mode!`")

    if (reply_msg := await event.get_reply_message()):
        fban_id = reply_msg.from_id
        reason = event.pattern_match.group(1)
    else:
        pattern = str(event.pattern_match.group(1)).split()
        fban_id = pattern[0]
        reason = ''.join(pattern[1:])

    self_user = await event.client.get_me()

    if fban_id == self_user.id or fban_id == "@" + self_user.username:
        return await event.edit(
            "`Error: This action has been prevented by KensurBot self preservation protocols.`"
        )

    if isinstance(fban_id, int):
        user_link = f"[{fban_id}](tg://user?id={fban_id})"
    else:
        user_link = fban_id

    if len((fed_list := get_flist())) == 0:
        return await event.edit("`You haven't connected any federations yet!`")

    await event.edit(f"`Fbanning `{user_link}`...`")

    for i in fed_list:
        await event.client.send_message(
            int(i.chat_id),
            f"/fban [{fban_id}](tg://user?id={fban_id}) {reason}")

    reason = reason if reason else "Not specified."
    await event.edit(f"`Fbanned `{user_link}`!\nReason: `{reason}")


@register(outgoing=True, pattern=r"^\.unfban *(.*)")
async def unfban(event):
    """Unbans a user from connected federations."""
    try:
        from userbot.modules.sql_helper.fban_sql import get_flist
    except IntegrityError:
        return await event.edit("`Running on Non-SQL mode!`")

    if (reply_msg := await event.get_reply_message()):
        unfban_id = reply_msg.from_id
        reason = event.pattern_match.group(1)
    else:
        pattern = str(event.pattern_match.group(1)).split()
        unfban_id = pattern[0]
        reason = ''.join(pattern[1:])

    self_user = await event.client.get_me()

    if unfban_id == self_user.id or unfban_id == "@" + self_user.username:
        return await event.edit("`Wait, that's illegal`")

    if isinstance(unfban_id, int):
        user_link = f"[{unfban_id}](tg://user?id={unfban_id})"
    else:
        user_link = unfban_id

    if len((fed_list := get_flist())) == 0:
        return await event.edit("`You haven't connected any federations yet!`")

    await event.edit(f"`Un-fbanning `{user_link}`...`")

    for i in fed_list:
        await event.client.send_message(
            int(i.chat_id),
            f"/unfban [{unfban_id}](tg://user?id={unfban_id}) {reason}")

    reason = reason if reason else "Not specified."
    await event.edit(f"`Un-fbanned `{user_link}`!\nReason: `{reason}")


@register(outgoing=True, pattern=r"^\.addf *(.*)")
async def addf(event):
    """Adds current chat to connected federations."""
    try:
        from userbot.modules.sql_helper.fban_sql import add_flist
    except IntegrityError:
        return await event.edit("`Running on Non-SQL mode!`")

    if not (fed_name := event.pattern_match.group(1)):
        return await event.edit("`Pass a name in order connect to this group!`"
                                )

    try:
        add_flist(event.chat_id, fed_name)
    except IntegrityError:
        return await event.edit(
            "`This group is already connected to federations list.`")

    await event.edit("`Added this group to federations list!`")


@register(outgoing=True, pattern=r"^\.delf$")
async def delf(event):
    """Removes current chat from connected federations."""
    try:
        from userbot.modules.sql_helper.fban_sql import del_flist
    except IntegrityError:
        return await event.edit("`Running on Non-SQL mode!`")

    del_flist(event.chat_id)
    await event.edit("`Removed this group from federations list!`")


@register(outgoing=True, pattern=r"^\.listf$")
async def listf(event):
    """List all connected federations."""
    try:
        from userbot.modules.sql_helper.fban_sql import get_flist
    except IntegrityError:
        return await event.edit("`Running on Non-SQL mode!`")

    if len((fed_list := get_flist())) == 0:
        return await event.edit(
            "`You haven't connected to any federations yet!`")

    msg = "**Connected federations:**\n\n"

    for i in fed_list:
        msg += "• " + str(i.fed_name) + "\n"

    await event.edit(msg)


CMD_HELP.update({
    "fban":
    ">`.fban <id/username> <reason>`"
    "\nUsage: Bans user from connected federations."
    "\nYou can reply to the user whom you want to fban or manually pass the username/id."
    "\n\n`>.unfban <id/username> <reason>`"
    "\nUsage: Same as fban but unbans the user"
    "\n\n>`.addf <name>`"
    "\nUsage: Adds current group and stores it as <name> in connected federations."
    "\nAdding one group is enough for one federation."
    "\n\n>`.delf`"
    "\nUsage: Removes current group from connected federations."
    "\n\n>`.listf`"
    "\nUsage: Lists all connected federations by specified name."
})
