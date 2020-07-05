# Copyright (C) 2020 Adek Maulana
#
# SPDX-License-Identifier: GPL-3.0-or-later
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


""" - OUBnew Google Drive managers - """
import io
import os
import pickle
import base64
import json
import asyncio
import math
import time
import re
import requests
import logging

import userbot.modules.sql_helper.google_drive_sql as helper

from bs4 import BeautifulSoup
from os.path import isfile, isdir, join, getctime
from mimetypes import guess_type

from telethon import events

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

from userbot import (
    G_DRIVE_DATA, G_DRIVE_CLIENT_ID, G_DRIVE_CLIENT_SECRET,
    G_DRIVE_FOLDER_ID, BOTLOG_CHATID, TEMP_DOWNLOAD_DIRECTORY, CMD_HELP, LOGS,
)
from userbot.events import register
from userbot.utils import progress, humanbytes, time_formatter, human_to_bytes
from userbot.utils.exceptions import CancelProcess
from userbot.modules.aria import aria2, check_metadata
# =========================================================== #
#                          STATIC                             #
# =========================================================== #
GOOGLE_AUTH_URI = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URI = "https://oauth2.googleapis.com/token"
SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.metadata"
]
REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"
# =========================================================== #
#      STATIC CASE FOR G_DRIVE_FOLDER_ID IF VALUE IS URL      #
# =========================================================== #
__ = G_DRIVE_FOLDER_ID
if __ is not None:
    if "uc?id=" in G_DRIVE_FOLDER_ID:
        LOGS.info(
            "G_DRIVE_FOLDER_ID is not a valid folderURL...")
        G_DRIVE_FOLDER_ID = None
    try:
        G_DRIVE_FOLDER_ID = __.split("folders/")[1]
    except IndexError:
        try:
            G_DRIVE_FOLDER_ID = __.split("open?id=")[1]
        except IndexError:
            if "/view" in __:
                G_DRIVE_FOLDER_ID = __.split("/")[-2]
            else:
                try:
                    G_DRIVE_FOLDER_ID = __.split(
                        "folderview?id=")[1]
                except IndexError:
                    if any(map(str.isdigit, __)):
                        _1 = True
                    else:
                        _1 = False
                    if "-" in __ or "_" in __:
                        _2 = True
                    else:
                        _2 = False
                    if True in [_1 or _2]:
                        pass
                    else:
                        LOGS.info(
                            "G_DRIVE_FOLDER_ID "
                            "not a valid ID/URL...")
                        G_DRIVE_FOLDER_ID = None
# =========================================================== #
#                           LOG                               #
# =========================================================== #
logger = logging.getLogger('googleapiclient.discovery')
logger.setLevel(logging.ERROR)
# =========================================================== #
#                                                             #
# =========================================================== #


@register(pattern=r"^\.gdauth(?: |$)", outgoing=True)
async def generate_credentials(gdrive):
    """ - Only generate once for long run - """
    if helper.get_credentials(str(gdrive.from_id)) is not None:
        await gdrive.edit("`You already authorized token...`")
        await asyncio.sleep(1.5)
        return await gdrive.delete()
    """ - Generate credentials - """
    if G_DRIVE_DATA is not None:
        try:
            configs = json.loads(G_DRIVE_DATA)
        except json.JSONDecodeError:
            return await gdrive.edit(
                "`[AUTHENTICATE - ERROR]`\n\n"
                "`Status` : **BAD**\n"
                "`Reason` : **G_DRIVE_DATA** entity is not valid!"
            )
    else:
        """ - Only for old user - """
        if G_DRIVE_CLIENT_ID is None and G_DRIVE_CLIENT_SECRET is None:
            return await gdrive.edit(
                "`[AUTHENTICATE - ERROR]`\n\n"
                "`Status` : **BAD**\n"
                "`Reason` : please get your **G_DRIVE_DATA** "
                "[here](https://telegra.ph/How-To-Setup-Google-Drive-04-03)"
            )
        configs = {
            "installed": {
                "client_id": G_DRIVE_CLIENT_ID,
                "client_secret": G_DRIVE_CLIENT_SECRET,
                "auth_uri": GOOGLE_AUTH_URI,
                "token_uri": GOOGLE_TOKEN_URI,
            }
        }
    await gdrive.edit("`Creating credentials...`")
    flow = InstalledAppFlow.from_client_config(
        configs, SCOPES, redirect_uri=REDIRECT_URI)
    auth_url, _ = flow.authorization_url(
        access_type='offline', prompt='consent')
    msg = await gdrive.respond(
        "`Go to your BOTLOG group to authenticate token...`"
    )
    async with gdrive.client.conversation(BOTLOG_CHATID) as conv:
        url_msg = await conv.send_message(
            "Please go to this URL:\n"
            f"{auth_url}\nauthorize then reply the code"
        )
        r = conv.wait_event(
            events.NewMessage(outgoing=True, chats=BOTLOG_CHATID))
        r = await r
        code = r.message.message.strip()
        flow.fetch_token(code=code)
        creds = flow.credentials
        await asyncio.sleep(3.5)
        await gdrive.client.delete_messages(gdrive.chat_id, msg.id)
        await gdrive.client.delete_messages(BOTLOG_CHATID, [url_msg.id, r.id])
        """ - Unpack credential objects into strings - """
        creds = base64.b64encode(pickle.dumps(creds)).decode()
        await gdrive.edit("`Credentials created...`")
    helper.save_credentials(str(gdrive.from_id), creds)
    await gdrive.delete()
    return


