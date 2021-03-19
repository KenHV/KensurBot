# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module for keeping control who PM you. """

from sqlalchemy.exc import IntegrityError
from telethon.tl.functions.contacts import BlockRequest, UnblockRequest
from telethon.tl.functions.messages import ReportSpamRequest
from telethon.tl.types import User

from userbot import (
    BOTLOG,
    BOTLOG_CHATID,
    CMD_HELP,
    COUNT_PM,
    LASTMSG,
    LOGS,
    PM_AUTO_BAN,
)
from userbot.events import register

# ========================= CONSTANTS ============================
DEF_UNAPPROVED_MSG = (
    "Hey there! Unfortunately, I don't accept private messages from strangers.\n"
    "Please contact me in a group, or wait for me to approve you."
)
# =================================================================


@register(incoming=True, disable_edited=True, disable_errors=True)
async def permitpm(event):
    """ Prohibits people from PMing you without approval. \
        Will block retarded nibbas automatically. """
    if not PM_AUTO_BAN:
        return
    self_user = await event.client.get_me()
    if (
        event.is_private
        and event.chat_id != 777000
        and event.chat_id != self_user.id
        and not (await event.get_sender()).bot
    ):
        try:
            from userbot.modules.sql_helper.globals import gvarstatus
            from userbot.modules.sql_helper.pm_permit_sql import is_approved
        except AttributeError:
            return
        apprv = is_approved(event.chat_id)
        notifsoff = gvarstatus("NOTIF_OFF")

        # Use user custom unapproved message
        getmsg = gvarstatus("unapproved_msg")
        UNAPPROVED_MSG = getmsg if getmsg is not None else DEF_UNAPPROVED_MSG
        # This part basically is a sanity check
        # If the message that sent before is Unapproved Message
        # then stop sending it again to prevent FloodHit
        if not apprv and event.text != UNAPPROVED_MSG:
            if event.chat_id in LASTMSG:
                prevmsg = LASTMSG[event.chat_id]
                # If the message doesn't same as previous one
                # Send the Unapproved Message again
                if event.text != prevmsg:
                    async for message in event.client.iter_messages(
                        event.chat_id, from_user="me", search=UNAPPROVED_MSG
                    ):
                        await message.delete()
                    await event.reply(f"`{UNAPPROVED_MSG}`")
            else:
                await event.reply(f"`{UNAPPROVED_MSG}`")
            LASTMSG.update({event.chat_id: event.text})
            if notifsoff:
                await event.client.send_read_acknowledge(event.chat_id)
            if event.chat_id not in COUNT_PM:
                COUNT_PM.update({event.chat_id: 1})
            else:
                COUNT_PM[event.chat_id] = COUNT_PM[event.chat_id] + 1

            if COUNT_PM[event.chat_id] > 4:
                await event.respond(
                    "`You were spamming my master's PM, which I didn't like.`\n"
                    "`You have been blocked and reported as spam, until further notice.`"
                )

                try:
                    del COUNT_PM[event.chat_id]
                    del LASTMSG[event.chat_id]
                except KeyError:
                    if BOTLOG:
                        await event.client.send_message(
                            BOTLOG_CHATID,
                            "Count PM is seemingly going retard, plis restart bot!",
                        )
                    return LOGS.info("CountPM wen't rarted boi")

                await event.client(BlockRequest(event.chat_id))
                await event.client(ReportSpamRequest(peer=event.chat_id))

                if BOTLOG:
                    name = await event.client.get_entity(event.chat_id)
                    name0 = str(name.first_name)
                    await event.client.send_message(
                        BOTLOG_CHATID,
                        "["
                        + name0
                        + "](tg://user?id="
                        + str(event.chat_id)
                        + ")"
                        + " was spamming your PM so he was blocked.",
                    )


@register(disable_edited=True, outgoing=True, disable_errors=True)
async def auto_accept(event):
    """ Will approve automatically if you texted them first. """
    if not PM_AUTO_BAN:
        return
    self_user = await event.client.get_me()
    if (
        event.is_private
        and event.chat_id != 777000
        and event.chat_id != self_user.id
        and not (await event.get_sender()).bot
    ):
        try:
            from userbot.modules.sql_helper.globals import gvarstatus
            from userbot.modules.sql_helper.pm_permit_sql import approve, is_approved
        except AttributeError:
            return

        # Use user custom unapproved message
        get_message = gvarstatus("unapproved_msg")
        UNAPPROVED_MSG = get_message if get_message is not None else DEF_UNAPPROVED_MSG
        chat = await event.get_chat()
        if isinstance(chat, User):
            if is_approved(event.chat_id) or chat.bot:
                return
            async for message in event.client.iter_messages(
                event.chat_id, reverse=True, limit=1
            ):
                if (
                    message.text is not UNAPPROVED_MSG
                    and message.sender_id == self_user.id
                ):
                    try:
                        approve(event.chat_id)
                    except IntegrityError:
                        return

                if is_approved(event.chat_id) and BOTLOG:
                    await event.client.send_message(
                        BOTLOG_CHATID,
                        "#AUTO-APPROVED\n"
                        + "User: "
                        + f"[{chat.first_name}](tg://user?id={chat.id})",
                    )


