# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module which contains afk-related commands """

import random

from asyncio import sleep

from telethon.events import StopPropagation

from userbot import (
    AFKREASON,
    COUNT_MSG,
    CMD_HELP,
    ISAFK,
    BOTLOG,
    BOTLOG_CHATID,
    USERS,
    PM_AUTO_BAN)

from userbot.events import register, errors_handler

# ========================= CONSTANTS ============================
AFKSTR = [
    "I'm busy right now. Please talk in a bag and when I come back you can just give me the bag!",
    "I'm away right now. If you need anything, leave a message after the beep:\n`beeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeep`!",
    "You missed me, next time aim better.",
    "I'll be back in a few minutes and if I'm not...,\nwait longer.",
    "I'm not here right now, so I'm probably somewhere else.",
    "Roses are red,\nViolets are blue,\nLeave me a message,\nAnd I'll get back to you.",
    "Sometimes the best things in life are worth waiting for…\nI`ll be right back.",
    "I'll be right back,\nbut if I'm not right back,\nI'll be back later.",
    "If you haven't figured it out already,\nI'm not here.",
    "Hello, welcome to my away message, how may I ignore you today?",
    "I'm away over 7 seas and 7 countries,\n7 waters and 7 continents,\n7 mountains and 7 hills,\n7 plains and 7 mounds,\n7 pools and 7 lakes,\n7 springs and 7 meadows,\n7 cities and 7 neighborhoods,\n7 blocks and 7 houses...\n\nWhere not even your messages can reach me!",
    "I'm away from the keyboard at the moment, but if you'll scream loud enough at your screen, I might just hear you.",
    "I went that way\n---->",
    "I went this way\n<----",
    "Please leave a message and make me feel even more important than I already am.",
    "I am not here so stop writing to me,\nor else you will find yourself with a screen full of your own messages.",
    "If I were here,\nI'd tell you where I am.\n\nBut I'm not,\nso ask me when I return...",
    "I am away!\nI don't know when I'll be back!\nHopefully a few minutes from now!",
    "I'm not available right now so please leave your name, number, and address and I will stalk you later.",
    "Sorry, I'm not here right now.\nFeel free to talk to my userbot as long as you like.\nI'll get back to you later.",
    "I bet you were expecting an away message!",
    "Life is so short, there are so many things to do...\nI'm away doing one of them..",
    "I am not here right now...\nbut if I was...\n\nwouldn't that be awesome?",
]
# =================================================================


@register(incoming=True, disable_edited=True)
@errors_handler
async def mention_afk(mention):
    """ This function takes care of notifying the people who mention you that you are AFK."""
    global COUNT_MSG
    global USERS
    global ISAFK
    if mention.message.mentioned and not (await mention.get_sender()).bot:
        if ISAFK:
            if mention.sender_id not in USERS:
                if AFKREASON:
                    await mention.reply(
                        f"Sorry! I am AFK because of `{AFKREASON}`. I'll have a look at this as soon as I come back."
                    )
                else:
                    await mention.reply(
                        str(random.choice(AFKSTR))
                    )
                USERS.update({mention.sender_id: 1})
                COUNT_MSG = COUNT_MSG + 1
            elif mention.sender_id in USERS:
                if USERS[mention.sender_id] % 2 == 0:
                    if AFKREASON:
                        await mention.reply(
                            f"Sorry! But I'm still not back yet. Currently busy with `{AFKREASON}`."
                        )
                    else:
                        await mention.reply(
                            str(random.choice(AFKSTR))
                        )
                    USERS[mention.sender_id] = USERS[mention.sender_id] + 1
                    COUNT_MSG = COUNT_MSG + 1
                else:
                    USERS[mention.sender_id] = USERS[mention.sender_id] + 1
                    COUNT_MSG = COUNT_MSG + 1


@register(incoming=True)
@errors_handler
async def afk_on_pm(sender):
    """ Function which informs people that you are AFK in PM """
    global ISAFK
    global USERS
    global COUNT_MSG
    if sender.is_private and sender.sender_id != 777000 and not (await sender.get_sender()).bot:
        if PM_AUTO_BAN:
            try:
                from userbot.modules.sql_helper.pm_permit_sql import is_approved
                apprv = is_approved(sender.sender_id)
            except AttributeError:
                apprv = True
        else:
            apprv = True
        if apprv and ISAFK:
            if sender.sender_id not in USERS:
                if AFKREASON:
                    await sender.reply(
                        f"Sorry! I am AFK due to `{AFKREASON}`. I'll respond as soon I come back."
                    )
                else:
                    await sender.reply(
                        str(random.choice(AFKSTR))
                    )
                USERS.update({sender.sender_id: 1})
                COUNT_MSG = COUNT_MSG + 1
            elif apprv and sender.sender_id in USERS:
                if USERS[sender.sender_id] % 2 == 0:
                    if AFKREASON:
                        await sender.reply(
                            f"Sorry! But I'm still not back yet. Currently busy with `{AFKREASON}`."
                        )
                    else:
                        await sender.reply(
                            str(random.choice(AFKSTR))
                        )
                    USERS[sender.sender_id] = USERS[sender.sender_id] + 1
                    COUNT_MSG = COUNT_MSG + 1
                else:
                    USERS[sender.sender_id] = USERS[sender.sender_id] + 1
                    COUNT_MSG = COUNT_MSG + 1


@register(outgoing=True, pattern="^.afk")
async def set_afk(afk_e):
    """ For .afk command, allows you to inform people that you are afk when they message you """
    if not afk_e.text[0].isalpha() and afk_e.text[0] not in (
            "/", "#", "@", "!"):
        message = afk_e.text
        string = str(message[5:])
        global ISAFK
        global AFKREASON
        await afk_e.edit("Going AFK !!")
        if string != "":
            AFKREASON = string
        if BOTLOG:
            await afk_e.client.send_message(BOTLOG_CHATID, "You went AFK!")
        ISAFK = True
        raise StopPropagation


@register(outgoing=True)
@errors_handler
async def type_afk_is_not_true(notafk):
    """ This sets your status as not afk automatically when you write something while being afk """
    global ISAFK
    global COUNT_MSG
    global USERS
    global AFKREASON
    if ISAFK:
        ISAFK = False
        await notafk.respond("I'm no longer AFK.")
        sleep(2)
        if BOTLOG:
            await notafk.client.send_message(
                BOTLOG_CHATID,
                "You've recieved " +
                str(COUNT_MSG) +
                " messages from " +
                str(len(USERS)) +
                " chats while you were away",
            )
            for i in USERS:
                name = await notafk.client.get_entity(i)
                name0 = str(name.first_name)
                await notafk.client.send_message(
                    BOTLOG_CHATID,
                    "[" +
                    name0 +
                    "](tg://user?id=" +
                    str(i) +
                    ")" +
                    " sent you " +
                    "`" +
                    str(USERS[i]) +
                    " messages`",
                )
        COUNT_MSG = 0
        USERS = {}
        AFKREASON = None

CMD_HELP.update({
    "afk": ".afk [Optional Reason]\
\nUsage: Sets you as afk.\nReplies to anyone who tags/PM's \
you telling them that you are AFK(reason).\n\nSwitches off AFK when you type back anything, anywhere.\
"})
