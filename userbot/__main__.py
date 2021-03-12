# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot start point """

import sys
from importlib import import_module

from telethon.errors.rpcerrorlist import PhoneNumberInvalidError

from userbot import LOGS, bot
from userbot.modules import ALL_MODULES

INVALID_PH = (
    "\nError: Invalid phone number."
    "\nTip: Prefix number with country code"
    "\nor check your phone number and try again."
)

try:
    bot.start()
except PhoneNumberInvalidError:
    print(INVALID_PH)
    sys.exit(1)

for module_name in ALL_MODULES:
    imported_module = import_module("userbot.modules." + module_name)

LOGS.info("Your userbot is running!")

LOGS.info(
    "Congratulations, the bot is up and running! Send .help in any chat for more info.\n"
    "If you need assistance, head to https://t.me/KensurOT"
)

if len(sys.argv) not in (1, 3, 4):
    bot.disconnect()
else:
    bot.run_until_disconnected()
