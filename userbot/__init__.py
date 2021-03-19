# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot initialization. """

import os
import sys
from distutils.util import strtobool as sb
from logging import DEBUG, INFO, basicConfig, getLogger
from pathlib import Path

from dotenv import load_dotenv
from pylast import LastFMNetwork, md5
from pySmartDL import SmartDL
from requests import get
from telethon import TelegramClient
from telethon.network.connection.tcpabridged import ConnectionTcpAbridged
from telethon.sessions import StringSession

from .storage import Storage

STORAGE = lambda n: Storage(Path("data") / n)

load_dotenv("config.env")

# Bot Logs setup:
CONSOLE_LOGGER_VERBOSE = sb(os.environ.get("CONSOLE_LOGGER_VERBOSE") or "False")

if CONSOLE_LOGGER_VERBOSE:
    basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=DEBUG,
    )
else:
    basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=INFO
    )
LOGS = getLogger(__name__)

if sys.version_info[0] < 3 or sys.version_info[1] < 8:
    LOGS.info(
        "You MUST have a python version of at least 3.8."
        "Multiple features depend on this. Bot quitting."
    )
    sys.exit(1)

# Check if the config was edited by using the already used variable.
# Basically, its the 'virginity check' for the config file ;)
CONFIG_CHECK = (
    os.environ.get("___________PLOX_______REMOVE_____THIS_____LINE__________") or None
)

if CONFIG_CHECK:
    LOGS.info(
        "Please remove the line mentioned in the first hashtag from the config.env file"
    )
    sys.exit(1)

# Telegram App KEY and HASH
API_KEY = int(os.environ.get("API_KEY") or 0)
API_HASH = str(os.environ.get("API_HASH") or None)

# Userbot Session String
STRING_SESSION = os.environ.get("STRING_SESSION") or None

# Logging channel/group ID configuration.
BOTLOG_CHATID = int(os.environ.get("BOTLOG_CHATID") or 0)

# Userbot logging feature switch.
BOTLOG = sb(os.environ.get("BOTLOG") or "False")
LOGSPAMMER = sb(os.environ.get("LOGSPAMMER") or "False")

# Bleep Blop, this is a bot ;)
PM_AUTO_BAN = sb(os.environ.get("PM_AUTO_BAN") or "False")

# Heroku Credentials for updater.
HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME") or None
HEROKU_API_KEY = os.environ.get("HEROKU_API_KEY") or None

# Custom (forked) repo URL and BRANCH for updater.
UPSTREAM_REPO_URL = "https://github.com/KenHV/KensurBot.git"
UPSTREAM_REPO_BRANCH = "master"

# Console verbose logging
CONSOLE_LOGGER_VERBOSE = sb(os.environ.get("CONSOLE_LOGGER_VERBOSE") or "False")

# SQL Database URI
DB_URI = os.environ.get("DATABASE_URL") or None

# OCR API key
OCR_SPACE_API_KEY = os.environ.get("OCR_SPACE_API_KEY") or None

# Default .alive name
ALIVE_NAME = str(os.environ.get("ALIVE_NAME")) or None

# remove.bg API key
REM_BG_API_KEY = os.environ.get("REM_BG_API_KEY") or None

# Chrome Driver and Headless Google Chrome Binaries
CHROME_DRIVER = os.environ.get("CHROME_DRIVER") or None
GOOGLE_CHROME_BIN = os.environ.get("GOOGLE_CHROME_BIN") or None

# OpenWeatherMap API Key
OPEN_WEATHER_MAP_APPID = os.environ.get("OPEN_WEATHER_MAP_APPID") or None
WEATHER_DEFCITY = os.environ.get("WEATHER_DEFCITY") or None

# Anti Spambot Config
ANTI_SPAMBOT = sb(os.environ.get("ANTI_SPAMBOT") or "False")
ANTI_SPAMBOT_SHOUT = sb(os.environ.get("ANTI_SPAMBOT_SHOUT") or "False")

# Default .alive name
ALIVE_NAME = os.environ.get("ALIVE_NAME") or None

# Time & Date - Country and Time Zone
COUNTRY = str(os.environ.get("COUNTRY") or "")
TZ_NUMBER = int(os.environ.get("TZ_NUMBER") or 1)

