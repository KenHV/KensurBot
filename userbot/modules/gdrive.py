# Special thanks to @spechide & @Zero_cool7870 & @Prakaska :)
# The entire code given below is verbatim copied from
# https://github.com/cyberboysumanjay/Gdrivedownloader/blob/master/gdrive_upload.py
# there might be some changes made to suit the needs for this repository
# Licensed under MIT License

import asyncio
import math
import os
import time
from telethon import events
from datetime import datetime
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from apiclient.errors import ResumableUploadError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage
from oauth2client import file, client, tools
from userbot import (G_DRIVE_CLIENT_ID, G_DRIVE_CLIENT_SECRET, G_DRIVE_AUTH_TOKEN_DATA, GDRIVE_FOLDER_ID, BOTLOG_CHATID, TEMP_DOWNLOAD_DIRECTORY, CMD_HELP, LOGS)
from userbot.events import register
from mimetypes import guess_type
import httplib2
import subprocess

# Path to token json file, it should be in same directory as script
G_DRIVE_TOKEN_FILE = "./auth_token.txt"
# Copy your credentials from the APIs Console
CLIENT_ID = G_DRIVE_CLIENT_ID
CLIENT_SECRET = G_DRIVE_CLIENT_SECRET
# Check https://developers.google.com/drive/scopes for all available scopes
OAUTH_SCOPE = "https://www.googleapis.com/auth/drive.file"
# Redirect URI for installed apps, can be left as is
REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"
# global variable to set Folder ID to upload to
parent_id = GDRIVE_FOLDER_ID

async def progress(current, total, event, start, type_of_ps, file_name = None):
    """Generic progress_callback for both
    upload.py and download.py"""
    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion
        progress_str = "[{0}{1}]\nProgress: {2}%\n".format(
            ''.join(["█" for i in range(math.floor(percentage / 5))]),
            ''.join(["░" for i in range(20 - math.floor(percentage / 5))]),
            round(percentage, 2))
        tmp = progress_str + \
            "{0} of {1}\nETA: {2}".format(
                humanbytes(current),
                humanbytes(total),
                time_formatter(estimated_total_time)
            )
        if file_name:
            await event.edit("{}\nFile Name: `{}`\n{}".format(
                type_of_ps,
                file_name,
                tmp
            ))
        else:
            await event.edit("{}\n{}".format(
                type_of_ps,
                tmp
            ))


def humanbytes(size):
    """Input size in bytes,
    outputs in a human readable format"""
    # https://stackoverflow.com/a/49361727/4723940
    if not size:
        return ""
    # 2 ** 10 = 1024
    power = 2 ** 10
    raised_to_pow = 0
    dict_power_n = {
        0: "",
        1: "Ki",
        2: "Mi",
        3: "Gi",
        4: "Ti"
    }
    while size > power:
        size /= power
        raised_to_pow += 1
    return str(round(size, 2)) + " " + dict_power_n[raised_to_pow] + "B"

def time_formatter(milliseconds: int) -> str:
    """Inputs time in milliseconds, to get beautified time,
    as string"""
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "day(s), ") if days else "") + \
        ((str(hours) + "hour(s), ") if hours else "") + \
        ((str(minutes) + "minute(s), ") if minutes else "") + \
        ((str(seconds) + "second(s), ") if seconds else "") + \
        ((str(milliseconds) + "millisecond(s), ") if milliseconds else "")
    return tmp[:-2]

