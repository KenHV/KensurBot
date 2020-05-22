# Copyright (C) 2020 Adek Maulana.
# All rights reserved.
"""
   Heroku manager for your userbot
"""

import heroku3
import aiohttp
import math

from userbot import (
    CMD_HELP,
    HEROKU_APP_NAME,
    HEROKU_API_KEY,
    BOTLOG,
    BOTLOG_CHATID
)

from userbot.events import register

heroku_api = "https://api.heroku.com"
if HEROKU_APP_NAME is not None and HEROKU_API_KEY is not None:
    Heroku = heroku3.from_key(HEROKU_API_KEY)
    app = Heroku.app(HEROKU_APP_NAME)


@register(outgoing=True,
          pattern=r"^.(set|get|del) var(?: |$)(.*)(?: |$)([\s\S]*)")
async def variable(var):
    """
        Manage most of ConfigVars setting, set new var, get current var,
        or delete var...
    """
    exe = var.pattern_match.group(1)
    try:
        heroku_var = app.config()
    except NameError:
        return await var.edit("`[HEROKU]"
                              "\nPlease setup your`  **HEROKU_APP_NAME**.")
    if exe == "get":
        await var.edit("`Getting information...`")
        try:
            variable = var.pattern_match.group(2).split()[0]
            if variable in heroku_var:
                if BOTLOG:
                    await var.client.send_message(
                        BOTLOG_CHATID, "#CONFIGVAR\n\n"
                        "**ConfigVar**:\n"
                        "`Config Variable`:\n"
                        f"`{variable}`\n"
                        "`Value`:\n"
                        f"`{heroku_var[variable]}`\n"
                    )
                    return await var.edit("`Received to BOTLOG_CHATID...`")
                else:
                    return await var.edit("`Please set BOTLOG to True...`")
            else:
                return await var.edit("`Information don't exists...`")
        except IndexError:
            configvars = heroku_var.to_dict()
            msg = ''
            if BOTLOG:
                for item in configvars:
                    msg += f"`{item}` **=** `{configvars[item]}`\n"
                await var.client.send_message(
                    BOTLOG_CHATID, "#CONFIGVARS\n\n"
                    "**ConfigVars**:\n"
                    f"{msg}"
                )
                return await var.edit("`Received to BOTLOG_CHATID...`")
            else:
                return await var.edit("`Please set BOTLOG to True...`")
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
                    "`Config Variable`:\n"
                    f"`{variable}`\n"
                    "`Value`:\n"
                    f"`{value}`\n\n"
                    "`Successfully changed...`"
                )
            await var.edit("`Information sets...`")
        else:
            if BOTLOG:
                await var.client.send_message(
                    BOTLOG_CHATID, "#ADDCONFIGVAR\n\n"
                    "**Add ConfigVar**:\n"
                    "`Config Variable`:\n"
                    f"`{variable}`\n"
                    "`Value`:\n"
                    f"`{value}`\n\n"
                    "`Successfully added...`"
                )
            await var.edit("`Information added...`")
        heroku_var[variable] = value
    elif exe == "del":
        await var.edit("`Getting and setting information...`")
        try:
            variable = var.pattern_match.group(2).split()[0]
        except IndexError:
            return await var.edit("`Specify ConfigVars you want to del...`")
        if variable in heroku_var:
            if BOTLOG:
                await var.client.send_message(
                    BOTLOG_CHATID, "#DELCONFIGVAR\n\n"
                    "**Delete ConfigVar**:\n"
                    "`Config Variable`:\n"
                    f"`{variable}`\n\n"
                    "`Successfully deleted...`"
                )
            await var.edit("`Information deleted...`")
            del heroku_var[variable]
        else:
            return await var.edit("`Information don't exists...`")


@register(outgoing=True, pattern=r"^.usage(?: |$)")
async def dyno_usage(dyno):
    """
        Get your account Dyno Usage
    """
    await dyno.edit("`Getting Information...`")
    useragent = (
        'Mozilla/5.0 (Linux; Android 10; SM-G975F) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/81.0.4044.117 Mobile Safari/537.36'
    )
    user_id = Heroku.account().id
    headers = {
     'User-Agent': useragent,
     'Authorization': f'Bearer {HEROKU_API_KEY}',
     'Accept': 'application/vnd.heroku+json; version=3.account-quotas',
    }
    path = "/accounts/" + user_id + "/actions/get-quota"
    async with aiohttp.ClientSession() as session:
        async with session.get(heroku_api + path, headers=headers) as r:
            if r.status != 200:
                await dyno.client.send_message(
                    dyno.chat_id,
                    f"`{r.reason}`",
                    reply_to=dyno.id
                )
                await dyno.edit("`Can't get information...`")
                return False
            result = await r.json()
            quota = result['account_quota']
            quota_used = result['quota_used']

            """ - User Quota Limit and Used - """
            remaining_quota = quota - quota_used
            percentage = math.floor(remaining_quota / quota * 100)
            minutes_remaining = remaining_quota / 60
            hours = math.floor(minutes_remaining / 60)
            minutes = math.floor(minutes_remaining % 60)

            """ - User App Used Quota - """
            Apps = result['apps']
            for apps in Apps:
                if apps.get('app_uuid') == app.id:
                    AppQuotaUsed = apps.get('quota_used') / 60
                    AppPercentage = math.floor(
                        apps.get('quota_used') * 100 / quota)
                    break
            else:
                AppQuotaUsed = 0
                AppPercentage = 0

            AppHours = math.floor(AppQuotaUsed / 60)
            AppMinutes = math.floor(AppQuotaUsed % 60)

            await dyno.edit(
                 "**Dyno Usage**:\n\n"
                 f" -> `Dyno usage for`  **{app.name}**:\n"
                 f"     •  `{AppHours}`**h**  `{AppMinutes}`**m**  "
                 f"**|**  [`{AppPercentage}`**%**]"
                 "\n\n"
                 " -> `Dyno hours quota remaining this month`:\n"
                 f"     •  `{hours}`**h**  `{minutes}`**m**  "
                 f"**|**  [`{percentage}`**%**]"
            )
            return True


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
