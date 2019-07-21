# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.b (the "License");
# you may not use this file except in compliance with the License.
#

""" Userbot module containing commands for keeping notes. """

from userbot import BOTLOG, BOTLOG_CHATID, CMD_HELP
from userbot.events import register


@register(outgoing=True, pattern="^.saved$")
async def notes_active(svd):
    """ For .saved command, list all of the notes saved in a chat. """
    if not svd.text[0].isalpha() and svd.text[0] not in ("/", "#", "@", "!"):
        try:
            from userbot.modules.sql_helper.notes_sql import get_notes
        except AttributeError:
            await svd.edit("`Running on Non-SQL mode!`")
            return
        
        message = "`There are no saved notes in this chat`"
        notes = get_notes(svd.chat_id)
        for note in notes:
            if message == "`There are no saved notes in this chat`":
                message = "Notes saved in this chat:\n"
                message += "🗒️ `{}`\n".format(note["name"])
            else:
                message += "🗒️ `{}`\n".format(note["name"])

        await svd.edit(message)

        
@register(outgoing=True, pattern=r"^.clear (\w*)")
async def remove_notes(clr):
    """ For .clear command, clear note with the given name."""
    if not clr.text[0].isalpha() and clr.text[0] not in ("/", "#", "@", "!"):
        try:
            from userbot.modules.sql_helper.notes_sql import rm_note
        except AttributeError:
            await clr.edit("`Running on Non-SQL mode!`")
            return
        notename = clr.pattern_match.group(1)
        if rm_note(clr.chat_id, notename) is False:
            return await clr.edit("`Couldn't find note:` **{}**"
                                  .format(notename))
        else:
            return await clr.edit("`Successfully deleted note:` **{}**"
                                  .format(notename))
        
        
@register(outgoing=True, pattern=r"^.save (\w*)")
async def add_filter(fltr):
    """ For .save command, saves notes in a chat. """
    if not fltr.text[0].isalpha() and fltr.text[0] not in ("/", "#", "@", "!"):
        try:
            from userbot.modules.sql_helper.notes_sql import add_note
        except AttributeError:
            await fltr.edit("`Running on Non-SQL mode!`")
            return

        notename = fltr.pattern_match.group(1)
        string = fltr.text.partition(notename)[2]
        if fltr.reply_to_msg_id:
            string = " " + (await fltr.get_reply_message()).text
            
        msg = "`Note {} successfully. Use` #{} `to get it`"
        if add_note(str(fltr.chat_id), notename, string) is False:
            return await fltr.edit(msg.format('updated', notename))
        else:
            return await fltr.edit(msg.format('added', notename))


@register(pattern=r"#\w*", disable_edited=True)
async def incom_note(getnt):
    """ Notes logic. """
    try:
        if not (await getnt.get_sender()).bot:
            try:
                from userbot.modules.sql_helper.notes_sql import get_notes
            except AttributeError:
                return
            notename = getnt.text[1:]
            notes = get_notes(getnt.chat_id)
            for note in notes:
                if notename == note.keyword:
                    await getnt.reply(note.reply)
                    return
    except AttributeError:
        pass

@register(outgoing=True, pattern="^.rmnotes (.*)")
async def kick_marie_notes(kick):
    """ For .rmfilters command, allows you to kick all \
        Marie(or her clones) filters from a chat. """
    if not kick.text[0].isalpha() and kick.text[0] not in ("/", "#", "@", "!"):
        bot_type = kick.pattern_match.group(1)
        if bot_type not in ["marie", "rose"]:
            await kick.edit("`That bot is not yet supported!`")
            return
        await kick.edit("```Will be kicking away all Notes!```")
        await sleep(3)
        resp = await kick.get_reply_message()
        filters = resp.text.split("-")[1:]
        for i in filters:
            if bot_type == "marie":
                await kick.reply("/clear %s" % (i.strip()))
            if bot_type == "rose":
                i = i.replace('`', '')
                await kick.reply("/clear %s" % (i.strip()))
            await sleep(0.3)
        await kick.respond(
            "```Successfully purged bots notes yaay!```\n Gimme cookies!"
        )
        if BOTLOG:
            await kick.client.send_message(
                BOTLOG_CHATID, "I cleaned all Notes at " +
                               str(kick.chat_id)
            )

CMD_HELP.update({
    "notes": "\
#<notename>\
\nUsage: Gets the note with name notename\
\n\n.save <notename> <notedata>\
\nUsage: Saves notedata as a note with the name notename\
\n\n.clear <notename>\
\nUsage: Deletes the note with name notename.\
"})
