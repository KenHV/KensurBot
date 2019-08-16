# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.b (the "License");
# you may not use this file except in compliance with the License.
"""
Userbot module to help you manage a group
"""

from asyncio import sleep
from os import remove

from telethon.errors import (BadRequestError, ChatAdminRequiredError,
                             ImageProcessFailedError, PhotoCropSizeSmallError,
                             UserAdminInvalidError)
from telethon.errors.rpcerrorlist import (UserIdInvalidError,
                                          MessageTooLongError)
from telethon.tl.functions.channels import (EditAdminRequest,
                                            EditBannedRequest,
                                            EditPhotoRequest)
from telethon.tl.functions.messages import UpdatePinnedMessageRequest
from telethon.tl.types import (ChannelParticipantsAdmins, ChatAdminRights,
                               ChatBannedRights, MessageEntityMentionName,
                               MessageMediaPhoto)

from userbot import BOTLOG, BOTLOG_CHATID, CMD_HELP, bot
from userbot.events import register

# =================== CONSTANT ===================
PP_TOO_SMOL = "`The image is too small`"
PP_ERROR = "`Failure while processing the image`"
NO_ADMIN = "`I am not an admin!`"
NO_PERM = "`I don't have sufficient permissions!`"
NO_SQL = "`Running on Non-SQL mode!`"

CHAT_PP_CHANGED = "`Chat Picture Changed`"
CHAT_PP_ERROR = "`Some issue with updating the pic,`" \
                "`maybe coz I'm not an admin,`" \
                "`or don't have enough rights.`"
INVALID_MEDIA = "`Invalid Extension`"

BANNED_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=True,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True,
)

UNBAN_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=None,
    send_media=None,
    send_stickers=None,
    send_gifs=None,
    send_games=None,
    send_inline=None,
    embed_links=None,
)

KICK_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=True
)

MUTE_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=True
)

UNMUTE_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=False
)
# ================================================

@register(outgoing=True, pattern="^.setgrouppic$")
async def set_group_photo(gpic):
    """ For .setgrouppic command, changes the picture of a group """
    if not gpic.text[0].isalpha() and gpic.text[0] not in ("/", "#", "@", "!"):
        replymsg = await gpic.get_reply_message()
        chat = await gpic.get_chat()
        admin = chat.admin_rights
        creator = chat.creator
        photo = None

        if not admin and not creator:
            await gpic.edit(NO_ADMIN)
            return

        if replymsg and replymsg.media:
            if isinstance(replymsg.media, MessageMediaPhoto):
                photo = await gpic.client.download_media(message=replymsg.photo)
            elif "image" in replymsg.media.document.mime_type.split('/'):
                photo = await gpic.client.download_file(replymsg.media.document)
            else:
                await gpic.edit(INVALID_MEDIA)

        if photo:
            try:
                await gpic.client(EditPhotoRequest(
                gpic.chat_id,
                await gpic.client.upload_file(photo)
                ))
                await gpic.edit(CHAT_PP_CHANGED)

            except PhotoCropSizeSmallError:
                await gpic.edit(PP_TOO_SMOL)
            except ImageProcessFailedError:
                await gpic.edit(PP_ERROR)


@register(outgoing=True, pattern="^.promote(?: |$)(.*)")
async def promote(promt):
    """ For .promote command, promotes the replied/tagged person """
    if not promt.text[0].isalpha() \
            and promt.text[0] not in ("/", "#", "@", "!"):
        # Get targeted chat
        chat = await promt.get_chat()
        # Grab admin status or creator in a chat
        admin = chat.admin_rights
        creator = chat.creator

        # If not admin and not creator, also return
        if not admin and not creator:
            await promt.edit(NO_ADMIN)
            return

        new_rights = ChatAdminRights(
            add_admins=False,
            invite_users=True,
            change_info=False,
            ban_users=True,
            delete_messages=True,
            pin_messages=True
        )

        await promt.edit("`Promoting...`")

        user = await get_user_from_event(promt)
        if user:
            pass
        else:
            return

        # Try to promote if current user is admin or creator
        try:
            await promt.client(
                EditAdminRequest(
                    promt.chat_id,
                    user.id,
                    new_rights
                )
            )
            await promt.edit("`Promoted Successfully!`")

        # If Telethon spit BadRequestError, assume
        # we don't have Promote permission
        except BadRequestError:
            await promt.edit(NO_PERM)
            return

        # Announce to the logging group if we have promoted successfully
        if BOTLOG:
            await promt.client.send_message(
                BOTLOG_CHATID,
                "#PROMOTE\n"
                f"USER: [{user.first_name}](tg://user?id={user.id})\n"
                f"CHAT: {promt.chat.title}(`{promt.chat_id}`)"
            )