async def create_app(gdrive):
    """ - Create google drive service app - """
    creds = helper.get_credentials(str(gdrive.from_id))
    if creds is not None:
        """ - Repack credential objects from strings - """
        creds = pickle.loads(
            base64.b64decode(creds.encode()))
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            await gdrive.edit("`Refreshing credentials...`")
            """ - Refresh credentials - """
            creds.refresh(Request())
            helper.save_credentials(str(
                gdrive.from_id), base64.b64encode(pickle.dumps(creds)).decode())
        else:
            await gdrive.edit("`Credentials is empty, please generate it...`")
            return False
    service = build('drive', 'v3', credentials=creds, cache_discovery=False)
    return service


@register(pattern=r"^\.gdreset(?: |$)", outgoing=True)
async def reset_credentials(gdrive):
    """ - Reset credentials or change account - """
    await gdrive.edit("`Resetting information...`")
    helper.clear_credentials(str(gdrive.from_id))
    await gdrive.edit("`Done...`")
    await asyncio.sleep(1)
    return await gdrive.delete()


async def get_raw_name(file_path):
    """ - Get file_name from file_path - """
    return file_path.split("/")[-1]


async def get_mimeType(name):
    """ - Check mimeType given file - """
    mimeType = guess_type(name)[0]
    if not mimeType:
        mimeType = 'text/plain'
    return mimeType


async def download(gdrive, service, uri=None):
    global is_cancelled
    reply = ''
    """ - Download files to local then upload - """
    if not isdir(TEMP_DOWNLOAD_DIRECTORY):
        os.makedirs(TEMP_DOWNLOAD_DIRECTORY)
        required_file_name = None
    if uri:
        full_path = os.getcwd() + TEMP_DOWNLOAD_DIRECTORY.strip('.')
        if isfile(uri) and uri.endswith(".torrent"):
            downloads = aria2.add_torrent(
                uri,
                uris=None,
                options={'dir': full_path},
                position=None)
        else:
            uri = [uri]
            downloads = aria2.add_uris(
                uri,
                options={'dir': full_path},
                position=None)
        gid = downloads.gid
        await check_progress_for_dl(gdrive, gid, previous=None)
        file = aria2.get_download(gid)
        filename = file.name
        if file.followed_by_ids:
            new_gid = await check_metadata(gid)
            await check_progress_for_dl(gdrive, new_gid, previous=None)
        try:
            required_file_name = TEMP_DOWNLOAD_DIRECTORY + filenames
        except Exception:
            required_file_name = TEMP_DOWNLOAD_DIRECTORY + filename
    else:
        try:
            current_time = time.time()
            is_cancelled = False
            downloaded_file_name = await gdrive.client.download_media(
                await gdrive.get_reply_message(),
                TEMP_DOWNLOAD_DIRECTORY,
                progress_callback=lambda d, t: asyncio.get_event_loop(
                ).create_task(progress(d, t, gdrive, current_time,
                                       "[FILE - DOWNLOAD]",
                                       is_cancelled=is_cancelled)))
        except CancelProcess:
            names = []
            for name in os.listdir(TEMP_DOWNLOAD_DIRECTORY):
                names.append(join(TEMP_DOWNLOAD_DIRECTORY, name))
            """ asumming newest files are the cancelled one """
            newest = max(names, key=getctime)
            os.remove(newest)
            reply += (
                "`[FILE - CANCELLED]`\n\n"
                "`Status` : **OK** - received signal cancelled."
            )
            return reply
        else:
            required_file_name = downloaded_file_name
    try:
        file_name = await get_raw_name(required_file_name)
    except AttributeError:
        reply += (
            "`[ENTRY - ERROR]`\n\n"
            "`Status` : **BAD**\n"
        )
        return reply
    mimeType = await get_mimeType(required_file_name)
    try:
        status = "[FILE - UPLOAD]"
        if isfile(required_file_name):
            try:
                result = await upload(
                    gdrive, service, required_file_name, file_name, mimeType)
            except CancelProcess:
                reply += (
                    "`[FILE - CANCELLED]`\n\n"
                    "`Status` : **OK** - received signal cancelled."
                )
                return reply
            else:
                reply += (
                    f"`{status}`\n\n"
                    f"`Name   :` `{file_name}`\n"
                    f"`Size   :` `{humanbytes(result[0])}`\n"
                    f"`Link   :` [{file_name}]({result[1]})\n"
                    "`Status :` **OK** - Successfully uploaded.\n\n"
                )
                return reply
        else:
            status = status.replace("[FILE", "[FOLDER")
            global parent_Id
            folder = await create_dir(service, file_name)
            parent_Id = folder.get('id')
            webViewURL = (
                "https://drive.google.com/drive/folders/"
                + parent_Id
            )
            try:
                await task_directory(gdrive, service, required_file_name)
            except CancelProcess:
                reply += (
                    "`[FOLDER - CANCELLED]`\n\n"
                    "`Status` : **OK** - received signal cancelled."
                )
                await reset_parentId()
                return reply
            except Exception:
                await reset_parentId()
            else:
                reply += (
                    f"`{status}`\n\n"
                    f"[{file_name}]({webViewURL})\n"
                    "`Status` : **OK** - Successfully uploaded.\n\n"
                )
                await reset_parentId()
                return reply
    except Exception as e:
        status = status.replace("DOWNLOAD]", "ERROR]")
        reply += (
            f"`{status}`\n\n"
            "`Status` : **failed**\n"
            f"`Reason` : `{str(e)}`\n\n"
        )
        return reply
    return


