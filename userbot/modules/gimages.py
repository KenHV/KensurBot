""" Userbot module for searching Image with CSE Google,
please setup your own CSE"""

import os
import shutil

from userbot import CMD_HELP, GCS_DEVELOPER_KEY, GCS_CX
from userbot.events import register
from google_images_search import GoogleImagesSearch

@register(outgoing=True, pattern="^.gimg (.*)")
async def gis_search(event):
 """ .srcimg command will search and download only"""
 await event.edit("Please wait..")
 q = event.pattern_match.group(1)
 num = findall(r"num=\d+", q)
 try:
     num = num[0]
     num = num.replace("num=" "")
     q = q.replace("num=" + n[0], "")
 except IndexError:
     num = 5
 response = google_images_search.GoogleImagesSearch()

 # if you don't enter api key and cx, the package will try to search
 # them from environment variables GCS_DEVELOPER_KEY and GCS_CX

 gis = GoogleImagesSearch(GCS_DEVELOPER_KEY, GCS_CX)

 #define search params:
 _search_params = {
    'q': '...',
    'num': 1-10,
    'safe': 'high|medium|off',
    'fileType': 'jpg|gif|png',
    'imgType': 'clipart|face|lineart|news|photo',
    'imgSize': 'huge|icon|large|medium|small|xlarge|xxlarge',
    'imgDominantColor': 'black|blue|brown|gray|green|pink|purple|teal|white|yellow'
 }

 gis.search(search_params=_search_params, path_to_dir='./downloads/')

 # argument list
 arguments = {
     "keywords": q,
     "limit": num,
     "filetype": "jpg",
     "path": "./downloads/"
 }

 # passing arguments to the function
 paths = response.download(arguments)
 lst = paths[0][q]
 await event.client.send_file(
     await event.client.get_input_entity(event.chat.id), lst)
 shutil.rmtree(os.path.dirname(os.path.abspath(lst[0]))
 )
 await event.delete()

 CMD_HELP.update({
    "googleimgsrc": 
    ".gimg <query>\
\nusage: search and download images from your customsearch engine" 
})
