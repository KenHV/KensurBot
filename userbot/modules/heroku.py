# Copyright (C) 2020 Adek Maulana.
# All rights reserved.
"""
   Heroku manager for your userbot
"""

import heroku3
import asyncio
import requests
import math

from userbot import (
    CMD_HELP,
    HEROKU_APP_NAME,
    HEROKU_API_KEY,
    BOTLOG,
    BOTLOG_CHATID
)

from userbot.events import register

Heroku = heroku3.from_key(HEROKU_API_KEY)
heroku_api = "https://api.heroku.com"


@register(outgoing=True, pattern=r"^.(set|get|del) var(?: |$)(.*)(?: |$)([\s\S]*)")
async def variable(var):
    """
        Manage most of ConfigVars setting, set new var, get current var,
        or delete var...
    """
    if HEROKU_APP_NAME is not None:
        app = Heroku.app(HEROKU_APP_NAME)
    else:
        return await var.edit("`[HEROKU]:"
                              "\nPlease setup your` **HEROKU_APP_NAME**.")
    exe = var.pattern_match.group(1)
    heroku_var = app.config()
    if exe == "get":
        await var.edit("`Getting information...`")
        try:
            variable = var.pattern_match.group(2).split()[0]
            if variable in heroku_var:
                if BOTLOG:
                    await var.client.send_message(
                        BOTLOG_CHATID, "#CONFIGVAR\n\n"
                        "**ConfigVar**:\n"
                        " -> `Config Variable`:\n"
                        f"     • `{variable}`\n"
                        " -> `Value`:\n"
                        f"     • `{heroku_var[variable]}`\n"
                    )
                    return await var.edit("`Received information to BOTLOG_CHATID`.")
                else:
                    return await var.edit("`Can't get information, set BOTLOG to True`.")
            else:
                if BOTLOG:
                    await var.client.send_message(
                        BOTLOG_CHATID, "#CONFIGVAR\n\n"
                        "**ConfigVar**:\n"
                        " -> `Config Variable`:\n"
                        f"     • `{variable}`\n"
                        " -> `Value`:\n"
                        "     • `ConfigVariable don't exists`\n"
                    )
                    return await var.edit("`Empty information...`")
        except IndexError:
            configvars = heroku_var.to_dict()
            msg = ''
            if BOTLOG:
                for item in configvars:
                    msg += f" • `{item}` **=** `{configvars[item]}`\n"
                await var.client.send_message(
                    BOTLOG_CHATID, "#CONFIGVARS\n\n"
                    "**ConfigVars**:\n"
                    f"{msg}"
                )
                return await var.edit("`Received information to BOTLOG_CHATID`.")
            else:
                return await var.edit("`Can't get information, set BOTLOG to True`.")
    elif exe == "set":
        await var.edit("`Setting information...`")
        variable = var.pattern_match.group(2)
        if not variable:
            return await var.edit(">`.set var <ConfigVars-name> <value>`")
        value = var.pattern_match.group(3)
        if not value:
            variable = variable.split()[0]
            try:
                value = var.pattern_match.group(2).split()[1]
            except IndexError:
                return await var.edit(">`.set var <ConfigVars-name> <value>`")
        if variable in heroku_var:
            if BOTLOG:
                await var.client.send_message(
                    BOTLOG_CHATID, "#SETCONFIGVAR\n\n"
                    "**Set ConfigVar**:\n"
                    " -> `Config Variable`:\n"
                    f"     • `{variable}`\n"
                    " -> `Value`:\n"
                    f"     • `{value}`\n\n"
                    "`Successfully changed...`"
                )
            await var.edit("`Information sets...`")
        else:
            if BOTLOG:
                await var.client.send_message(
                    BOTLOG_CHATID, "#ADDCONFIGVAR\n\n"
                    "**Add ConfigVar**:\n"
                    " -> `Config Variable`:\n"
                    f"     • `{variable}`\n"
                    " -> `Value`:\n"
                    f"     • `{value}`\n\n"
                    "`Successfully added...`"
                )
            await var.edit("`Information added...`")
        heroku_var[variable] = value
    elif exe == "del":
        await var.edit("`Getting and setting information...`")
        try:
            variable = var.pattern_match.group(2).split()[0]
        except IndexError:
            return await var.edit("`Please specify ConfigVars you want to delete`.")
        if variable in heroku_var:
            if BOTLOG:
                await var.client.send_message(
                    BOTLOG_CHATID, "#DELCONFIGVAR\n\n"
                    "**Delete ConfigVar**:\n"
                    " -> `Config Variable`:\n"
                    f"     • `{variable}`\n\n"
                    "`Successfully deleted...`"
                )
            await var.edit("`Information deleted...`")
            del heroku_var[variable]
        else:
            await var.edit(f"`Can't get information...`")
            rsp = await var.respond(
                "**Delete ConfigVar**:\n"
                " -> `Config Variable`:\n"
                f"     • `{variable}`\n\n"
                "`Is not exists...`"
                )
            await asyncio.sleep(3.5)
            await var.client.delete_messages(var.chat_id, rsp.id)