async def download_gdrive(gdrive, service, uri):
    reply = ''
    global is_cancelled
    """ - remove drivesdk and export=download from link - """
    if not isdir(TEMP_DOWNLOAD_DIRECTORY):
        os.mkdir(TEMP_DOWNLOAD_DIRECTORY)
    if "&export=download" in uri:
        uri = uri.split("&export=download")[0]
    elif "file/d/" in uri and "/view" in uri:
        uri = uri.split("?usp=drivesdk")[0]
    try:
        file_Id = uri.split("uc?id=")[1]
    except IndexError:
        try:
            file_Id = uri.split("open?id=")[1]
        except IndexError:
            if "/view" in uri:
                file_Id = uri.split("/")[-2]
            else:
                try:
                    file_Id = uri.split("uc?export=download&confirm="
                                        )[1].split("id=")[1]
                except IndexError:
                    """ - if error parse in url, assume given value is Id - """
                    file_Id = uri
    try:
        file = await get_information(service, file_Id)
    except HttpError as e:
        if '404' in str(e):
            drive = 'https://drive.google.com'
            url = f'{drive}/uc?export=download&id={file_Id}'

            session = requests.session()
            download = session.get(url, stream=True)

            try:
                download.headers['Content-Disposition']
            except KeyError:
                page = BeautifulSoup(download.content, 'lxml')
                try:
                    export = drive + page.find('a', {'id': 'uc-download-link'}
                                               ).get('href')
                except AttributeError:
                    try:
                        error = (
                            page.find('p', {'class': 'uc-error-caption'}).text
                            + '\n' +
                            page.find('p', {'class': 'uc-error-subcaption'}
                                      ).text
                        )
                    except Exception:
                        reply += (
                            "`[FILE - ERROR]`\n\n"
                            "`Status` : **BAD** - failed to download.\n"
                            "`Reason` : uncaught err."
                        )
                    else:
                        reply += (
                            "`[FILE - ERROR]`\n\n"
                            "`Status` : **BAD** - failed to download.\n"
                            f"`Reason` : {error}"
                        )
                    return reply
                download = session.get(export, stream=True)
                file_size = human_to_bytes(
                    page.find('span', {'class': 'uc-name-size'}
                              ).text.split()[-1].strip('()'))
            else:
                file_size = int(download.headers['Content-Length'])

            file_name = re.search(
                'filename="(.*)"', download.headers["Content-Disposition"]
            ).group(1)
            file_path = TEMP_DOWNLOAD_DIRECTORY + file_name
            with io.FileIO(file_path, 'wb') as files:
                CHUNK_SIZE = None
                current_time = time.time()
                display_message = None
                first = True
                is_cancelled = False
                for chunk in download.iter_content(CHUNK_SIZE):
                    if is_cancelled is True:
                        raise CancelProcess

                    if not chunk:
                        break

                    diff = time.time() - current_time
                    if first is True:
                        downloaded = len(chunk)
                        first = False
                    else:
                        downloaded += len(chunk)
                    percentage = downloaded / file_size * 100
                    speed = round(downloaded / diff, 2)
                    eta = round((file_size - downloaded) / speed)
                    prog_str = "`Downloading` | [{0}{1}] `{2}%`".format(
                        "".join(["▰" for i in range(
                                math.floor(percentage / 10))]),
                        "".join(["▱"for i in range(
                                10 - math.floor(percentage / 10))]),
                        round(percentage, 2))
                    current_message = (
                        "`[FILE - DOWNLOAD]`\n\n"
                        f"`{file_name}`\n"
                        f"`Status`\n{prog_str}\n"
                        f"`{humanbytes(downloaded)} of {humanbytes(file_size)}"
                        f" @ {humanbytes(speed)}`\n"
                        f"`ETA` -> {time_formatter(eta)}"
                    )
                    if round(
                            diff % 15.00) == 0 and (display_message
                                                    != current_message) or (
                            downloaded == file_size):
                        await gdrive.edit(current_message)
                        display_message = current_message
                    files.write(chunk)
    else:
        file_name = file.get('name')
        mimeType = file.get('mimeType')
        if mimeType == 'application/vnd.google-apps.folder':
            return await gdrive.edit("`Aborting, folder download not support`")
        file_path = TEMP_DOWNLOAD_DIRECTORY + file_name
        request = service.files().get_media(fileId=file_Id)
        with io.FileIO(file_path, 'wb') as df:
            downloader = MediaIoBaseDownload(df, request)
            complete = False
            is_cancelled = False
            current_time = time.time()
            display_message = None
            while complete is False:
                if is_cancelled is True:
                    raise CancelProcess

                status, complete = downloader.next_chunk()
                if status:
                    file_size = status.total_size
                    diff = time.time() - current_time
                    downloaded = status.resumable_progress
                    percentage = downloaded / file_size * 100
                    speed = round(downloaded / diff, 2)
                    eta = round((file_size - downloaded) / speed)
                    prog_str = "`Downloading` | [{0}{1}] `{2}%`".format(
                        "".join(["▰" for i in range(
                                math.floor(percentage / 10))]),
                        "".join(["▱" for i in range(
                                10 - math.floor(percentage / 10))]),
                        round(percentage, 2))
                    current_message = (
                        "`[FILE - DOWNLOAD]`\n\n"
                        f"`{file_name}`\n"
                        f"`Status`\n{prog_str}\n"
                        f"`{humanbytes(downloaded)} of {humanbytes(file_size)}"
                        f" @ {humanbytes(speed)}`\n"
                        f"`ETA` -> {time_formatter(eta)}"
                    )
                    if round(
                            diff % 15.00) == 0 and (display_message
                                                    != current_message) or (
                            downloaded == file_size):
                        await gdrive.edit(current_message)
                        display_message = current_message
    await gdrive.edit(
        "`[FILE - DOWNLOAD]`\n\n"
        f"`Name   :` `{file_name}`\n"
        f"`Size   :` `{humanbytes(file_size)}`\n"
        f"`Path   :` `{file_path}`\n"
        "`Status :` **OK** - Successfully downloaded."
    )
    msg = await gdrive.respond("`Answer the question in your BOTLOG group`")
    async with gdrive.client.conversation(BOTLOG_CHATID) as conv:
        ask = await conv.send_message("`Proceed with mirroring? [y/N]`")
        try:
            r = conv.wait_event(
                events.NewMessage(outgoing=True, chats=BOTLOG_CHATID))
            r = await r
        except Exception:
            ans = 'N'
        else:
            ans = r.message.message.strip()
            await gdrive.client.delete_messages(BOTLOG_CHATID, r.id)
        await gdrive.client.delete_messages(gdrive.chat_id, msg.id)
        await gdrive.client.delete_messages(BOTLOG_CHATID, ask.id)
    if ans.capitalize() == 'N':
        return reply
    elif ans.capitalize() == "Y":
        try:
            result = await upload(
                gdrive, service, file_path, file_name, mimeType)
        except CancelProcess:
            reply += (
                "`[FILE - CANCELLED]`\n\n"
                "`Status` : **OK** - received signal cancelled."
            )
        else:
            reply += (
                "`[FILE - UPLOAD]`\n\n"
                f"`Name   :` `{file_name}`\n"
                f"`Size   :` `{humanbytes(result[0])}`\n"
                f"`Link   :` [{file_name}]({result[1]})\n"
                "`Status :` **OK**\n\n"
            )
        return reply
    else:
        await gdrive.client.send_message(
            BOTLOG_CHATID,
            "`Invalid answer type [Y/N] only...`"
        )
        return reply