@register(outgoing=True, pattern=r"^\.notifoff$")
async def notifoff(noff_event):
    """ For .notifoff command, stop getting notifications from unapproved PMs. """
    try:
        from userbot.modules.sql_helper.globals import addgvar
    except AttributeError:
        return await noff_event.edit("**Running on Non-SQL mode!**")
    addgvar("NOTIF_OFF", True)
    await noff_event.edit("**Notifications from unapproved PMs are silenced!**")


@register(outgoing=True, pattern=r"^\.notifon$")
async def notifon(non_event):
    """ For .notifoff command, get notifications from unapproved PMs. """
    try:
        from userbot.modules.sql_helper.globals import delgvar
    except AttributeError:
        return await non_event.edit("**Running on Non-SQL mode!**")
    delgvar("NOTIF_OFF")
    await non_event.edit("**Notifications from unapproved PMs unmuted!**")


@register(outgoing=True, pattern=r"^\.approve(?:$| )(.*)")
async def approvepm(apprvpm):
    """ For .approve command, give someone the permissions to PM you. """
    try:
        from userbot.modules.sql_helper.globals import gvarstatus
        from userbot.modules.sql_helper.pm_permit_sql import approve
    except AttributeError:
        return await apprvpm.edit("**Running on Non-SQL mode!**")

    if apprvpm.reply_to_msg_id:
        reply = await apprvpm.get_reply_message()
        replied_user = await apprvpm.client.get_entity(reply.sender_id)
        uid = replied_user.id
        name0 = str(replied_user.first_name)

    elif apprvpm.pattern_match.group(1):
        inputArgs = apprvpm.pattern_match.group(1)

        try:
            inputArgs = int(inputArgs)
        except ValueError:
            pass

        try:
            user = await apprvpm.client.get_entity(inputArgs)
        except:
            return await apprvpm.edit("**Invalid username/ID.**")

        if not isinstance(user, User):
            return await apprvpm.edit("**This can be done only with users.**")

        uid = user.id
        name0 = str(user.first_name)

    else:
        aname = await apprvpm.client.get_entity(apprvpm.chat_id)
        if not isinstance(aname, User):
            return await apprvpm.edit("**This can be done only with users.**")
        name0 = str(aname.first_name)
        uid = apprvpm.chat_id

    # Get user custom msg
    getmsg = gvarstatus("unapproved_msg")
    UNAPPROVED_MSG = getmsg if getmsg is not None else DEF_UNAPPROVED_MSG
    async for message in apprvpm.client.iter_messages(
        apprvpm.chat_id, from_user="me", search=UNAPPROVED_MSG
    ):
        await message.delete()

    try:
        approve(uid)
    except IntegrityError:
        return await apprvpm.edit("**User may already be approved.**")

    await apprvpm.edit(f"[{name0}](tg://user?id={uid}) **approved to PM!**")

    if BOTLOG:
        await apprvpm.client.send_message(
            BOTLOG_CHATID,
            "#APPROVED\n" + "User: " + f"[{name0}](tg://user?id={uid})",
        )


@register(outgoing=True, pattern=r"^\.disapprove(?:$| )(.*)")
async def disapprovepm(disapprvpm):
    try:
        from userbot.modules.sql_helper.pm_permit_sql import dissprove
    except BaseException:
        return await disapprvpm.edit("**Running on Non-SQL mode!**")

    if disapprvpm.reply_to_msg_id:
        reply = await disapprvpm.get_reply_message()
        replied_user = await disapprvpm.client.get_entity(reply.sender_id)
        aname = replied_user.id
        name0 = str(replied_user.first_name)
        dissprove(aname)

    elif disapprvpm.pattern_match.group(1):
        inputArgs = disapprvpm.pattern_match.group(1)

        try:
            inputArgs = int(inputArgs)
        except ValueError:
            pass

        try:
            user = await disapprvpm.client.get_entity(inputArgs)
        except:
            return await disapprvpm.edit("**Invalid username/ID.**")

        if not isinstance(user, User):
            return await disapprvpm.edit("**This can be done only with users.**")

        aname = user.id
        dissprove(aname)
        name0 = str(user.first_name)

    else:
        dissprove(disapprvpm.chat_id)
        aname = await disapprvpm.client.get_entity(disapprvpm.chat_id)
        if not isinstance(aname, User):
            return await disapprvpm.edit("**This can be done only with users.**")
        name0 = str(aname.first_name)
        aname = aname.id

    await disapprvpm.edit(f"[{name0}](tg://user?id={aname}) **disapproved to PM!**")

    if BOTLOG:
        await disapprvpm.client.send_message(
            BOTLOG_CHATID,
            f"[{name0}](tg://user?id={aname})" " was disapproved to PM you.",
        )


