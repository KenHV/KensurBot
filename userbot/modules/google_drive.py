# Copyright (C) 2019 Adek Maulana
#
# Ported and add more features from my script inside build-kernel.py

"""
    Google Drive manager for Userbot
"""
import pickle
import codecs
import asyncio
import math
from os.path import isfile, isdir
from mimetypes import guess_type

from telethon import events

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload

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
    mimeType = guess_type(name)[0]
    if not mimeType:
        mimeType = 'text/plain'
    return mimeType


@register(pattern=r"^.gdf (mkdir|rm)(.*)", outgoing=True)
async def folders(gdrive):
    """ - Google Drive folder/file management - """
    await gdrive.edit("`Sending information...`")
    service = await create_app(gdrive)
    f_name = gdrive.pattern_match.group(2).strip()
    exe = gdrive.pattern_match.group(1)
    """ - Check if given value is file and exists in local - """
    if isfile(f_name) and exe == "mkdir":
        return await gdrive.edit("`Failed to send information...`")
    """ - Only if given value are mkdir - """
    metadata = {
        'name': f_name,
        'mimeType': 'application/vnd.google-apps.folder',
    }
    permission = {
        "role": "reader",
        "type": "anyone",
        "allowFileDiscovery": True,
        "value": None,
    }
    page_token = None
    result = service.files().list(
        q=f"name='{f_name}'",
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
                   body=metadata,
                   fields='id'
             ).execute()
            folder_id = folder.get('id')
            """ - Change permission - """
            try:
                service.permissions().create(
                   fileId=folder_id, body=permission).execute()
            except HttpError as e:
                return await gdrive.edit("`" + str(e) + "`")
            folder = service.files().get(
                   fileId=folder_id, fields="webViewLink").execute()
            webViewURL = folder.get("webViewLink")
            await gdrive.edit(
                "`[FOLDER - CREATED]`\n\n"
                f" • `Name :` `{f_name}`\n"
                f" • `ID   :` `{folder_id}`\n"
                f" • `URL  :` {webViewURL}"
            )
        else:
            await gdrive.edit(
                "`[FOLDER - EXIST]`\n\n"
                f" • `Name :` `{f_name}`")
    elif exe == "rm":
        """ - Permanently delete, skipping the trash - """
        try:
            """ - Try if given value is a name not a folderId/fileId - """
            f = result.get('files', [])[0]
            f_id = f.get('id')
        except IndexError:
            """ - If failed assumming value is folderId/fileId - """
            folder_id = f_name
        page_token = result.get('nextPageToken', None)
        try:
            service.files().delete(fileId=f_id).execute()
        except HttpError as e:
            status = "[FILE - ERROR]" if isfile(f_name) else "[FOLDER - ERROR]"
            await gdrive.edit(
                f"`{status}`\n\n"
                f" • `Status :` `{str(e)}`"
            )
        else:
            status = (
                "[FILE - DELETE]" if isfile(f_name) else
                "[FOLDER - DELETE]"
            )
            await gdrive.edit(
                    f"`{status}`\n\n"
                    " • `Status :` `OK`"
            )
    page_token = result.get('nextPageToken', None)
    return


@register(pattern="^.gd(?: |$)(.*)", outgoing=True)
async def upload(gdrive):
    if not gdrive.pattern_match.group(1) and not gdrive.reply_to_msg_id:
        return
    file_name = gdrive.pattern_match.group(1)
    mimeType = await get_mimeType(file_name)
    if isdir(file_name):
        return await gdrive.edit("`[FOLDER - ERROR]`\n\n"
                                 " • `Status :` `FAILED`\n"
                                 " • `Reason :` `Folder upload not supported"
                                 )
    service = await create_app(gdrive)
    await gdrive.edit("`Processing upload...`")
    body = {
        "name": file_name,
        "description": "Uploaded from Telegram using ProjectBish userbot.",
        "mimeType": mimeType,
    }
    permission = {
        "role": "reader",
        "type": "anyone",
        "allowFileDiscovery": True,
        "value": None,
    }
    media_body = MediaFileUpload(
        file_name,
        mimetype=mimeType,
        resumable=True
    )
    """ - Start upload process - """
    response = None
    display_message = None
    file = service.files().create(body=body, media_body=media_body,
                                  fields="id, webContentLink, webViewLink")
    while response is None:
        status, response = file.next_chunk()
        await asyncio.sleep(0.3)
        if status:
            percentage = int(status.progress() * 100)
            prog_str = "`Uploading...` | [{0}{1}] `{2}%`".format(
                "".join(["**#**" for i in range(math.floor(percentage / 10))]),
                "".join(["**-**"
                         for i in range(10 - math.floor(percentage / 10))]),
                round(percentage, 2))
            current_message = (
                "`[FILE - UPLOAD]`\n\n"
                " • `File Name :`"
                f"\n    `{file_name}`\n"
                " • `Status    :`\n"
                f"    {prog_str}"
            )
            if display_message != current_message:
                try:
                    await gdrive.edit(current_message)
                    display_message = current_message
                except Exception:
                    pass
    file_id = response.get("id")
    viewURL = response.get("webViewLink")
    downloadURL = response.get("webContentLink")
    """ - Change permission - """
    try:
        service.permissions().create(fileId=file_id, body=permission).execute()
    except HttpError as e:
        return await gdrive.edit("`" + str(e) + "`")
    await gdrive.edit(
        "`[FILE - UPLOAD]`\n\n"
        f" • `Name     :`\n    `{file_name}`\n"
        " • `Status   :` **OK**\n"
        f" • `URL      :` [{file_name}]({viewURL})\n"
        f" • `Download :` [{file_name}]({downloadURL})"
    )
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
            await gdrive.client.send_file(
                BOTLOG_CHATID, "auth.txt",
                caption=("This is your `G_DRIVE_AUTH_TOKEN_DATA`, "
                         "open then copy and paste to your heroku configvars."
                         "\nor you can do >`set var G_DRIVE_AUTH_TOKEN_DATA "
                         "<value inside auth.txt>`")
            )
    return creds


async def create_app(gdrive):
    """ - Create google drive service app - """
    creds = await generate_credentials(gdrive)
    service = build('drive', 'v3', credentials=creds, cache_discovery=False)
    return service


CMD_HELP.update({
    "gdrive":
    ">.`gd`"
    "\nUsage: Upload file into google drive"
    "\n\n>`.gdf mkdir <folder name>`"
    "\nUsage: create google drive folder"
    "\n\n>`.gdf rm <folder/file|name/id>`"
    "\nUsage: delete a file/folder, and can't be undone"
    "\nThis method skipping file trash, so be caution..."
})