async def change_permission(service, Id):
    permission = {
        "role": "reader",
        "type": "anyone",
        "allowFileDiscovery": True,
        "value": None,
    }
    try:
        service.permissions().create(fileId=Id, body=permission
                                     ).execute()
    except Exception:
        pass
    return True


async def get_information(service, Id):
    r = service.files().get(fileId=Id, fields="name, id, size, mimeType, "
                            "webViewLink, webContentLink,"
                            "description").execute()
    return r


async def create_dir(service, folder_name):
    metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
    }
    try:
        if parent_Id is not None:
            pass
    except NameError:
        """ - Fallback to G_DRIVE_FOLDER_ID else root dir - """
        if G_DRIVE_FOLDER_ID is not None:
            metadata['parents'] = [G_DRIVE_FOLDER_ID]
    else:
        """ - Override G_DRIVE_FOLDER_ID because parent_Id not empty - """
        metadata['parents'] = [parent_Id]
    folder = service.files().create(
        body=metadata, fields="id, webViewLink").execute()
    try:
        await change_permission(service, folder.get('id'))
    except Exception:
        pass
    return folder


async def upload(gdrive, service, file_path, file_name, mimeType):
    try:
        await gdrive.edit("`Processing upload...`")
    except Exception:
        pass
    body = {
        "name": file_name,
        "description": "Uploaded from Telegram using ProjectBish userbot.",
        "mimeType": mimeType,
    }
    try:
        if parent_Id is not None:
            pass
    except NameError:
        """ - Fallback to G_DRIVE_FOLDER_ID else root dir - """
        if G_DRIVE_FOLDER_ID is not None:
            body['parents'] = [G_DRIVE_FOLDER_ID]
    else:
        """ - Override G_DRIVE_FOLDER_ID because parent_Id not empty - """
        body['parents'] = [parent_Id]
    media_body = MediaFileUpload(
        file_path,
        mimetype=mimeType,
        resumable=True
    )
    """ - Start upload process - """
    file = service.files().create(body=body, media_body=media_body,
                                  fields="id, size, webContentLink")
    global is_cancelled
    current_time = time.time()
    response = None
    display_message = None
    is_cancelled = False
    while response is None:
        if is_cancelled is True:
            raise CancelProcess

        status, response = file.next_chunk()
        if status:
            file_size = status.total_size
            diff = time.time() - current_time
            uploaded = status.resumable_progress
            percentage = uploaded / file_size * 100
            speed = round(uploaded / diff, 2)
            eta = round((file_size - uploaded) / speed)
            prog_str = "`Uploading` | [{0}{1}] `{2}%`".format(
                "".join(["▰" for i in range(
                        math.floor(percentage / 10))]),
                "".join(["▱" for i in range(
                        10 - math.floor(percentage / 10))]),
                round(percentage, 2))
            current_message = (
                "`[FILE - UPLOAD]`\n\n"
                f"`{file_name}`\n"
                f"`Status`\n{prog_str}\n"
                f"`{humanbytes(uploaded)} of {humanbytes(file_size)} "
                f"@ {humanbytes(speed)}`\n"
                f"`ETA` -> {time_formatter(eta)}"
            )
            if round(diff % 15.00) == 0 and (
                    display_message != current_message) or (
                    uploaded == file_size):
                await gdrive.edit(current_message)
                display_message = current_message
    file_id = response.get("id")
    file_size = response.get("size")
    downloadURL = response.get("webContentLink")
    """ - Change permission - """
    try:
        await change_permission(service, file_id)
    except Exception:
        pass
    return int(file_size), downloadURL