# Zipfile module
ZIP_DOWNLOAD_DIRECTORY = os.environ.get("ZIP_DOWNLOAD_DIRECTORY") or "./zips"

# Clean Welcome
CLEAN_WELCOME = sb(os.environ.get("CLEAN_WELCOME") or "False")

# Last.fm Module
BIO_PREFIX = os.environ.get("BIO_PREFIX") or None
DEFAULT_BIO = os.environ.get("DEFAULT_BIO") or None

LASTFM_API = os.environ.get("LASTFM_API") or None
LASTFM_SECRET = os.environ.get("LASTFM_SECRET") or None
LASTFM_USERNAME = os.environ.get("LASTFM_USERNAME") or None
LASTFM_PASSWORD_PLAIN = os.environ.get("LASTFM_PASSWORD") or None
LASTFM_PASS = md5(LASTFM_PASSWORD_PLAIN)
if LASTFM_API and LASTFM_SECRET and LASTFM_USERNAME and LASTFM_PASS:
    lastfm = LastFMNetwork(
        api_key=LASTFM_API,
        api_secret=LASTFM_SECRET,
        username=LASTFM_USERNAME,
        password_hash=LASTFM_PASS,
    )
else:
    lastfm = None

# Google Drive Module
G_DRIVE_DATA = os.environ.get("G_DRIVE_DATA") or None
G_DRIVE_CLIENT_ID = os.environ.get("G_DRIVE_CLIENT_ID") or None
G_DRIVE_CLIENT_SECRET = os.environ.get("G_DRIVE_CLIENT_SECRET") or None
G_DRIVE_AUTH_TOKEN_DATA = os.environ.get("G_DRIVE_AUTH_TOKEN_DATA") or None
G_DRIVE_FOLDER_ID = os.environ.get("G_DRIVE_FOLDER_ID") or None
TEMP_DOWNLOAD_DIRECTORY = os.environ.get("TMP_DOWNLOAD_DIRECTORY") or "./downloads/"

# Terminal Alias
TERM_ALIAS = os.environ.get("TERM_ALIAS") or None

# Deezloader
DEEZER_ARL_TOKEN = os.environ.get("DEEZER_ARL_TOKEN") or None

# Genius Lyrics API
GENIUS = os.environ.get("GENIUS_ACCESS_TOKEN") or None

# Uptobox
USR_TOKEN = os.environ.get("USR_TOKEN_UPTOBOX") or None

# 'bot' variable
if STRING_SESSION:
    # pylint: disable=invalid-name
    bot = TelegramClient(
        session=StringSession(STRING_SESSION),
        api_id=API_KEY,
        api_hash=API_HASH,
        connection=ConnectionTcpAbridged,
        auto_reconnect=True,
        connection_retries=-1,
    )
else:
    # pylint: disable=invalid-name
    bot = TelegramClient("userbot", API_KEY, API_HASH)


async def check_botlog_chatid():
    if not BOTLOG_CHATID and LOGSPAMMER:
        LOGS.info(
            "You must set up the BOTLOG_CHATID variable in the config.env or environment variables, for the private error log storage to work."
        )
        sys.exit(1)

    elif not BOTLOG_CHATID and BOTLOG:
        LOGS.info(
            "You must set up the BOTLOG_CHATID variable in the config.env or environment variables, for the userbot logging feature to work."
        )
        sys.exit(1)

    elif not (BOTLOG and LOGSPAMMER):
        return

    entity = await bot.get_entity(BOTLOG_CHATID)
    if entity.default_banned_rights.send_messages:
        LOGS.info(
            "Your account doesn't have rights to send messages to BOTLOG_CHATID "
            "group. Check if you typed the Chat ID correctly."
        )
        sys.exit(1)


with bot:
    try:
        bot.loop.run_until_complete(check_botlog_chatid())
    except BaseException:
        LOGS.info(
            "BOTLOG_CHATID environment variable isn't a "
            "valid entity. Check your environment variables/config.env file."
        )
        sys.exit(1)

# Global Variables
COUNT_MSG = 0
USERS = {}
COUNT_PM = {}
LASTMSG = {}
CMD_HELP = {}
ISAFK = False
AFKREASON = None
