# Copyright (C) 2019 Adek Maulana
#
# Ported and add more features from my script inside build-kernel.py

"""
    Google Drive manager for Userbot
"""
import pickle
import codecs
from os.path import isfile

from telethon import events

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

from userbot import (G_DRIVE_CLIENT_ID, G_DRIVE_CLIENT_SECRET,
                     G_DRIVE_AUTH_TOKEN_DATA, GDRIVE_FOLDER_ID, BOTLOG_CHATID,
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


@register(pattern="^.gdf (.*)", outgoing=True)
async def test(gdrive):
    service = await services(gdrive)
    folder_name = gdrive.pattern_match.group(1)
    folder_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
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
    try:
        folder = result.get('files', [])[0]
    except IndexError:
        return await gdrive.edit(f"**{folder_name}**  `is not exists`")
    else:
        f_name = folder.get('name')
        f_id = folder.get('id')
    page_token = result.get('nextPageToken', None)
    return await gdrive.edit(f"**{f_name}** is exists")


async def services(gdrive):
    """
        Generate credentials
    """
    await gdrive.edit("`Setting information...`")
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
        # decoded creds string to class object
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
            if G_DRIVE_AUTH_TOKEN_DATA is None:
                with open("auth.txt", "w") as f:
                    # save credentials object as a string
                    pickled = codecs.encode(
                            pickle.dumps(creds), "base64").decode()
                    f.write(pickled)
    service = build('drive', 'v3', credentials=creds, cache_discovery=False)
    return service