async def task_directory(gdrive, service, folder_path):
    global parent_Id
    global is_cancelled
    is_cancelled = False
    lists = os.listdir(folder_path)
    if len(lists) == 0:
        return parent_Id
    root_parent_Id = None
    for f in lists:
        if is_cancelled is True:
            raise CancelProcess

        current_f_name = join(folder_path, f)
        if isdir(current_f_name):
            folder = await create_dir(service, f)
            parent_Id = folder.get('id')
            root_parent_Id = await task_directory(gdrive,
                                                  service, current_f_name)
        else:
            file_name = await get_raw_name(current_f_name)
            mimeType = await get_mimeType(current_f_name)
            await upload(gdrive, service, current_f_name, file_name, mimeType)
            root_parent_Id = parent_Id
    return root_parent_Id


async def reset_parentId():
    global parent_Id
    try:
        if parent_Id is not None:
            pass
    except NameError:
        if G_DRIVE_FOLDER_ID is not None:
            parent_Id = G_DRIVE_FOLDER_ID
    else:
        del parent_Id
    return


@register(pattern=r"^\.gdlist(?: |$)(-l \d+)?(?: |$)?(.*)?(?: |$)",
          outgoing=True)
async def lists(gdrive):
    await gdrive.edit("`Getting information...`")
    checker = gdrive.pattern_match.group(1)
    if checker is not None:
        page_size = int(gdrive.pattern_match.group(1).strip('-l '))
        if page_size > 1000:
            await gdrive.edit(
                "`[GDRIVE - LIST]`\n\n"
                "`Status` : **BAD**\n"
                "`Reason` : can't get list if limit more than 1000."
            )
            return
    else:
        page_size = 50  # default page_size is 50
    checker = gdrive.pattern_match.group(2)
    if checker != '':
        if checker.startswith('-p'):
            parents = checker.split(None, 2)[1]
            try:
                name = checker.split(None, 2)[2]
            except IndexError:
                query = f"'{parents}' in parents and (name contains '*')"
            else:
                query = f"'{parents}' in parents and (name contains '{name}')"
        else:
            if re.search('-p (.*)', checker):
                parents = re.search('-p (.*)', checker).group(1)
                name = checker.split('-p')[0].strip()
                query = f"'{parents}' in parents and (name contains '{name}')"
            else:
                name = checker
                query = f"name contains '{name}'"
    else:
        query = ''
    service = await create_app(gdrive)
    if service is False:
        return False
    message = ''
    fields = ('nextPageToken, files(name, id, '
              'mimeType, webViewLink, webContentLink)')
    page_token = None
    result = []
    while True:
        try:
            response = service.files().list(
                supportsTeamDrives=True,
                includeTeamDriveItems=True,
                q=query,
                spaces='drive',
                corpora='allDrives',
                fields=fields,
                pageSize=page_size,
                orderBy='modifiedTime desc, folder',
                pageToken=page_token
            ).execute()
        except HttpError as e:
            await gdrive.edit(
                "`[GDRIVE - LIST]`\n\n"
                "`Status` : **BAD**\n"
                f"`Reason` : {str(e)}"
            )
            return
        for files in response.get('files', []):
            if len(result) >= page_size:
                break

            file_name = files.get('name')
            file_id = files.get('id')
            if files.get('mimeType') == 'application/vnd.google-apps.folder':
                link = files.get('webViewLink')
                message += (
                    f"`[FOLDER]` - `{file_id}`\n"
                    f"`{file_name}`\n{link}\n\n"
                )
            else:
                link = files.get('webContentLink')
                message += (
                    f"`[FILE]` - `{file_id}`\n"
                    f"`{file_name}`\n{link}\n\n"
                )
            result.append(files)
        if len(result) >= page_size:
            break

        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break

    del result
    if query == '':
        query = 'Not specified'
    if len(message) > 4096:
        await gdrive.edit("`Result is too big, sending it as file...`")
        with open('result.txt', 'w') as r:
            r.write(
                f"Google Drive Query:\n{query}\n\nResults\n\n{message}")
        await gdrive.client.send_file(
            gdrive.chat_id,
            'result.txt',
            caption='Google Drive Query List.'
        )
    else:
        await gdrive.edit(
            "**Google Drive Query**:\n"
            f"`{query}`\n\n**Results**\n\n{message}")
    return