@register(pattern=r"^.gdrive(?: |$)(.*)", outgoing=True)
async def download(dryb):
    """ For .gdrive command, upload files to google drive. """
    if not dryb.text[0].isalpha() and dryb.text[0] not in ("/", "#", "@", "!"):
        if dryb.fwd_from:
            return
        await dryb.edit("Processing ...")
        input_str = dryb.pattern_match.group(1)
        if CLIENT_ID is None or CLIENT_SECRET is None:
            return false
        if not os.path.isdir(TEMP_DOWNLOAD_DIRECTORY):
            os.makedirs(TEMP_DOWNLOAD_DIRECTORY)
            required_file_name = None
        message = await dryb.get_reply_message()
        if "|" in input_str:
            start = datetime.now()
            url, file_name = input_str.split("|")
            url = url.strip()
            # https://stackoverflow.com/a/761825/4723940
            file_name = file_name.strip()
            head, tail = os.path.split(file_name)
            if head:
                if not os.path.isdir(os.path.join(TEMP_DOWNLOAD_DIRECTORY, head)):
                    os.makedirs(os.path.join(TEMP_DOWNLOAD_DIRECTORY, head))
                    file_name = os.path.join(head, tail)
            downloaded_file_name = TEMP_DOWNLOAD_DIRECTORY + "" + file_name
            downloader = SmartDL(url, downloaded_file_name, progress_bar=False)
            downloader.start(blocking=False)
            c_time = time.time()
            while not downloader.isFinished():
                display_message = ""
                total_length = downloader.filesize if downloader.filesize else None
                downloaded = downloader.get_dl_size()
                now = time.time()
                diff = now - start
                percentage = downloader.get_progress()*100
                speed = downloader.get_speed()
                elapsed_time = round(diff) * 1000
                progress_str = "[{0}{1}]\nProgress: {2}%".format(
                    ''.join(["█" for i in range(math.floor(percentage / 5))]),
                    ''.join(["░" for i in range(20 - math.floor(percentage / 5))]),
                    round(percentage, 2))
                estimated_total_time = downloader.get_eta()
                try:
                    current_message = f"Downloading...\nURL: {url}\nFile Name: {file_name}\n{progress_str}\n{humanbytes(total_length)} of {humanbytes(downloaded)}\nETA: {time_formatter(estimated_total_time)}"
                    if current_message != display_message:
                        await dryb.edit(current_message)
                        display_message = current_message
                except Exception as e:
                    LOGS.info(str(e))
                    pass
            end = datetime.now()
            duration = (end - start).seconds
            if downloader.isSuccessful():
                await dryb.edit(
                    "Downloaded to `{}` in {} seconds.".format(
                        downloaded_file_name, duration)
                )
            else:
                await dryb.edit(
                    "Incorrect URL\n{}".format(url)
                )
        elif message.media:
            start = datetime.now()
            try:
                c_time = time.time()
                downloaded_file_name = await dryb.client.download_media(
                    message,
                    TEMP_DOWNLOAD_DIRECTORY,
                    progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                        progress(d, t, dryb, c_time, "Downloading...")
                    )
                )
            except Exception as e: # pylint:disable=C0103,W0703
                await dryb.edit(str(e))
            else:
                end = datetime.now()
                required_file_name = downloaded_file_name
                duration = (end - start).seconds
                await dryb.edit(
                    "Downloaded to `{}` in {} seconds.\nNow uploading to GDrive...".format(
                        downloaded_file_name, duration)
                )
        elif input_str:
            input_str = input_str.strip()
            if os.path.exists(input_str):
                start = datetime.now()
                end = datetime.now()
                duration = (end - start).seconds
                required_file_name = input_str
                await dryb.edit("Found `{}` in {} seconds, uploading to Google Drive !!".format(input_str, duration))
            else:
                await dryb.edit("File not found in local server. Give me a valid file path !!")
                return False
    if required_file_name:
        #
        if G_DRIVE_AUTH_TOKEN_DATA is not None:
            with open(G_DRIVE_TOKEN_FILE, "w") as t_file:
                t_file.write(G_DRIVE_AUTH_TOKEN_DATA)
        # Check if token file exists, if not create it by requesting authorization code
        if not os.path.isfile(G_DRIVE_TOKEN_FILE):
            storage = await create_token_file(G_DRIVE_TOKEN_FILE, dryb)
            http = authorize(G_DRIVE_TOKEN_FILE, storage)
        # Authorize, get file parameters, upload file and print out result URL for download
        http = authorize(G_DRIVE_TOKEN_FILE, None)
        file_name, mime_type = file_ops(required_file_name)
        # required_file_name will have the full path
        # Sometimes API fails to retrieve starting URI, we wrap it.
        try:
            g_drive_link = await upload_file(http, required_file_name, file_name, mime_type, dryb)
            await dryb.edit(f"File:`{required_file_name}`\nwas successfully uploaded to [Google Drive]({g_drive_link})!")
        except Exception as e:
            await dryb.edit(f"Error while uploading to Google Drive\nError Code:\n`{e}`")


@register(pattern=r"^.gsetf https?://drive\.google\.com/drive/u/\d/folders/([-\w]{25,})", outgoing=True)
async def download(set):
    """For .gsetf command, allows you to set path"""
    if not set.text[0].isalpha() and set.text[0] not in ("/", "#", "@", "!"):
        if set.fwd_from:
            return
        await set.reply("Processing ...")
        input_str = set.pattern_match.group(1)
        if input_str:
            parent_id = input_str
            await set.edit("Custom Folder ID set successfully. The next uploads will upload to {parent_id} till `.gdriveclear`")
            await set.delete()
        else:
            await set.edit("Use `.gdrivesp <link to GDrive Folder>` to set the folder to upload new files to.")


