# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# From UniBorg by @Spechide

""" Userbot module containing commands for keeping global notes. """

from telethon import utils
from telethon.tl import types
from userbot.events import register, errors_handler
from userbot import CMD_HELP


TYPE_TEXT = 0
TYPE_PHOTO = 1
TYPE_DOCUMENT = 2


@register(outgoing=True, pattern=r"\$\w*")
@errors_handler
async def on_snip(event):
    """ Snips logic. """
    try:
        from userbot.modules.sql_helper.snips_sql import get_snip
    except AttributeError:
        return
    name = event.text[1:]
    snip = get_snip(name)
    if snip:
        if snip.snip_type == TYPE_PHOTO:
            media = types.InputPhoto(
                int(snip.media_id),
                int(snip.media_access_hash),
                snip.media_file_reference
            )
        elif snip.snip_type == TYPE_DOCUMENT:
            media = types.InputDocument(
                int(snip.media_id),
                int(snip.media_access_hash),
                snip.media_file_reference
            )
        else:
            media = None

        message_id_to_reply = event.message.reply_to_msg_id

        if not message_id_to_reply:
            message_id_to_reply = None

        await event.client.send_message(
            event.chat_id,
            snip.reply,
            reply_to=message_id_to_reply,
            file=media
        )
        await event.delete()


@register(outgoing=True, pattern="^.snip (.*)")
@errors_handler
async def on_snip_save(event):
    """ For .snip command, saves snips for future use. """
    try:
        from userbot.modules.sql_helper.snips_sql import add_snip
    except AtrributeError:
        await event.edit("`Running on Non-SQL mode!`")
        return
    name = event.pattern_match.group(1)
    msg = await event.get_reply_message()
    if not msg:
        await event.edit("`I need something to save as a snip.`")
        return
    else:
        snip = {'type': TYPE_TEXT, 'text': msg.message or ''}
        if msg.media:
            media = None
            if isinstance(msg.media, types.MessageMediaPhoto):
                media = utils.get_input_photo(msg.media.photo)
                snip['type'] = TYPE_PHOTO
            elif isinstance(msg.media, types.MessageMediaDocument):
                media = utils.get_input_document(msg.media.document)
                snip['type'] = TYPE_DOCUMENT
            if media:
                snip['id'] = media.id
                snip['hash'] = media.access_hash
                snip['fr'] = media.file_reference

        success = "`Snip {} successfully. Use` **${}** `anywhere to get it`"

        if add_snip(
                name,
                snip['text'],
                snip['type'],
                snip.get('id'),
                snip.get('hash'),
                snip.get('fr')) is False:
            await event.edit(success.format('updated', name))
        else:
            await event.edit(success.format('saved', name))


@register(outgoing=True, pattern="^.snips$")
@errors_handler
async def on_snip_list(event):
    """ For .snips command, lists snips saved by you. """
    if not event.text[0].isalpha() and event.text[0] not in (
            "/", "#", "@", "!"):
        try:
            from userbot.modules.sql_helper.snips_sql import get_snips
        except AttributeError:
            await event.edit("`Running on Non-SQL mode!`")
            return

        message = "`No snips available right now.`"
        all_snips = get_snips()
        for a_snip in all_snips:
            if message == "`No snips available right now.`":
                message = "Available snips:\n"
                message += f"- `${a_snip.snip}`\n"
            else:
                message += f"- `${a_snip.snip}`\n"

        await event.edit(message)


@register(outgoing=True, pattern="^.remsnip (.*)")
@errors_handler
async def on_snip_delete(event):
    """ For .remsnip command, deletes a snip. """
    try:
        from userbot.modules.sql_helper.snips_sql import remove_snip
    except AttributeError:
        await event.edit("`Running on Non-SQL mode!`")
        return
    name = event.pattern_match.group(1)
    if remove_snip(name) is True:
        await event.edit(f"`Successfully deleted snip:` **{name}**")
    else:
        await event.edit(f"`Couldn't find snip:` **{name}**")

CMD_HELP.update({
    "snips": "\
$<snip_name>\
\nUsage: Gets the specified snip.\
\n\n.snip <name>\
\nUsage: Saves the replied message as a snip with the name. (Works with pics, docs, and stickers too!)\
\n\n.snips\
\nUsage: Gets all saved snips.\
\n\n.remsnip <snip_name>\
\nUsage: Deletes the specified snip.\
"})