@register(outgoing=True, pattern=r"^.usage(?: |$)")
async def dyno_usage(dyno):
    """
        Get your account Dyno Usage
    """
    await dyno.edit("`Getting Information...`")
    useragent = ('Mozilla/5.0 (Linux; Android 10; SM-G975F) '
                 'AppleWebKit/537.36 (KHTML, like Gecko) '
                 'Chrome/80.0.3987.149 Mobile Safari/537.36'
                 )
    user_id = Heroku.account().id
    headers = {
     'User-Agent': useragent,
     'Authorization': f'Bearer {HEROKU_API_KEY}',
     'Accept': 'application/vnd.heroku+json; version=3.account-quotas',
    }
    path = "/accounts/" + user_id + "/actions/get-quota"
    r = requests.get(heroku_api + path, headers=headers)
    if r.status_code != 200:
        return await dyno.edit("`Error: something bad happened`\n\n"
                               f">.`{r.reason}`\n")
    result = r.json()
    quota = result['account_quota']
    quota_used = result['quota_used']

    """ - Used - """
    remaining_quota = quota - quota_used
    percentage = math.floor(remaining_quota / quota * 100)
    minutes_remaining = remaining_quota / 60
    hours = math.floor(minutes_remaining / 60)
    minutes = math.floor(minutes_remaining % 60)

    """ - Current - """
    App = result['apps']
    try:
        App[0]['quota_used']
    except IndexError:
        AppQuotaUsed = 0
        AppPercentage = 0
    else:
        AppQuotaUsed = App[0]['quota_used'] / 60
        AppPercentage = math.floor(App[0]['quota_used'] * 100 / quota)
    AppHours = math.floor(AppQuotaUsed / 60)
    AppMinutes = math.floor(AppQuotaUsed % 60)

    return await dyno.edit("**Dyno Usage**:\n\n"
                           f" -> `Dyno usage for`  **{HEROKU_APP_NAME}**:\n"
                           f"     •  `{AppHours}`**h**  `{AppMinutes}`**m**  "
                           f"**|**  [`{AppPercentage}`**%**]"
                           "\n\n"
                           " -> `Dyno hours quota remaining this month`:\n"
                           f"     •  `{hours}`**h**  `{minutes}`**m**  "
                           f"**|**  [`{percentage}`**%**]"
                           )


CMD_HELP.update({
    "heroku":
    ">.`usage`"
    "\nUsage: Check your heroku dyno hours remaining"
    "\n\n>`.set var <NEW VAR> <VALUE>`"
    "\nUsage: add new variable or update existing value variable"
    "\n!!! WARNING !!!, after setting a variable the bot will restarted"
    "\n\n>`.get var or .get var <VAR>`"
    "\nUsage: get your existing varibles, use it only on your private group!"
    "\nThis returns all of your private information, please be caution..."
    "\n\n>`.del var <VAR>`"
    "\nUsage: delete existing variable"
    "\n!!! WARNING !!!, after deleting variable the bot will restarted"
})