@register(pattern="^.gsetclear$", outgoing=True)
async def download(gclr):
    """For .gsetclear command, allows you clear ur curnt custom path"""
    if not gclr.text[0].isalpha() and gclr.text[0] not in ("/", "#", "@", "!"):
        if gclr.fwd_from:
            return
        await gclr.reply("Processing ...")
        parent_id = GDRIVE_FOLDER_ID
        await gclr.edit("Custom Folder ID cleared successfully.")
        await gclr.delete()


# Get mime type and name of given file
def file_ops(file_path):
    mime_type = guess_type(file_path)[0]
    mime_type = mime_type if mime_type else "text/plain"
    file_name = file_path.split("/")[-1]
    return file_name, mime_type


async def create_token_file(token_file, event):
    # Run through the OAuth flow and retrieve credentials
    flow = OAuth2WebServerFlow(
        CLIENT_ID,
        CLIENT_SECRET,
        OAUTH_SCOPE,
        redirect_uri=REDIRECT_URI
    )
    authorize_url = flow.step1_get_authorize_url()
    await event.edit("Check your userbot log for authentication link !!")
    async with event.client.conversation(BOTLOG_CHATID) as conv:
        await conv.send_message(f"Go to the following link in your browser: {authorize_url} and reply the code")
        response = conv.wait_event(events.NewMessage(
            outgoing=True,
            chats=BOTLOG_CHATID
        ))
        response = await response
        code = response.message.message.strip()
        credentials = flow.step2_exchange(code)
        storage = Storage(token_file)
        storage.put(credentials)
        return storage


def authorize(token_file, storage):
    # Get credentials
    if storage is None:
        storage = Storage(token_file)
    credentials = storage.get()
    # Create an httplib2.Http object and authorize it with our credentials
    http = httplib2.Http()
    credentials.refresh(http)
    http = credentials.authorize(http)
    return http


async def upload_file(http, file_path, file_name, mime_type, event):
    # Create Google Drive service instance
    drive_service = build("drive", "v2", http=http, cache_discovery=False)
    # File body description
    media_body = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
    body = {
        "title": file_name,
        "description": "Uploaded using PaperplaneExtended Userbot.",
        "mimeType": mime_type,
    }
    if parent_id:
        body["parents"] = [{"id": parent_id}]
    # Permissions body description: anyone who has link can upload
    # Other permissions can be found at https://developers.google.com/drive/v2/reference/permissions
    permissions = {
        "role": "reader",
        "type": "anyone",
        "value": None,
        "withLink": True
    }
    # Insert a file
    file = drive_service.files().insert(body=body, media_body=media_body)
    response = None
    while response is None:
        status, response = file.next_chunk()
        if status:
            percentage = int(status.progress() * 100)
            progress_str = "[{0}{1}]\nProgress: {2}%\n".format(
                ''.join(["█" for i in range(math.floor(percentage / 5))]),
                ''.join(["░" for i in range(20 - math.floor(percentage / 5))]),
                round(percentage, 2))
            await event.edit(f"Uploading to Google Drive...\n\nFile Name: {file_name}\n{progress_str}")
    if file:
        await event.edit(file_name + " uploaded successfully")
    # Insert new permissions
    drive_service.permissions().insert(fileId=response.get('id'), body=permissions)
    # Define file instance and get url for download
    download_url = "https://drive.google.com/file/d/" + response.get('id') + "/view"
    return download_url

@register(pattern="^.gfolder$", outgoing=True)
async def _(event):
    if event.fwd_from:
        return
    folder_link = "https://drive.google.com/drive/u/2/folders/"+parent_id
    await event.edit("Your current Google Drive upload directory: \n"+folder_link)


CMD_HELP.update({
    "gdrive": ".gdrive <file_path / reply / URL|file_name>\nUsage: Uploads the file in reply , URL or file path in server to your Google Drive.\n\n.gsetf <GDrive Folder URL>\nUsage:Sets the folder to upload new files to.\n\n.gsetclear\nUsage:Reverts to default upload destination.\n\n.gfolder\nUsage:Shows your current upload destination/folder."
})