@register(pattern=r"^\.gdf (mkdir|rm|chck) (.*)", outgoing=True)
async def google_drive_managers(gdrive):
    """ - Google Drive folder/file management - """
    await gdrive.edit("`Sending information...`")
    service = await create_app(gdrive)
    if service is False:
        return
    """ - Split name if contains spaces by using ; - """
    f_name = gdrive.pattern_match.group(2).split(';')
    exe = gdrive.pattern_match.group(1)
    reply = ''
    for name_or_id in f_name:
        """ - in case given name has a space beetween ; - """
        name_or_id = name_or_id.strip()
        metadata = {
            'name': name_or_id,
            'mimeType': 'application/vnd.google-apps.folder',
        }
        try:
            if parent_Id is not None:
                pass
        except NameError:
            """ - Fallback to G_DRIVE_FOLDER_ID else to root dir - """
            if G_DRIVE_FOLDER_ID is not None:
                metadata['parents'] = [G_DRIVE_FOLDER_ID]
        else:
            """ - Override G_DRIVE_FOLDER_ID because parent_Id not empty - """
            metadata['parents'] = [parent_Id]
        page_token = None
        result = service.files().list(
            q=f'name="{name_or_id}"',
            spaces='drive',
            fields=(
                'nextPageToken, files(parents, name, id, size, '
                'mimeType, webViewLink, webContentLink, description)'
            ),
            pageToken=page_token
        ).execute()
        if exe == "mkdir":
            """
            - Create a directory, abort if exist when parent not given -
            """
            status = "[FOLDER - EXIST]"
            try:
                folder = result.get('files', [])[0]
            except IndexError:
                folder = await create_dir(service, name_or_id)
                status = status.replace("EXIST]", "CREATED]")
            folder_id = folder.get('id')
            webViewURL = folder.get('webViewLink')
            if "CREATED" in status:
                """ - Change permission - """
                try:
                    await change_permission(service, folder_id)
                except Exception:
                    pass
            reply += (
                f"`{status}`\n\n"
                f"`{name_or_id}`\n"
                f"`ID  :` `{folder_id}`\n"
                f"`URL :` [Open]({webViewURL})\n\n"
            )
        elif exe == "rm":
            """ - Permanently delete, skipping the trash - """
            try:
                """ - Try if given value is a name not a folderId/fileId - """
                f = result.get('files', [])[0]
                f_id = f.get('id')
            except IndexError:
                """ - If failed assumming value is folderId/fileId - """
                f_id = name_or_id
                try:
                    f = await get_information(service, f_id)
                except Exception as e:
                    reply += (
                        f"`[FILE/FOLDER - ERROR]`\n\n"
                        "`Status` : **BAD**"
                        f"`Reason` : `{str(e)}`\n\n"
                    )
                    continue
            name = f.get('name')
            mimeType = f.get('mimeType')
            if mimeType == 'application/vnd.google-apps.folder':
                status = "[FOLDER - DELETE]"
            else:
                status = "[FILE - DELETE]"
            try:
                service.files().delete(fileId=f_id).execute()
            except HttpError as e:
                status.replace("DELETE]", "ERROR]")
                reply += (
                    f"`{status}`\n\n"
                    "`Status` : **BAD**"
                    f"`Reason` : {str(e)}\n\n"
                )
                continue
            else:
                reply += (
                    f"`{status}`\n\n"
                    f"`{name}`\n"
                    "`Status` : **OK**\n\n"
                )
        elif exe == "chck":
            """ - Check file/folder if exists - """
            try:
                f = result.get('files', [])[0]
            except IndexError:
                """ - If failed assumming value is folderId/fileId - """
                f_id = name_or_id
                try:
                    f = await get_information(service, f_id)
                except Exception as e:
                    reply += (
                        "`[FILE/FOLDER - ERROR]`\n\n"
                        "`Status` : **BAD**\n"
                        f"`Reason` : `{str(e)}`\n\n"
                    )
                    continue
            """ - If exists parse file/folder information - """
            name_or_id = f.get('name')  # override input value
            f_id = f.get('id')
            f_size = f.get('size')
            mimeType = f.get('mimeType')
            webViewLink = f.get('webViewLink')
            downloadURL = f.get('webContentLink')
            description = f.get('description')
            if mimeType == "application/vnd.google-apps.folder":
                status = "[FOLDER - EXIST]"
            else:
                status = "[FILE - EXIST]"
            msg = (
                f"`{status}`\n\n"
                f"`Name  :` `{name_or_id}`\n"
                f"`ID    :` `{f_id}`\n"
            )
            if mimeType != "application/vnd.google-apps.folder":
                msg += f"`Size  :` `{humanbytes(f_size)}`\n"
                msg += f"`Link  :` [{name_or_id}]({downloadURL})\n\n"
            else:
                msg += f"`URL   :` [Open]({webViewLink})\n\n"
            if description:
                msg += f"`About :`\n`{description}`\n\n"
            reply += msg
        page_token = result.get('nextPageToken', None)
    await gdrive.edit(reply)
    return


@register(pattern=r"^\.gdabort(?: |$)", outgoing=True)
async def cancel_process(gdrive):
    """
       Abort process for download and upload
    """
    global is_cancelled
    downloads = aria2.get_downloads()
    await gdrive.edit("`Cancelling...`")
    if len(downloads) != 0:
        aria2.remove_all(force=True)
        aria2.autopurge()
    is_cancelled = True
    await asyncio.sleep(3.5)
    await gdrive.delete()


