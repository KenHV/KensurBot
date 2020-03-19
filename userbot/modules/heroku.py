# Copyright (C) 2020 Adek Maulana.
# All rights reserved.
"""
   Heroku manager for your userbot
"""

import heroku3

from userbot import CMD_HELP, LOGS, HEROKU_APP_NAME, HEROKU_API_KEY
from userbot.events import register

Heroku = heroku3.from_key(HEROKU_API_KEY)


@register(outgoing=True, pattern=r"^.heroku(?: |$)(.*)")
async def heroku_manager(heroku):
    await heroku.edit("`Processing...`")
    conf = heroku.pattern_match.group(1)
    hours_remaining = Heroku.ratelimit_remaining()
    await heroku.edit(f"**Heroku** rate limit remaining: {hours_remaining}")
    return


CMD_HELP.update({
    "heroku":
    "`.heroku`"
    "Usage: Your heroku account manager"
})
