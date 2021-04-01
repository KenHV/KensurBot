# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot initialization. """

import os
import signal
import sys
from distutils.util import strtobool
from logging import DEBUG, INFO, basicConfig, getLogger
from pathlib import Path
from platform import python_version

from dotenv import load_dotenv
from pylast import LastFMNetwork, md5
from telethon import TelegramClient, version
from telethon.network.connection.tcpabridged import ConnectionTcpAbridged
from telethon.sessions import StringSession

from .storage import Storage

STORAGE = lambda n: Storage(Path("data") / n)

load_dotenv("config.env")

# Bot Logs setup:
CONSOLE_LOGGER_VERBOSE = strtobool(os.environ.get("CONSOLE_LOGGER_VERBOSE", "False"))

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

if sys.version_info[0] < 3 or sys.version_info[1] < 9:
    LOGS.info(
        "You MUST have a python version of at least 3.9."
        "Multiple features depend on this. Bot quitting."
    )
    sys.exit(1)

# Check if the config was edited by using the already used variable.
# Basically, its the 'virginity check' for the config file ;)
CONFIG_CHECK = os.environ.get(
    "___________PLOX_______REMOVE_____THIS_____LINE__________"
)

if CONFIG_CHECK:
    LOGS.info(
        "Please remove the line mentioned in the first hashtag from the config.env file"
    )
    sys.exit(1)

# Telegram App KEY and HASH
API_KEY = int(os.environ.get("API_KEY", 0))
API_HASH = str(os.environ.get("API_HASH"))

# Userbot Session String
STRING_SESSION = os.environ.get("STRING_SESSION")

# Logging channel/group ID configuration.
BOTLOG_CHATID = int(os.environ.get("BOTLOG_CHATID", 0))

# Userbot logging feature switch.
BOTLOG = strtobool(os.environ.get("BOTLOG", "False"))
LOGSPAMMER = strtobool(os.environ.get("LOGSPAMMER", "False"))

# Bleep Blop, this is a bot ;)
PM_AUTO_BAN = strtobool(os.environ.get("PM_AUTO_BAN", "False"))

# Heroku Credentials for updater.
HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
HEROKU_API_KEY = os.environ.get("HEROKU_API_KEY")

# Custom (forked) repo URL and BRANCH for updater.
UPSTREAM_REPO_URL = "https://github.com/KenHV/KensurBot.git"
UPSTREAM_REPO_BRANCH = "staging"

# Console verbose logging
CONSOLE_LOGGER_VERBOSE = strtobool(os.environ.get("CONSOLE_LOGGER_VERBOSE") or "False")

# SQL Database URI
DB_URI = os.environ.get("DATABASE_URL")

# OCR API key
OCR_SPACE_API_KEY = os.environ.get("OCR_SPACE_API_KEY")

# remove.bg API key
REM_BG_API_KEY = os.environ.get("REM_BG_API_KEY")

# Chrome Driver and Chrome Binaries
CHROME_DRIVER = "/usr/bin/chromedriver"
CHROME_BIN = "/usr/bin/chromium"

# OpenWeatherMap API Key
OPEN_WEATHER_MAP_APPID = os.environ.get("OPEN_WEATHER_MAP_APPID")
WEATHER_DEFCITY = os.environ.get("WEATHER_DEFCITY")

# Anti Spambot Config
ANTI_SPAMBOT = strtobool(os.environ.get("ANTI_SPAMBOT", "False"))
ANTI_SPAMBOT_SHOUT = strtobool(os.environ.get("ANTI_SPAMBOT_SHOUT", "False"))

# Default .alive name
ALIVE_NAME = os.environ.get("ALIVE_NAME")

# Time & Date - Country and Time Zone
COUNTRY = os.environ.get("COUNTRY")
TZ_NUMBER = int(os.environ.get("TZ_NUMBER", 1))