@register(outgoing=True, pattern="^.demote(?: |$)(.*)")
async def demote(dmod):
    """ For .demote command, demotes the replied/tagged person """
    if not dmod.text[0].isalpha() and dmod.text[0] not in ("/", "#", "@", "!"):
        # Admin right check
        chat = await dmod.get_chat()
        admin = chat.admin_rights
        creator = chat.creator

        if not admin and not creator:
            await dmod.edit(NO_ADMIN)
            return

        # If passing, declare that we're going to demote
        await dmod.edit("`Demoting...`")

        user = await get_user_from_event(dmod)
        if user:
            pass
        else:
            return

        # New rights after demotion
        newrights = ChatAdminRights(
            add_admins=None,
            invite_users=None,
            change_info=None,
            ban_users=None,
            delete_messages=None,
            pin_messages=None
        )
        # Edit Admin Permission
        try:
            await dmod.client(
                EditAdminRequest(
                    dmod.chat_id,
                    user.id,
                    newrights
                )
            )

        # If we catch BadRequestError from Telethon
        # Assume we don't have permission to demote
        except BadRequestError:
            await dmod.edit(NO_PERM)
            return
        await dmod.edit("`Demoted Successfully!`")

        # Announce to the logging group if we have demoted successfully
        if BOTLOG:
            await dmod.client.send_message(
                BOTLOG_CHATID,
                "#DEMOTE\n"
                f"USER: [{user.first_name}](tg://user?id={user.id})\n"
                f"CHAT: {dmod.chat.title}(`{dmod.chat_id}`)"
            )


@register(outgoing=True, pattern="^.ban(?: |$)(.*)")
async def ban(bon):
    """ For .ban command, bans the replied/tagged person """
    if not bon.text[0].isalpha() and bon.text[0] not in ("/", "#", "@", "!"):
        # Here laying the sanity check
        chat = await bon.get_chat()
        admin = chat.admin_rights
        creator = chat.creator

        # Well
        if not admin and not creator:
            await bon.edit(NO_ADMIN)
            return

        user = await get_user_from_event(bon)
        if user:
            pass
        else:
            return


        # Announce that we're going to whack the pest
        await bon.edit("`Whacking the pest!`")

        try:
            await bon.client(
                EditBannedRequest(
                    bon.chat_id,
                    user.id,
                    BANNED_RIGHTS
                )
            )
        except BadRequestError:
            await bon.edit(NO_PERM)
            return
        # Helps ban group join spammers more easily
        try:
            reply = await bon.get_reply_message()
            if reply:
                await reply.delete()
        except BadRequestError:
            await bon.edit("`I dont have message nuking rights! But still he was banned!`")
            return
        # Delete message and then tell that the command
        # is done gracefully
        # Shout out the ID, so that fedadmins can fban later

        await bon.edit("`{}` was banned!".format(str(user.id)))

        # Announce to the logging group if we have banned the person successfully!
        if BOTLOG:
            await bon.client.send_message(
                BOTLOG_CHATID,
                "#BAN\n"
                f"USER: [{user.first_name}](tg://user?id={user.id})\n"
                f"CHAT: {bon.chat.title}(`{bon.chat_id}`)"
            )


@register(outgoing=True, pattern="^.unban(?: |$)(.*)")
async def nothanos(unbon):
    """ For .unban command, unbans the replied/tagged person """
    if not unbon.text[0].isalpha() and unbon.text[0] \
            not in ("/", "#", "@", "!"):

        # Here laying the sanity check
        chat = await unbon.get_chat()
        admin = chat.admin_rights
        creator = chat.creator

        # Well
        if not admin and not creator:
            await unbon.edit(NO_ADMIN)
            return

        # If everything goes well...
        await unbon.edit("`Unbanning...`")

        user = await get_user_from_event(unbon)
        if user:
            pass
        else:
            return

        try:
            await unbon.client(EditBannedRequest(
                unbon.chat_id,
                user.id,
                UNBAN_RIGHTS
            ))
            await unbon.edit("```Unbanned Successfully```")

            if BOTLOG:
                await unbon.client.send_message(
                    BOTLOG_CHATID,
                    "#UNBAN\n"
                    f"USER: [{user.first_name}](tg://user?id={user.id})\n"
                    f"CHAT: {unbon.chat.title}(`{unbon.chat_id}`)"
                )
        except UserIdInvalidError:
            await unbon.edit("`Uh oh my unban logic broke!`")