@register(pattern=r"^\.gd(?: |$)(.*)", outgoing=True)
async def google_drive(gdrive):
    reply = ''
    """ - Parsing all google drive function - """
    value = gdrive.pattern_match.group(1)
    file_path = None
    uri = None
    if not value and not gdrive.reply_to_msg_id:
        return
    elif value and gdrive.reply_to_msg_id:
        return await gdrive.edit(
            "`[UNKNOWN - ERROR]`\n\n"
            "`Status` : **failed**\n"
            "`Reason` : Confused to upload file or the replied message/media."
        )
    service = await create_app(gdrive)
    if service is False:
        return
    if isfile(value):
        file_path = value
        if file_path.endswith(".torrent"):
            uri = [file_path]
            file_path = None
    elif isdir(value):
        folder_path = value
        global parent_Id
        folder_name = await get_raw_name(folder_path)
        folder = await create_dir(service, folder_name)
        parent_Id = folder.get('id')
        webViewURL = "https://drive.google.com/drive/folders/" + parent_Id
        try:
            await task_directory(gdrive, service, folder_path)
        except CancelProcess:
            await gdrive.respond(
                "`[FOLDER - CANCELLED]`\n\n"
                "`Status` : **OK** - received signal cancelled."
            )
            await reset_parentId()
            return await gdrive.delete()
        except Exception as e:
            await gdrive.edit(
                "`[FOLDER - UPLOAD]`\n\n"
                f"`{folder_name}`\n"
                "`Status` : **BAD**\n"
                f"`Reason` : {str(e)}"
            )
            return await reset_parentId()
        else:
            await gdrive.edit(
                "`[FOLDER - UPLOAD]`\n\n"
                f"[{folder_name}]({webViewURL})\n"
                "`Status` : **OK** - Successfully uploaded.\n\n"
            )
            return await reset_parentId()
    elif not value and gdrive.reply_to_msg_id:
        reply += await download(gdrive, service)
        await gdrive.respond(reply)
        return await gdrive.delete()
    else:
        if re.findall(r'\bhttps?://drive\.google\.com\S+', value):
            """ - Link is google drive fallback to download - """
            value = re.findall(r'\bhttps?://drive\.google\.com\S+', value)
            for uri in value:
                try:
                    reply += await download_gdrive(gdrive, service, uri)
                except CancelProcess:
                    reply += (
                        "`[FILE - CANCELLED]`\n\n"
                        "`Status` : **OK** - received signal cancelled."
                    )
                    break
                except Exception as e:
                    reply += (
                        "`[FILE - ERROR]`\n\n"
                        "`Status` : **BAD**\n"
                        f"`Reason` : {str(e)}\n\n"
                    )
                    continue
            if reply:
                await gdrive.respond(reply, link_preview=False)
                return await gdrive.delete()
            else:
                return
        elif re.findall(r'\bhttps?://.*\.\S+', value) or "magnet:?" in value:
            uri = value.split()
        else:
            for fileId in value.split():
                if any(map(str.isdigit, fileId)):
                    one = True
                else:
                    one = False
                if "-" in fileId or "_" in fileId:
                    two = True
                else:
                    two = False
                if True in [one or two]:
                    try:
                        reply += await download_gdrive(gdrive, service, fileId)
                    except CancelProcess:
                        reply += (
                            "`[FILE - CANCELLED]`\n\n"
                            "`Status` : **OK** - received signal cancelled."
                        )
                        break
                    except Exception as e:
                        reply += (
                            "`[FILE - ERROR]`\n\n"
                            "`Status` : **BAD**\n"
                            f"`Reason` : {str(e)}\n\n"
                        )
                        continue
            if reply:
                await gdrive.respond(reply, link_preview=False)
                return await gdrive.delete()
            else:
                return
        if not uri and not gdrive.reply_to_msg_id:
            return await gdrive.edit(
                "`[VALUE - ERROR]`\n\n"
                "`Status` : **BAD**\n"
                "`Reason` : given value is not URL nor file/folder path. "
                "If you think this is wrong, maybe you use .gd with multiple "
                "value of files/folders, e.g `.gd <filename1> <filename2>` "
                "for upload from files/folders path this doesn't support it."
            )
    if uri and not gdrive.reply_to_msg_id:
        for dl in uri:
            try:
                reply += await download(gdrive, service, dl)
            except Exception as e:
                if " not found" in str(e) or "'file'" in str(e):
                    reply += (
                        "`[FILE - CANCELLED]`\n\n"
                        "`Status` : **OK** - received signal cancelled."
                    )
                    await asyncio.sleep(2.5)
                    break
                else:
                    """ - if something bad happened, continue to next uri - """
                    reply += (
                        "`[UNKNOWN - ERROR]`\n\n"
                        "`Status` : **BAD**\n"
                        f"`Reason` : `{dl}` | `{str(e)}`\n\n"
                    )
                    continue
        await gdrive.respond(reply, link_preview=False)
        return await gdrive.delete()
    mimeType = await get_mimeType(file_path)
    file_name = await get_raw_name(file_path)
    try:
        result = await upload(gdrive, service,
                              file_path, file_name, mimeType)
    except CancelProcess:
        gdrive.respond(
            "`[FILE - CANCELLED]`\n\n"
            "`Status` : **OK** - received signal cancelled."
        )
    if result:
        await gdrive.respond(
            "`[FILE - UPLOAD]`\n\n"
            f"`Name   :` `{file_name}`\n"
            f"`Size   :` `{humanbytes(result[0])}`\n"
            f"`Link   :` [{file_name}]({result[1]})\n"
            "`Status :` **OK** - Successfully uploaded.\n",
            link_preview=False
        )
    await gdrive.delete()
    return