# Zipfile module
ZIP_DOWNLOAD_DIRECTORY = os.environ.get("ZIP_DOWNLOAD_DIRECTORY") or "./zips"

# Clean Welcome
CLEAN_WELCOME = strtobool(os.environ.get("CLEAN_WELCOME") or "False")

# Last.fm Module
BIO_PREFIX = os.environ.get("BIO_PREFIX")
DEFAULT_BIO = os.environ.get("DEFAULT_BIO")

LASTFM_API = os.environ.get("LASTFM_API")
LASTFM_SECRET = os.environ.get("LASTFM_SECRET")
LASTFM_USERNAME = os.environ.get("LASTFM_USERNAME")
LASTFM_PASSWORD_PLAIN = os.environ.get("LASTFM_PASSWORD")
LASTFM_PASS = md5(LASTFM_PASSWORD_PLAIN)

lastfm = None
if LASTFM_API and LASTFM_SECRET and LASTFM_USERNAME and LASTFM_PASS:
    try:
        lastfm = LastFMNetwork(
            api_key=LASTFM_API,
            api_secret=LASTFM_SECRET,
            username=LASTFM_USERNAME,
            password_hash=LASTFM_PASS,
        )
    except Exception:
        pass

# Google Drive Module
G_DRIVE_DATA = os.environ.get("G_DRIVE_DATA")
G_DRIVE_CLIENT_ID = os.environ.get("G_DRIVE_CLIENT_ID")
G_DRIVE_CLIENT_SECRET = os.environ.get("G_DRIVE_CLIENT_SECRET")
G_DRIVE_AUTH_TOKEN_DATA = os.environ.get("G_DRIVE_AUTH_TOKEN_DATA")
G_DRIVE_FOLDER_ID = os.environ.get("G_DRIVE_FOLDER_ID")
G_DRIVE_INDEX_URL = os.environ.get("G_DRIVE_INDEX_URL")

TEMP_DOWNLOAD_DIRECTORY = os.environ.get("TMP_DOWNLOAD_DIRECTORY", "./downloads/")

# Terminal Alias
TERM_ALIAS = os.environ.get("TERM_ALIAS")

# Deezloader
DEEZER_ARL_TOKEN = os.environ.get("DEEZER_ARL_TOKEN")

# Genius Lyrics API
GENIUS = os.environ.get("GENIUS_ACCESS_TOKEN")

# Uptobox
USR_TOKEN = os.environ.get("USR_TOKEN_UPTOBOX")

# KensurBot version
KENSURBOT_VERSION = "1.2"


def shutdown_bot(*_):
    LOGS.info("Received SIGTERM.")
    bot.disconnect()
    sys.exit(143)


signal.signal(signal.SIGTERM, shutdown_bot)


bot = TelegramClient(
    session=StringSession(STRING_SESSION),
    api_id=API_KEY,
    api_hash=API_HASH,
    connection=ConnectionTcpAbridged,
    auto_reconnect=True,
)


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


async def update_restart_msg(chat_id, msg_id):
    DEFAULTUSER = ALIVE_NAME or "Set `ALIVE_NAME` ConfigVar!"
    message = (
        f"**KensurBot v{KENSURBOT_VERSION} is back up and running!**\n\n"
        f"**Telethon:** {version.__version__}\n"
        f"**Python:** {python_version()}\n"
        f"**User:** {DEFAULTUSER}"
    )
    await bot.edit_message(chat_id, msg_id, message)
    return True


try:
    from userbot.modules.sql_helper.globals import delgvar, gvarstatus

    chat_id, msg_id = gvarstatus("restartstatus").split("\n")
    with bot:
        try:
            bot.loop.run_until_complete(update_restart_msg(int(chat_id), int(msg_id)))
        except:
            pass
    delgvar("restartstatus")
except AttributeError:
    pass

# Global Variables
COUNT_MSG = 0
USERS = {}
COUNT_PM = {}
LASTMSG = {}
CMD_HELP = {}
ISAFK = False
AFKREASON = None