@register(outgoing=True, pattern="^.mute(?: |$)(.*)")
async def spider(spdr):
    """
    This function is basically muting peeps
    """
    if not spdr.text[0].isalpha() and spdr.text[0] not in ("/", "#", "@", "!"):
        # Check if the function running under SQL mode
        try:
            from userbot.modules.sql_helper.spam_mute_sql import mute
        except AttributeError:
            await spdr.edit(NO_SQL)
            return

        # Admin or creator check
        chat = await spdr.get_chat()
        admin = chat.admin_rights
        creator = chat.creator

        # If not admin and not creator, return
        if not admin and not creator:
            await spdr.edit(NO_ADMIN)
            return

        user = await get_user_from_event(spdr)
        if user:
            pass
        else:
            return

        self_user = await spdr.client.get_me()

        if user.id == self_user.id:
        	await spdr.edit("`Hands too short, can't duct tape myself...\n(ヘ･_･)ヘ┳━┳`")
        	return


        # If everything goes well, do announcing and mute
        await spdr.edit("`Gets a tape!`")
        if mute(spdr.chat_id, user.id) is False:
            return await spdr.edit('`Error! User probably already muted.`')
        else:
            try:
                await spdr.client(
                    EditBannedRequest(
                        spdr.chat_id,
                        user.id,
                        MUTE_RIGHTS
                    )
                )

                # Announce that the function is done
                await spdr.edit("`Safely taped!`")

                # Announce to logging group
                if BOTLOG:
                    await spdr.client.send_message(
                        BOTLOG_CHATID,
                        "#MUTE\n"
                        f"USER: [{user.first_name}](tg://user?id={user.id})\n"
                        f"CHAT: {spdr.chat.title}(`{spdr.chat_id}`)"
                    )
            except UserIdInvalidError:
                return await spdr.edit("`Uh oh my unmute logic broke!`")


@register(outgoing=True, pattern="^.unmute(?: |$)(.*)")
async def unmoot(unmot):
    """ For .unmute command, unmute the replied/tagged person """
    if not unmot.text[0].isalpha() and unmot.text[0] \
            not in ("/", "#", "@", "!"):

        # Admin or creator check
        chat = await unmot.get_chat()
        admin = chat.admin_rights
        creator = chat.creator

        # If not admin and not creator, return
        if not admin and not creator:
            await unmot.edit(NO_ADMIN)
            return

        # Check if the function running under SQL mode
        try:
            from userbot.modules.sql_helper.spam_mute_sql import unmute
        except AttributeError:
            await unmot.edit(NO_SQL)
            return

        # If admin or creator, inform the user and start unmuting
        await unmot.edit('```Unmuting...```')
        user = await get_user_from_event(unmot)
        if user:
            pass
        else:
            return

        if unmute(unmot.chat_id, user.id) is False:
            return await unmot.edit("`Error! User probably already unmuted.`")
        else:

            try:
                await unmot.client(
                    EditBannedRequest(
                        unmot.chat_id,
                        user.id,
                        UNBAN_RIGHTS
                    )
                )
                await unmot.edit("```Unmuted Successfully```")
            except UserIdInvalidError:
                await unmot.edit("`Uh oh my unmute logic broke!`")
                return

            if BOTLOG:
                await unmot.client.send_message(
                    BOTLOG_CHATID,
                    "#UNMUTE\n"
                    f"USER: [{user.first_name}](tg://user?id={user.id})\n"
                    f"CHAT: {unmot.chat.title}(`{unmot.chat_id}`)"
                )


