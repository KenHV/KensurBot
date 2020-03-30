# Copyright (C) 2019 Adek Maulana
#
# Ported and add more features from my script inside build-kernel.py

"""
    Google Drive manager for Userbot
"""
import pickle
import codecs
from os.path import isfile, isdir
from mimetypes import guess_type

from telethon import events

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request

from userbot import (G_DRIVE_CLIENT_ID, G_DRIVE_CLIENT_SECRET,
                     G_DRIVE_AUTH_TOKEN_DATA, BOTLOG_CHATID,
                     TEMP_DOWNLOAD_DIRECTORY, CMD_HELP, LOGS)
from userbot.events import register

#                          STATIC                             #
# =========================================================== #
GOOGLE_AUTH_URI = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URI = "https://oauth2.googleapis.com/token"
SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.metadata"
]
REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"
# ============================================================ #


async def get_mimeType(name):
    """ - Check mimeType given file - """
    if isfile(name):
        mimeType = guess_type(name)[0]
        if not mimeType:
            mimeType = 'text/plain'
    return mimeType


@register(pattern=r"^.gdf (mkdir|rm)(.*)", outgoing=True)
async def folders(gdrive):
    """ - Google Drive folder management - """
    URL = "https://drive.google.com/drive/folders/"
    await gdrive.edit("`Sending information...`")
    service = await create_app(gdrive)
    folder_name = gdrive.pattern_match.group(2).strip()
    exe = gdrive.pattern_match.group(1)
    folder_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
    }
    page_token = None
    result = service.files().list(
        q=f"name='{folder_name}'",
        spaces='drive',
        fields=(
            'nextPageToken, '
            'files(parents, name, id)'
        ),
        pageToken=page_token
     ).execute()
    if exe == "mkdir":
        """ - Create a directory, abort if exist when parent not given - """
        try:
            folder = result.get('files', [])[0]
        except IndexError:
            folder = service.files().create(
                   body=folder_metadata,
                   fields='id'
             ).execute()
            folder_id = folder.get('id')
            await gdrive.edit(
                "`[FOLDER - CREATED]`\n\n"
                f" • `Name :` `{folder_name}`\n"
                f" • `ID   :` `{folder_id}`\n"
                f" • `URL  :` {URL + folder_id}"
            )
        else:
            await gdrive.edit(
                "`[FOLDER - EXIST]`\n\n"
                f" • `Name :` `{folder_name}`")
    elif exe == "rm":
        """ - Permanently delete, skipping the trash - """
        try:
            """ - Try if given value is a name not a folderID - """
            folder = result.get('files', [])[0]
            folder_id = folder.get('id')
        except IndexError:
            """ - If failed assumming value is folderID - """
            folder_id = folder_name
        page_token = result.get('nextPageToken', None)
        try:
            service.files().delete(fileId=folder_id).execute()
        except HttpError as e:
            await gdrive.edit(
                "`[FOLDER - ERROR]`\n\n"
                f" • `Status :` `{str(e)}`"
            )
        else:
            await gdrive.edit(
                    "`[FOLDER - DELETE]`\n\n"
                    " • `Status :` `OK`"
            )
    page_token = result.get('nextPageToken', None)
    return


async def generate_credentials(gdrive):
    """ - Generate credentials - """
    configs = {
        "installed": {
            "client_id": G_DRIVE_CLIENT_ID,
            "client_secret": G_DRIVE_CLIENT_SECRET,
            "auth_uri": GOOGLE_AUTH_URI,
            "token_uri": GOOGLE_TOKEN_URI,
        }
    }
    creds = None
    if G_DRIVE_AUTH_TOKEN_DATA is not None:
        """ - Repack credential objects from strings - """
        creds = pickle.loads(
              codecs.decode(G_DRIVE_AUTH_TOKEN_DATA.encode(), "base64"))
    else:
        if isfile("auth.txt"):
            with open("auth.txt", "r") as token:
                creds = token.read()
                creds = pickle.loads(codecs.decode(creds.encode(), "base64"))
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(
                 configs, SCOPES, redirect_uri=REDIRECT_URI)
            auth_url, _ = flow.authorization_url(
                        access_type='offline', prompt='consent')
            async with gdrive.client.conversation(BOTLOG_CHATID) as conv:
                await conv.send_message(
                    "Please go to this URL:\n"
                    f"{auth_url}\nauthorize then reply the code"
                )
                r = conv.wait_event(
                  events.NewMessage(outgoing=True, chats=BOTLOG_CHATID))
                r = await r
                code = r.message.message.strip()
                flow.fetch_token(code=code)
                creds = flow.credentials
            """ - Unpack credential objects into strings - """
            if G_DRIVE_AUTH_TOKEN_DATA is None:
                with open("auth.txt", "w") as f:
                    pickled = codecs.encode(
                            pickle.dumps(creds), "base64").decode()
                    """ - Put into file to use it later - """
                    f.write(pickled)
    return creds


async def create_app(gdrive):
    """ - Create google drive service app - """
    creds = await generate_credentials(gdrive)
    service = build('drive', 'v3', credentials=creds, cache_discovery=False)
    return service