@register(outgoing=True, pattern=r"^\.block$")
async def blockpm(block):
    """ For .block command, block people from PMing you! """
    if block.reply_to_msg_id:
        reply = await block.get_reply_message()
        replied_user = await block.client.get_entity(reply.sender_id)
        aname = replied_user.id
        name0 = str(replied_user.first_name)
        await block.client(BlockRequest(aname))
        await block.edit("**You've been blocked!**")
        uid = replied_user.id
    else:
        await block.client(BlockRequest(block.chat_id))
        aname = await block.client.get_entity(block.chat_id)
        if not isinstance(aname, User):
            return await block.edit("**This can be done only with users.**")
        await block.edit("**You've been blocked!**")
        name0 = str(aname.first_name)
        uid = block.chat_id

    try:
        from userbot.modules.sql_helper.pm_permit_sql import dissprove

        dissprove(uid)
    except AttributeError:
        pass

    if BOTLOG:
        await block.client.send_message(
            BOTLOG_CHATID,
            "#BLOCKED\n" + "User: " + f"[{name0}](tg://user?id={uid})",
        )


@register(outgoing=True, pattern=r"^\.unblock$")
async def unblockpm(unblock):
    """ For .unblock command, let people PMing you again! """
    if unblock.reply_to_msg_id:
        reply = await unblock.get_reply_message()
        replied_user = await unblock.client.get_entity(reply.sender_id)
        name0 = str(replied_user.first_name)
        await unblock.client(UnblockRequest(replied_user.id))
        await unblock.edit("**You have been unblocked.**")

    if BOTLOG:
        await unblock.client.send_message(
            BOTLOG_CHATID,
            f"[{name0}](tg://user?id={replied_user.id})" " was unblocc'd!.",
        )


@register(outgoing=True, pattern=r"^\.(set|get|reset) pmpermit(?: |$)(\w*)")
async def add_pmsg(cust_msg):
    """Set your own Unapproved message"""
    if not PM_AUTO_BAN:
        return await cust_msg.edit("You need to set `PM_AUTO_BAN` to `True`")
    try:
        import userbot.modules.sql_helper.globals as sql
    except AttributeError:
        await cust_msg.edit("**Running on Non-SQL mode!**")
        return

    await cust_msg.edit("**Processing...**")
    conf = cust_msg.pattern_match.group(1)

    custom_message = sql.gvarstatus("unapproved_msg")

    if conf.lower() == "set":
        message = await cust_msg.get_reply_message()
        status = "Saved"

        # check and clear user unapproved message first
        if custom_message is not None:
            sql.delgvar("unapproved_msg")
            status = "Updated"

        if not message:
            return await cust_msg.edit("**Reply to a message.**")

        # TODO: allow user to have a custom text formatting
        # eg: bold, underline, striketrough, link
        # for now all text are in monoscape
        msg = message.message  # get the plain text
        sql.addgvar("unapproved_msg", msg)
        await cust_msg.edit("**Message saved as PMPermit message.**")

        if BOTLOG:
            await cust_msg.client.send_message(
                BOTLOG_CHATID, f"***{status} PMPermit message :*** \n\n{msg}"
            )

    if conf.lower() == "reset":
        if custom_message is None:
            await cust_msg.edit("**You haven't set a custom PMPermit message yet.**")

        else:
            sql.delgvar("unapproved_msg")
            await cust_msg.edit("**PMPermit message has been reset to default.**")
    if conf.lower() == "get":
        if custom_message is not None:
            await cust_msg.edit(
                "**This is your current PMPermit message:**" f"\n\n{custom_message}"
            )
        else:
            await cust_msg.edit(
                "**You haven't set a custom PMPermit message yet.**\n"
                f"Using default message: \n\n`{DEF_UNAPPROVED_MSG}`"
            )


CMD_HELP.update(
    {
        "pmpermit": ">`.approve`"
        "\nUsage: Approves the mentioned/replied person to PM."
        "\n\n>`.disapprove`"
        "\nUsage: Disapproves the mentioned/replied person to PM."
        "\n\n>`.block`"
        "\nUsage: Blocks the person."
        "\n\n>`.unblock`"
        "\nUsage: Unblocks the person so they can PM you."
        "\n\n>`.notifoff`"
        "\nUsage: Clears/Disables any notifications of unapproved PMs."
        "\n\n>`.notifon`"
        "\nUsage: Allows notifications for unapproved PMs."
        "\n\n`.set pmpermit` <reply to msg>"
        "\nUsage: Sets a custom PMPermit message."
        "\n\n`.get pmpermit`"
        "\nUsage: Shows your current PMPermit message."
        "\n\n`.reset pmpermit`"
        "\nUsage: Resets PMPermit message to default."
    }
)