@register(pattern=r"^\.gdfset (put|rm)(?: |$)(.*)", outgoing=True)
async def set_upload_folder(gdrive):
    """ - Set parents dir for upload/check/makedir/remove - """
    await gdrive.edit("`Sending information...`")
    global parent_Id
    exe = gdrive.pattern_match.group(1)
    if exe == "rm":
        if G_DRIVE_FOLDER_ID is not None:
            parent_Id = G_DRIVE_FOLDER_ID
            return await gdrive.edit(
                "`[FOLDER - SET]`\n\n"
                "`Status` : **OK** - using `G_DRIVE_FOLDER_ID` now."
            )
        else:
            try:
                del parent_Id
            except NameError:
                return await gdrive.edit(
                    "`[FOLDER - SET]`\n\n"
                    "`Status` : **BAD** - No parent_Id is set."
                )
            else:
                return await gdrive.edit(
                    "`[FOLDER - SET]`\n\n"
                    "`Status` : **OK**"
                    " - `G_DRIVE_FOLDER_ID` empty, will use root."
                )
    inp = gdrive.pattern_match.group(2)
    if not inp:
        return await gdrive.edit(">`.gdfset put <folderURL/folderID>`")
    """ - Value for .gdfset (put|rm) can be folderId or folder link - """
    try:
        ext_id = re.findall(r'\bhttps?://drive\.google\.com\S+', inp)[0]
    except IndexError:
        """ - if given value isn't folderURL assume it's an Id - """
        if any(map(str.isdigit, inp)):
            c1 = True
        else:
            c1 = False
        if "-" in inp or "_" in inp:
            c2 = True
        else:
            c2 = False
        if True in [c1 or c2]:
            parent_Id = inp
            return await gdrive.edit(
                "`[PARENT - FOLDER]`\n\n"
                "`Status` : **OK** - Successfully changed."
            )
        else:
            await gdrive.edit(
                "`[PARENT - FOLDER]`\n\n"
                "`Status` : **WARNING** - forcing use..."
            )
            parent_Id = inp
    else:
        if "uc?id=" in ext_id:
            return await gdrive.edit(
                "`[URL - ERROR]`\n\n"
                "`Status` : **BAD** - Not a valid folderURL."
            )
        try:
            parent_Id = ext_id.split("folders/")[1]
        except IndexError:
            """ - Try catch again if URL open?id= - """
            try:
                parent_Id = ext_id.split("open?id=")[1]
            except IndexError:
                if "/view" in ext_id:
                    parent_Id = ext_id.split("/")[-2]
                else:
                    try:
                        parent_Id = ext_id.split("folderview?id=")[1]
                    except IndexError:
                        return await gdrive.edit(
                            "`[URL - ERROR]`\n\n"
                            "`Status` : **BAD** - Not a valid folderURL."
                        )
        await gdrive.edit(
            "`[PARENT - FOLDER]`\n\n"
            "`Status` : **OK** - Successfully changed."
        )
    return


async def check_progress_for_dl(gdrive, gid, previous):
    complete = None
    global is_cancelled
    global filenames
    is_cancelled = False
    while not complete:
        if is_cancelled is True:
            raise CancelProcess

        file = aria2.get_download(gid)
        complete = file.is_complete
        try:
            filenames = file.name
        except IndexError:
            pass
        try:
            if not complete and not file.error_message:
                percentage = int(file.progress)
                downloaded = percentage * int(file.total_length) / 100
                prog_str = "`Downloading` | [{0}{1}] `{2}`".format(
                    "".join(["▰" for i in range(
                            math.floor(percentage / 10))]),
                    "".join(["▱" for i in range(
                            10 - math.floor(percentage / 10))]),
                    file.progress_string())
                msg = (
                    "`[URI - DOWNLOAD]`\n\n"
                    f"`{file.name}`\n"
                    f"`Status` -> **{file.status.capitalize()}**\n"
                    f"{prog_str}\n"
                    f"`{humanbytes(downloaded)} of"
                    f" {file.total_length_string()}"
                    f" @ {file.download_speed_string()}`\n"
                    f"`ETA` -> {file.eta_string()}\n"
                )
                if msg != previous or downloaded == file.total_length_string():
                    await gdrive.edit(msg)
                    msg = previous
            else:
                await gdrive.edit(f"`{msg}`")
            await asyncio.sleep(15)
            await check_progress_for_dl(gdrive, gid, previous)
            file = aria2.get_download(gid)
            complete = file.is_complete
            if complete:
                return await gdrive.edit(f"`{file.name}`\n\n"
                                         "Successfully downloaded...")
        except Exception as e:
            if " depth exceeded" in str(e):
                file.remove(force=True)
                try:
                    await gdrive.edit(
                        "`[URI - DOWNLOAD]`\n\n"
                        f"`{file.name}`\n"
                        "`Status` : **failed**\n"
                        "`Reason` : Auto cancelled download, URI/Torrent dead."
                    )
                except Exception:
                    pass


CMD_HELP.update({
    "gdrive":
    ">`.gdauth`"
    "\nUsage: generate token to enable all cmd google drive service."
    "\nThis only need to run once in life time."
    "\n\n>`.gdreset`"
    "\nUsage: reset your token if something bad happened or change drive acc."
    "\n\n>`.gd`"
    "\nUsage: Upload file from local or uri/url/drivelink into google drive."
    "\nfor drivelink it's upload only if you want to."
    "\n\n>`.gdabort`"
    "\nUsage: Abort process uploading or downloading."
    "\n\n>`.gdlist`"
    "\nUsage: Get list of folders and files with default size 50."
    "\nUse flags `-l range[1-1000]` for limit output."
    "\nUse flags `-p parents-folder_id` for lists given folder in gdrive."
    "\n\n>`.gdf mkdir`"
    "\nUsage: Create gdrive folder."
    "\n\n>`.gdf chck`"
    "\nUsage: Check file/folder in gdrive."
    "\n\n>`.gdf rm`"
    "\nUsage: Delete files/folders in gdrive."
    "\nCan't be undone, this method skipping file trash, so be caution..."
    "\n\n>`.gdfset put`"
    "\nUsage: Change upload directory in gdrive."
    "\n\n>`.gdfset rm`"
    "\nUsage: remove set parentId from cmd\n>`.gdfset put` "
    "into **G_DRIVE_FOLDER_ID** and if empty upload will go to root."
    "\n\nNOTE:"
    "\nfor >`.gdlist` you can combine -l and -p flags with or without name "
    "at the same time, it must be `-l` flags first before use `-p` flags.\n"
    "And by default it lists from latest 'modifiedTime' and then folders."
})