@register(incoming=True)
async def muter(moot):
    """ Used for deleting the messages of muted people """
    try:
        from userbot.modules.sql_helper.spam_mute_sql import is_muted
        from userbot.modules.sql_helper.gmute_sql import is_gmuted
    except AttributeError:
        return
    muted = is_muted(moot.chat_id)
    gmuted = is_gmuted(moot.sender_id)
    rights = ChatBannedRights(
        until_date=None,
        send_messages=True,
        send_media=True,
        send_stickers=True,
        send_gifs=True,
        send_games=True,
        send_inline=True,
        embed_links=True,
    )
    if muted:
        for i in muted:
            if str(i.sender) == str(moot.sender_id):
                await moot.delete()
                await moot.client(EditBannedRequest(
                    moot.chat_id,
                    moot.sender_id,
                    rights
                ))
    for i in gmuted:
        if i.sender == str(moot.sender_id):
            await moot.delete()


@register(outgoing=True, pattern="^.ungmute(?: |$)(.*)")
async def ungmoot(un_gmute):
    """ For .ungmute command, ungmutes the target in the userbot """
    if not un_gmute.text[0].isalpha() and un_gmute.text[0] \
            not in ("/", "#", "@", "!"):
        # Admin or creator check
        chat = await un_gmute.get_chat()
        admin = chat.admin_rights
        creator = chat.creator

        # If not admin and not creator, return
        if not admin and not creator:
            await un_gmute.edit(NO_ADMIN)
            return

        # Check if the function running under SQL mode
        try:
            from userbot.modules.sql_helper.gmute_sql import ungmute
        except AttributeError:
            await un_gmute.edit(NO_SQL)
            return

        user = await get_user_from_event(un_gmute)
        if user:
            pass
        else:
            return

        # If pass, inform and start ungmuting
        await un_gmute.edit('```Ungmuting...```')

        if ungmute(user.id) is False:
            await un_gmute.edit("`Error! User probably not gmuted.`")
        else:
            # Inform about success
            await un_gmute.edit("```Ungmuted Successfully```")

            if BOTLOG:
                await un_gmute.client.send_message(
                    BOTLOG_CHATID,
                    "#UNGMUTE\n"
                    f"USER: [{user.first_name}](tg://user?id={user.id})\n"
                    f"CHAT: {un_gmute.chat.title}(`{un_gmute.chat_id}`)"
                )


@register(outgoing=True, pattern="^.gmute(?: |$)(.*)")
async def gspider(gspdr):
    """ For .gmute command, globally mutes the replied/tagged person """
    if not gspdr.text[0].isalpha() and gspdr.text[0] not in ("/", "#", "@", "!"):
        # Admin or creator check
        chat = await gspdr.get_chat()
        admin = chat.admin_rights
        creator = chat.creator

        # If not admin and not creator, return
        if not admin and not creator:
            await gspdr.edit(NO_ADMIN)
            return

        # Check if the function running under SQL mode
        try:
            from userbot.modules.sql_helper.gmute_sql import gmute
        except AttributeError:
            await gspdr.edit(NO_SQL)
            return

        user = await get_user_from_event(gspdr)
        if user:
            pass
        else:
            return


        # If pass, inform and start gmuting
        await gspdr.edit("`Grabs a huge, sticky duct tape!`")
        if gmute(user.id) is False:
            await gspdr.edit('`Error! User probably already gmuted.\nRe-rolls the tape.`')
        else:
            await gspdr.edit("`Globally taped!`")

            if BOTLOG:
                await gspdr.client.send_message(
                    BOTLOG_CHATID,
                    "#GMUTE\n"
                    f"USER: [{user.first_name}](tg://user?id={user.id})\n"
                    f"CHAT: {gspdr.chat.title}(`{gspdr.chat_id}`)"
                )


