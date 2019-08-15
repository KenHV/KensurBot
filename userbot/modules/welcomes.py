from telethon.utils import pack_bot_file_id
from userbot.events import register
from userbot import CMD_HELP, bot, LOGS, CLEAN_WELCOME
from telethon.events import ChatAction


@bot.on(ChatAction)
async def welcome_to_chat(event):
    
    try:
        from userbot.modules.sql_helper.welcome_sql import get_current_welcome_settings
        from userbot.modules.sql_helper.welcome_sql import update_previous_welcome
    except AttributeError:
        return
    
    cws = get_current_welcome_settings(event.chat_id)
    if cws:
        """user_added=True,
        user_joined=True,
        user_left=False,
        user_kicked=False,"""
        if (event.user_joined or event.user_added) and not (await event.get_user()).bot:
            if CLEAN_WELCOME:
                try:
                    await event.client.delete_messages(
                        event.chat_id,
                        cws.previous_welcome
                    )
                except Exception as e:
                    LOGS.warn(str(e))

            a_user = await event.get_user()
            chat = await event.get_chat()
            me = await event.client.get_me()

            title = chat.title if chat.title else "this chat"

            participants = await event.client.get_participants(chat)
            count = len(participants)

            current_saved_welcome_message = cws.custom_welcome_message

            mention = "[{}](tg://user?id={})".format(a_user.first_name, a_user.id)
            my_mention = "[{}](tg://user?id={})".format(me.first_name, me.id)

            first = a_user.first_name
            last = a_user.last_name
            if last:
                fullname = f"{first} {last}"
            else:
                fullname = first

            username = f"@{a_user.username}" if a_user.username else mention

            userid = a_user.id

            my_first = me.first_name
            my_last = me.last_name
            if my_last:
                my_fullname = f"{my_first} {my_last}"
            else:
                my_fullname = my_first

            my_username = f"@{me.username}" if me.username else my_mention

            current_message = await event.reply(
                current_saved_welcome_message.format(mention=mention,
                                                     title=title,
                                                     count=count,
                                                     first=first,
                                                     last=last,
                                                     fullname=fullname,
                                                     username=username,
                                                     userid=userid,
                                                     my_first=my_first,
                                                     my_last=my_last,
                                                     my_fullname=my_fullname,
                                                     my_username=my_username,
                                                     my_mention=my_mention),
                file=cws.media_file_id
            )
            
            update_previous_welcome(event.chat_id, current_message.id)


@register(outgoing=True, pattern=r"^.welcome(?: |$)(.*)")
async def save_welcome(event):
    if not event.text[0].isalpha() and event.text[0] not in ("/", "#", "@", "!"):
        try:
            from userbot.modules.sql_helper.welcome_sql import add_welcome_setting
        except AttributeError:
            await event.edit("`Running on Non-SQL mode!`")
            return
        
        msg = await event.get_reply_message()
        input_str = event.pattern_match.group(1)
        if input_str:
            if add_welcome_setting(event.chat_id, input_str, 0) is True:
                await event.edit("`Welcome note saved !!`")
            else:
                await event.edit("`I can only have one welcome note per chat !!`")
        elif msg and msg.media:
            bot_api_file_id = pack_bot_file_id(msg.media)
            if add_welcome_setting(event.chat_id, msg.message, 0, bot_api_file_id) is True:
                await event.edit("`Welcome note saved !!`")
            else:
                await event.edit("`I can only have one welcome note per chat !!`")
        elif msg.message is not None:
            if add_welcome_setting(event.chat_id, msg.message, 0) is True:
                await event.edit("`Welcome note saved !!`")
            else:
                await event.edit("`I can only have one welcome note per chat !!`")


@register(outgoing=True, pattern="^.show welcome$")
async def show_welcome(event):
    if not event.text[0].isalpha() and event.text[0] not in ("/", "#", "@", "!"):
        try:
            from userbot.modules.sql_helper.welcome_sql import get_current_welcome_settings
        except AttributeError:
            await event.edit("`Running on Non-SQL mode!`")
            return
        
        cws = get_current_welcome_settings(event.chat_id)
        if cws:
            await event.edit(f"`The current welcome message is:`\n{cws.custom_welcome_message}")
        else:
            await event.edit("`No welcome note saved here !!`")

@register(outgoing=True, pattern="^.del welcome$")
async def del_welcome(event):
    if not event.text[0].isalpha() and event.text[0] not in ("/", "#", "@", "!"):
        try:
            from userbot.modules.sql_helper.welcome_sql import rm_welcome_setting
        except AttributeError:
            await event.edit("`Running on Non-SQL mode!`")
            return
        
        if rm_welcome_setting(event.chat_id) is True:
            await event.edit("`Welcome note deleted for this chat.`")
        else:
            await event.edit("`Do I even have a welcome note here ?`")


CMD_HELP.update({
    "welcome": "\
.welcome <notedata/reply>\
\nUsage: Saves notedata / replied message as a welcome note in the chat.\
\n\nAvailable variables for formatting welcome messages : \
\n`{mention}, {title}, {count}, {first}, {last}, {fullname}, {userid}, {username}, {my_first}, {my_fullname}, {my_last}, {my_mention}, {my_username}`\
\n\n.show welcome\
\nUsage: Gets your current welcome message in the chat.\
\n\n.del welcome\
\nUsage: Deletes the welcome note for the current chat.\
"})
