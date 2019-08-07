# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.b (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module for managing events. One of the main components of the userbot. """

from telethon import events
from telethon.events import StopPropagation
import asyncio
from userbot import bot
from traceback import format_exc
from time import gmtime, strftime
import math
import subprocess
import sys
import traceback
import datetime


def register(**args):
    """ Register a new event. """
    pattern = args.get('pattern', None)
    disable_edited = args.get('disable_edited', False)

    if pattern is not None and not pattern.startswith('(?i)'):
        args['pattern'] = '(?i)' + pattern

    if "disable_edited" in args:
        del args['disable_edited']

    def decorator(func):
        if not disable_edited:
            bot.add_event_handler(func, events.MessageEdited(**args))
        bot.add_event_handler(func, events.NewMessage(**args))

        return func

    return decorator