@register(outgoing=True, pattern="^.delusers(?: |$)(.*)")
async def rm_deletedacc(show):
    """ For .delusers command, list all the ghost/deleted accounts in a chat. """
    if not show.text[0].isalpha() and show.text[0] not in ("/", "#", "@", "!"):
        con = show.pattern_match.group(1)
        del_u = 0
        del_status = "`No deleted accounts found, Group is cleaned as Hell`"

        if not show.is_group:
            await show.edit("`This command is only for groups!`")
            return

        if con != "clean":
            await show.edit("`Searching for zombie accounts...`")
            async for user in show.client.iter_participants(
                    show.chat_id
            ):
                if user.deleted:
                    del_u += 1

            if del_u > 0:
                del_status = f"found **{del_u}** deleted account(s) in this group \
                \nclean them by using .delusers clean"
            await show.edit(del_status)
            return

        # Here laying the sanity check
        chat = await show.get_chat()
        admin = chat.admin_rights
        creator = chat.creator

        # Well
        if not admin and not creator:
            await show.edit("`I am not an admin here!`")
            return

        await show.edit("`Deleting deleted accounts...\nOh I can do that?!?!`")
        del_u = 0
        del_a = 0

        async for user in show.client.iter_participants(
                show.chat_id
        ):
            if user.deleted:
                try:
                    await show.client(
                        EditBannedRequest(
                            show.chat_id,
                            user.id,
                            BANNED_RIGHTS
                        )
                    )
                except ChatAdminRequiredError:
                    await show.edit("`I don't have ban rights in this group`")
                    return
                except UserAdminInvalidError:
                    del_u -= 1
                    del_a += 1
                await show.client(
                    EditBannedRequest(
                        show.chat_id,
                        user.id,
                        UNBAN_RIGHTS
                    )
                )
                del_u += 1

        if del_u > 0:
            del_status = f"cleaned **{del_u}** deleted account(s)"

        if del_a > 0:
            del_status = f"cleaned **{del_u}** deleted account(s) \
            \n**{del_a}** deleted admin accounts are not removed"

        await show.edit(del_status)


@register(outgoing=True, pattern="^.adminlist$")
async def get_admin(show):
    """ For .adminlist command, list all of the admins of the chat. """
    if not show.text[0].isalpha() and show.text[0] not in ("/", "#", "@", "!"):
        if not show.is_group:
            await show.edit("I don't think this is a group.")
            return
        info = await show.client.get_entity(show.chat_id)
        title = info.title if info.title else "this chat"
        mentions = f'<b>Admins in {title}:</b> \n'
        try:
            async for user in show.client.iter_participants(
                    show.chat_id, filter=ChannelParticipantsAdmins
            ):
                if not user.deleted:
                    link = f"<a href=\"tg://user?id={user.id}\">{user.first_name}</a>"
                    userid = f"<code>{user.id}</code>"
                    mentions += f"\n{link} {userid}"
                else:
                    mentions += f"\nDeleted Account <code>{user.id}</code>"
        except ChatAdminRequiredError as err:
            mentions += " " + str(err) + "\n"
        await show.edit(mentions, parse_mode="html")


@register(outgoing=True, pattern="^.pin(?: |$)(.*)")
async def pin(msg):
    """ For .pin command, pins the replied/tagged message on the top the chat. """
    if not msg.text[0].isalpha() and msg.text[0] not in ("/", "#", "@", "!"):
        # Admin or creator check
        chat = await msg.get_chat()
        admin = chat.admin_rights
        creator = chat.creator

        # If not admin and not creator, return
        if not admin and not creator:
            await msg.edit(NO_ADMIN)
            return

        to_pin = msg.reply_to_msg_id

        if not to_pin:
            await msg.edit("`Reply to a message to pin it.`")
            return

        options = msg.pattern_match.group(1)

        is_silent = True

        if options.lower() == "loud":
            is_silent = False

        try:
            await msg.client(UpdatePinnedMessageRequest(msg.to_id, to_pin, is_silent))
        except BadRequestError:
            await msg.edit(NO_PERM)
            return

        await msg.edit("`Pinned Successfully!`")

        user = await get_user_from_id(msg.from_id, msg)

        if BOTLOG:
            await msg.client.send_message(
                BOTLOG_CHATID,
                "#PIN\n"
                f"ADMIN: [{user.first_name}](tg://user?id={user.id})\n"
                f"CHAT: {msg.chat.title}(`{msg.chat_id}`)\n"
                f"LOUD: {not is_silent}"
            )


@register(outgoing=True, pattern="^.kick(?: |$)(.*)")
async def kick(usr):
    """ For .kick command, kicks the replied/tagged person from the group. """
    if not usr.text[0].isalpha() and usr.text[0] not in ("/", "#", "@", "!"):
        # Admin or creator check
        chat = await usr.get_chat()
        admin = chat.admin_rights
        creator = chat.creator

        # If not admin and not creator, return
        if not admin and not creator:
            await usr.edit(NO_ADMIN)
            return

        user = await get_user_from_event(usr)
        if not user:
            await usr.edit("`Couldn't fetch user.`")
            return


        await usr.edit("`Kicking...`")

        try:
            await usr.client(
                EditBannedRequest(
                    usr.chat_id,
                    user.id,
                    KICK_RIGHTS
                )
            )
            await sleep(.5)
        except BadRequestError:
            await usr.edit(NO_PERM)
            return
        await usr.client(
            EditBannedRequest(
                usr.chat_id,
                user.id,
                ChatBannedRights(until_date=None)
            )
        )

        await usr.edit(f"`Kicked` [{user.first_name}](tg://user?id={user.id})`!`")

        if BOTLOG:
            await usr.client.send_message(
                BOTLOG_CHATID,
                "#KICK\n"
                f"USER: [{user.first_name}](tg://user?id={user.id})\n"
                f"CHAT: {usr.chat.title}(`{usr.chat_id}`)\n"
            )


@register(outgoing=True, pattern="^.userslist ?(.*)")
async def get_users(show):
    """ For .userslist command, list all of the users in a chat. """
    if not show.text[0].isalpha() and show.text[0] not in ("/", "#", "@", "!"):
        if not show.is_group:
            await show.edit("Are you sure this is a group?")
            return
        info = await show.client.get_entity(show.chat_id)
        title = info.title if info.title else "this chat"
        mentions = 'Users in {}: \n'.format(title)
        try:
            if not show.pattern_match.group(1):
                async for user in show.client.iter_participants(show.chat_id):
                    if not user.deleted:
                        mentions += f"\n[{user.first_name}](tg://user?id={user.id}) `{user.id}`"
                    else:
                        mentions += f"\nDeleted Account `{user.id}`"
            else:
                searchq = show.pattern_match.group(1)
                async for user in show.client.iter_participants(show.chat_id, search=f'{searchq}'):
                    if not user.deleted:
                        mentions += f"\n[{user.first_name}](tg://user?id={user.id}) `{user.id}`"
                    else:
                        mentions += f"\nDeleted Account `{user.id}`"
        except ChatAdminRequiredError as err:
            mentions += " " + str(err) + "\n"
        try:
            await show.edit(mentions)
        except MessageTooLongError:
            await show.edit("Damn, this is a huge group. Uploading users lists as file.")
            file = open("userslist.txt", "w+")
            file.write(mentions)
            file.close()
            await show.client.send_file(
                show.chat_id,
                "userslist.txt",
                caption='Users in {}'.format(title),
                reply_to=show.id,
            )
            remove("userslist.txt")


async def get_user_from_event(event):
    """ Get the user from argument or replied message. """
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        user_obj = await event.client.get_entity(previous_message.from_id)
    else:
        user = event.pattern_match.group(1)

        if user.isnumeric():
            user = int(user)

        if not user:
            await event.edit("`Pass the user's username, id or reply!`")
            return

        if event.message.entities is not None:
            probable_user_mention_entity = event.message.entities[0]

            if isinstance(probable_user_mention_entity, MessageEntityMentionName):
                user_id = probable_user_mention_entity.user_id
                user_obj = await event.client.get_entity(user_id)
                return user_obj
        try:
            user_obj = await event.client.get_entity(user)
        except (TypeError, ValueError) as err:
            await event.edit(str(err))
            return None

    return user_obj

async def get_user_from_id(user, event):
    if isinstance(user, str):
        user = int(user)

    try:
        user_obj = await event.client.get_entity(user)
    except (TypeError, ValueError) as err:
        await event.edit(str(err))
        return None

    return user_obj

CMD_HELP.update({
    "admin": ".promote\
\nUsage: Reply to someone's message with .promote to promote them.\
\n\n.demote\
\nUsage: Reply to someone's message with .demote to revoke their admin permissions.\
\n\n.ban\
\nUsage: Reply to someone's message with .ban to ban them.\
\n\n.unban\
\nUsage: Reply to someone's message with .unban to unban them in this chat.\
\n\n.mute\
\nUsage: Reply to someone's message with .mute to mute them, works on admins too.\
\n\n.unmute\
\nUsage: Reply to someone's message with .unmute to remove them from muted list.\
\n\n.gmute\
\nUsage: Reply to someone's message with .gmute to mute them in all groups you have in common with them.\
\n\n.ungmute\
\nUsage: Reply someone's message with .ungmute to remove them from the gmuted list.\
\n\n.delusers\
\nUsage: Searches for deleted accounts in a group. Use .delusers clean to remove deleted accounts from the group.\
\n\n.adminlist\
\nUsage: Retrieves all admins in a chat.\
\n\n.userslist or .userslist <name>\
\nUsage: Retrieves all users in a chat."
})
