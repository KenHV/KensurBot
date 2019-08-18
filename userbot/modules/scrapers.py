# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.b (the "License");
# you may not use this file except in compliance with the License.
#

""" Userbot module containing various scrapers. """

import os
import shutil
from bs4 import BeautifulSoup
import re
from time import sleep
from html import unescape
from re import findall
from datetime import datetime
from selenium import webdriver
from urllib.parse import quote_plus
from urllib.error import HTTPError
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from wikipedia import summary
from wikipedia.exceptions import DisambiguationError, PageError
from urbandict import define
from requests import get
from google_images_download import google_images_download
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googletrans import LANGUAGES, Translator
from gtts import gTTS
from emoji import get_emoji_regexp
from pytube import YouTube
from pytube.helpers import safe_filename

from userbot import CMD_HELP, BOTLOG, BOTLOG_CHATID, YOUTUBE_API_KEY, CHROME_DRIVER, GOOGLE_CHROME_BIN
from userbot.events import register

CARBONLANG = "auto"
LANG = "en"

@register(outgoing=True, pattern="^.crblang")
async def setlang(prog):
    if not prog.text[0].isalpha() and prog.text[0] not in ("/", "#", "@", "!"):
        global CARBONLANG
        CARBONLANG = prog.text.split()[1]
        await prog.edit(f"language set to {CARBONLANG}")

@register(outgoing=True, pattern="^.carbon")
async def carbon_api(e):
 if not e.text[0].isalpha() and e.text[0] not in ("/", "#", "@", "!"):
   """ A Wrapper for carbon.now.sh """
   await e.edit("`Processing..`")
   CARBON = 'https://carbon.now.sh/?l={lang}&code={code}'
   global CARBONLANG
   textx = await e.get_reply_message()
   pcode = e.text
   if pcode[8:]:
         pcode = str(pcode[8:])
   elif textx:
         pcode = str(textx.message) # Importing message to module
   code = quote_plus(pcode) # Converting to urlencoded
   await e.edit("`Processing..\n25%`")
   url = CARBON.format(code=code, lang=CARBONLANG)
   chrome_options = Options()
   chrome_options.add_argument("--headless")
   chrome_options.binary_location = GOOGLE_CHROME_BIN
   chrome_options.add_argument("--window-size=1920x1080")
   chrome_options.add_argument("--disable-dev-shm-usage")
   chrome_options.add_argument("--no-sandbox")
   chrome_options.add_argument("--disable-gpu")
   prefs = {'download.default_directory' : './'}
   chrome_options.add_experimental_option('prefs', prefs)
   driver = webdriver.Chrome(executable_path=CHROME_DRIVER, options=chrome_options)
   driver.get(url)
   await e.edit("`Processing..\n50%`")
   download_path = './'
   driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
   params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_path}}
   command_result = driver.execute("send_command", params)
   driver.find_element_by_xpath("//button[contains(text(),'Export')]").click()
   driver.find_element_by_xpath("//button[contains(text(),'4x')]").click()
   driver.find_element_by_xpath("//button[contains(text(),'PNG')]").click()
   await e.edit("`Processing..\n75%`")
   # Waiting for downloading
   sleep(2.5)
   await e.edit("`Processing..\n100%`")
   file = './carbon.png'
   await e.edit("`Uploading..`")
   await e.client.send_file(
         e.chat_id,
         file,
         caption="Made using [Carbon](https://carbon.now.sh/about/), a project by [Dawn Labs](https://dawnlabs.io/)",
         force_document=True,
         reply_to=e.message.reply_to_msg_id,
         )

   os.remove('./carbon.png')
   driver.quit()
   # Removing carbon.png after uploading
   await e.delete() # Deleting msg

@register(outgoing=True, pattern="^.img (.*)")
async def img_sampler(event):
    """ For .img command, search and return images matching the query. """
    if not event.text[0].isalpha() and event.text[0] not in ("/", "#", "@", "!"):
        await event.edit("Processing...")
        query = event.pattern_match.group(1)
        lim = findall(r"lim=\d+", query)
        try:
            lim = lim[0]
            lim = lim.replace("lim=", "")
            query = query.replace("lim=" + lim[0], "")
        except IndexError:
            lim = 3
        response = google_images_download.googleimagesdownload()

        # creating list of arguments
        arguments = {
            "keywords": query,
            "limit": lim,
            "format": "jpg",
            "no_directory": "no_directory"
        }

        # passing the arguments to the function
        paths = response.download(arguments)
        lst = paths[0][query]
        await event.client.send_file(await event.client.get_input_entity(event.chat_id), lst)
        shutil.rmtree(os.path.dirname(os.path.abspath(lst[0])))
        await event.delete()

@register(outgoing=True, pattern="^.currency (.*)")
async def _(event):
    if not event.text[0].isalpha() and event.text[0] not in ("/", "#", "@", "!"):
        if event.fwd_from:
            return
        start = datetime.now()
        input_str = event.pattern_match.group(1)
        input_sgra = input_str.split(" ")
        if len(input_sgra) == 3:
            try:
                number = float(input_sgra[0])
                currency_from = input_sgra[1].upper()
                currency_to = input_sgra[2].upper()
                request_url = "https://api.exchangeratesapi.io/latest?base={}".format(currency_from)
                current_response = get(request_url).json()
                if currency_to in current_response["rates"]:
                    current_rate = float(current_response["rates"][currency_to])
                    rebmun = round(number * current_rate, 2)
                    await event.edit("{} {} = {} {}".format(number, currency_from, rebmun, currency_to))
                else:
                    await event.edit("`This seems to be some alien currency, which I can't convert right now.`")
            except e:
                await event.edit(str(e))
        else:
            await event.edit("`Invalid syntax.`")
        end = datetime.now()
        ms = (end - start).seconds


@register(outgoing=True, pattern=r"^.search (.*)")
async def gsearch(q_event):
    """ For .google command, do a Google search. """
    if not q_event.text[0].isalpha() and q_event.text[0] not in (
            "/", "#", "@", "!"):
        match_ = q_event.pattern_match.group(1)
        match = quote_plus(match_)
        plain_txt = get(f"https://www.startpage.com/do/search?cmd=process_search&query={match}", 'html').text
        soup = BeautifulSoup(plain_txt, "lxml")
        
        msg = ""
        for result in soup.find_all('a', {'class': 'w-gl__result-title'}):
            title = result.text
            link = result.get('href')
            msg += f"{title}{link}\n"
            
        await q_event.edit(
            "**Search Query:**\n`" + match_ + "`\n\n**Results:**\n" + msg,
            link_preview = False
        )
        
        if BOTLOG:
            await q_event.client.send_message(
                BOTLOG_CHATID,
                "Search query `" + match_ + "` was executed successfully",
            )

@register(outgoing=True, pattern=r"^.wiki (.*)")
async def wiki(wiki_q):
    """ For .google command, fetch content from Wikipedia. """
    if not wiki_q.text[0].isalpha() and wiki_q.text[0] not in ("/", "#", "@", "!"):
        match = wiki_q.pattern_match.group(1)
        try:
            summary(match)
        except DisambiguationError as error:
            await wiki_q.edit(f"Disambiguated page found.\n\n{error}")
            return
        except PageError as pageerror:
            await wiki_q.edit(f"Page not found.\n\n{pageerror}")
            return
        result = summary(match)
        if len(result) >= 4096:
            file = open("output.txt", "w+")
            file.write(result)
            file.close()
            await wiki_q.client.send_file(
                wiki_q.chat_id,
                "output.txt",
                reply_to=wiki_q.id,
                caption="`Output too large, sending as file`",
            )
            if os.path.exists("output.txt"):
                os.remove("output.txt")
            return
        await wiki_q.edit(
            "**Search:**\n`" + match + "`\n\n**Result:**\n" + result
        )
        if BOTLOG:
            await wiki_q.client.send_message(
                BOTLOG_CHATID,
                f"Wiki query `{match}` was executed successfully"
            )


@register(outgoing=True, pattern="^.ud (.*)")
async def urban_dict(ud_e):
    """ For .ud command, fetch content from Urban Dictionary. """
    if not ud_e.text[0].isalpha() and ud_e.text[0] not in ("/", "#", "@", "!"):
        await ud_e.edit("Processing...")
        query = ud_e.pattern_match.group(1)
        try:
            define(query)
        except HTTPError:
            await ud_e.edit(f"Sorry, couldn't find any results for: {query}")
            return
        mean = define(query)
        deflen = sum(len(i) for i in mean[0]["def"])
        exalen = sum(len(i) for i in mean[0]["example"])
        meanlen = deflen + exalen
        if int(meanlen) >= 0:
            if int(meanlen) >= 4096:
                await ud_e.edit("`Output too large, sending as file.`")
                file = open("output.txt", "w+")
                file.write(
                    "Text: " +
                    query +
                    "\n\nMeaning: " +
                    mean[0]["def"] +
                    "\n\n" +
                    "Example: \n" +
                    mean[0]["example"]
                )
                file.close()
                await ud_e.client.send_file(
                    ud_e.chat_id,
                    "output.txt",
                    caption="`Output was too large, sent it as a file.`"
                )
                if os.path.exists("output.txt"):
                    os.remove("output.txt")
                await ud_e.delete()
                return
            await ud_e.edit(
                "Text: **" +
                query +
                "**\n\nMeaning: **" +
                mean[0]["def"] +
                "**\n\n" +
                "Example: \n__" +
                mean[0]["example"] +
                "__"
            )
            if BOTLOG:
                await ud_e.client.send_message(
                    BOTLOG_CHATID, "ud query `" + query + "` executed successfully."
                )
        else:
            await ud_e.edit("No result found for **" + query + "**")


@register(outgoing=True, pattern=r"^.tts(?: |$)([\s\S]*)")
async def text_to_speech(query):
    """ For .tts command, a wrapper for Google Text-to-Speech. """
    if not query.text[0].isalpha() and query.text[0] not in ("/", "#", "@", "!"):
        textx = await query.get_reply_message()
        message = query.pattern_match.group(1)
        if message:
            pass
        elif textx:
            message = textx.text
        else:
            await query.edit("`Give a text or reply to a message for Text-to-Speech!`")
            return

        try:
            gTTS(message, LANG)
        except AssertionError:
            await query.edit(
                'The text is empty.\n'
                'Nothing left to speak after pre-precessing, tokenizing and cleaning.'
            )
            return
        except ValueError:
            await query.edit('Language is not supported.')
            return
        except RuntimeError:
            await query.edit('Error loading the languages dictionary.')
            return
        tts = gTTS(message, LANG)
        tts.save("k.mp3")
        with open("k.mp3", "rb") as audio:
            linelist = list(audio)
            linecount = len(linelist)
        if linecount == 1:
            tts = gTTS(message, LANG)
            tts.save("k.mp3")
        with open("k.mp3", "r"):
            await query.client.send_file(query.chat_id, "k.mp3", voice_note=True)
            os.remove("k.mp3")
            if BOTLOG:
                await query.client.send_message(
                    BOTLOG_CHATID, "tts of `" + message + "` executed successfully!"
                )
            await query.delete()


#kanged from Blank-x ;---;
@register(outgoing=True, pattern="^.imdb (.*)")
async def imdb(e):
    if not e.text[0].isalpha() and e.text[0] not in ("/", "#", "@", "!"):
        try:
            movie_name = e.pattern_match.group(1)
            remove_space = movie_name.split(' ')
            final_name = '+'.join(remove_space)
            page = get("https://www.imdb.com/find?ref_=nv_sr_fn&q="+final_name+"&s=all")
            lnk = str(page.status_code)
            soup = BeautifulSoup(page.content,'lxml')
            odds = soup.findAll("tr","odd")
            mov_title = odds[0].findNext('td').findNext('td').text
            mov_link = "http://www.imdb.com/"+odds[0].findNext('td').findNext('td').a['href']
            page1 = get(mov_link)
            soup = BeautifulSoup(page1.content,'lxml')
            if soup.find('div','poster'):
    	        poster = soup.find('div','poster').img['src']
            else:
    	        poster = ''
            if soup.find('div','title_wrapper'):
    	        pg = soup.find('div','title_wrapper').findNext('div').text
    	        mov_details = re.sub(r'\s+',' ',pg)
            else:
    	        mov_details = ''
            credits = soup.findAll('div', 'credit_summary_item')
            if len(credits)==1:
    	        director = credits[0].a.text
    	        writer = 'Not available'
    	        stars = 'Not available'
            elif len(credits)>2:
    	        director = credits[0].a.text
    	        writer = credits[1].a.text
    	        actors = []
    	        for x in credits[2].findAll('a'):
    		        actors.append(x.text)
    	        actors.pop()
    	        stars = actors[0]+','+actors[1]+','+actors[2]
            else:
    	        director = credits[0].a.text
    	        writer = 'Not available'
    	        actors = []
    	        for x in credits[1].findAll('a'):
    		        actors.append(x.text)
    	        actors.pop()
    	        stars = actors[0]+','+actors[1]+','+actors[2]
            if soup.find('div', "inline canwrap"):
    	        story_line = soup.find('div', "inline canwrap").findAll('p')[0].text
            else:
    	        story_line = 'Not available'
            info = soup.findAll('div', "txt-block")
            if info:
    	        mov_country = []
    	        mov_language = []
    	        for node in info:
    		        a = node.findAll('a')
    		        for i in a:
    			        if "country_of_origin" in i['href']:
    				        mov_country.append(i.text)
    			        elif "primary_language" in i['href']:
    				        mov_language.append(i.text)
            if soup.findAll('div',"ratingValue"):
    	        for r in soup.findAll('div',"ratingValue"):
    		        mov_rating = r.strong['title']
            else:
    	        mov_rating = 'Not available'
            await e.edit('<a href='+poster+'>&#8203;</a>'
    			        '<b>Title : </b><code>'+mov_title+
    			        '</code>\n<code>'+mov_details+
    			        '</code>\n<b>Rating : </b><code>'+mov_rating+
    			        '</code>\n<b>Country : </b><code>'+mov_country[0]+
    			        '</code>\n<b>Language : </b><code>'+mov_language[0]+
    			        '</code>\n<b>Director : </b><code>'+director+
    			        '</code>\n<b>Writer : </b><code>'+writer+
    			        '</code>\n<b>Stars : </b><code>'+stars+
    			        '</code>\n<b>IMDB Url : </b>'+mov_link+
    			        '\n<b>Story Line : </b>'+story_line,
    			        link_preview = True , parse_mode = 'HTML'
    			        )
        except IndexError:
            await e.edit("Plox enter **Valid movie name** kthx")

@register(outgoing=True, pattern=r"^.trt(?: |$)([\s\S]*)")
async def translateme(trans):
    """ For .trt command, translate the given text using Google Translate. """
    if not trans.text[0].isalpha() and trans.text[0] not in ("/", "#", "@", "!"):
        translator = Translator()
        textx = await trans.get_reply_message()
        message = trans.pattern_match.group(1)
        if message:
            pass
        elif textx:
            message = textx.text
        else:
            await trans.edit("`Give a text or reply to a message to translate!`")
            return

        try:
            reply_text = translator.translate(deEmojify(message), dest=LANG)
        except ValueError:
            await trans.edit("Invalid destination language.")
            return

        source_lan = LANGUAGES[f'{reply_text.src.lower()}']
        transl_lan = LANGUAGES[f'{reply_text.dest.lower()}']
        reply_text = f"From **{source_lan.title()}**\nTo **{transl_lan.title()}:**\n\n{reply_text.text}"

        await trans.edit(reply_text)
        if BOTLOG:
            await trans.client.send_message(
                BOTLOG_CHATID,
                f"Translated some {source_lan.title()} stuff to {transl_lan.title()} just now.",
            )


@register(pattern=".lang (.*)", outgoing=True)
async def lang(value):
    """ For .lang command, change the default langauge of userbot scrapers. """
    if not value.text[0].isalpha() and value.text[0] not in ("/", "#", "@", "!"):
        global LANG
        LANG = value.pattern_match.group(1)
        if BOTLOG:
            await value.client.send_message(
                BOTLOG_CHATID, "Default language changed to **" + LANG + "**"
            )
            await value.edit("Default language changed to **" + LANG + "**")


@register(outgoing=True, pattern="^.yt (.*)")
async def yt_search(video_q):
    """ For .yt command, do a YouTube search from Telegram. """
    if not video_q.text[0].isalpha() and video_q.text[0] not in ("/", "#", "@", "!"):
        query = video_q.pattern_match.group(1)
        result = ''

        if not YOUTUBE_API_KEY:
            await video_q.edit("`Error: YouTube API key missing! Add it to environment vars or config.env.`")
            return

        await video_q.edit("```Processing...```")

        full_response = youtube_search(query)
        videos_json = full_response[1]


        for video in videos_json:
            title = f"{unescape(video['snippet']['title'])}"
            link = f"https://youtu.be/{video['id']['videoId']}"
            result += f"{title}\n{link}\n\n"

        reply_text = f"**Search Query:**\n`{query}`\n\n**Results:**\n\n{result}"

        await video_q.edit(reply_text)


def youtube_search(
        query,
        order="relevance",
        token=None,
        location=None,
        location_radius=None
    ):

    """ Do a YouTube search. """
    youtube = build('youtube', 'v3',
                    developerKey=YOUTUBE_API_KEY, cache_discovery=False)
    search_response = youtube.search().list(
        q=query,
        type="video",
        pageToken=token,
        order=order,
        part="id,snippet",
        maxResults=10,
        location=location,
        locationRadius=location_radius
    ).execute()

    videos = []

    for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
            videos.append(search_result)
    try:
        nexttok = search_response["nextPageToken"]
        return(nexttok, videos)
    except HttpError:
        nexttok = "last_page"
        return(nexttok, videos)
    except KeyError:
        nexttok = "KeyError, try again."
        return(nexttok, videos)


@register(outgoing=True, pattern=r".yt_dl (\S*) ?(\S*)")
async def download_video(v_url):
    """ For .yt_dl command, download videos from YouTube. """
    if not v_url.text[0].isalpha() and v_url.text[0] not in ("/", "#", "@", "!"):
        url = v_url.pattern_match.group(1)
        quality = v_url.pattern_match.group(2)

        await v_url.edit("**Fetching...**")

        video = YouTube(url)

        if quality:
            video_stream = video.streams.filter(
                progressive=True,
                subtype="mp4",
                res=quality
            ).first()
        else:
            video_stream = video.streams.filter(
                progressive=True,
                subtype="mp4"
            ).first()

        if video_stream is None:
            all_streams = video.streams.filter(
                progressive=True,
                subtype="mp4"
            ).all()
            available_qualities = ""

            for item in all_streams[:-1]:
                available_qualities += f"{item.resolution}, "
            available_qualities += all_streams[-1].resolution

            await v_url.edit(
                "**A stream matching your query wasn't found. Try again with different options.\n**"
                "**Available Qualities:**\n"
                f"{available_qualities}"
            )
            return

        video_size = video_stream.filesize / 1000000

        if video_size >= 50:
            await v_url.edit(
                ("**File larger than 50MB. Sending the link instead.\n**"
                 f"Get the video [here]({video_stream.url})\n\n"
                 "**If the video plays instead of downloading, right click(or long press on touchscreen) and "
                 "press 'Save Video As...'(may depend on the browser) to download the video.**")
            )
            return

        await v_url.edit("**Downloading...**")

        video_stream.download(filename=video.title)

        url = f"https://img.youtube.com/vi/{video.video_id}/maxresdefault.jpg"
        resp = get(url)
        with open('thumbnail.jpg', 'wb') as file:
            file.write(resp.content)

        await v_url.edit("**Uploading...**")
        await v_url.client.send_file(
            v_url.chat_id,
            f'{safe_filename(video.title)}.mp4',
            caption=f"{video.title}",
            thumb="thumbnail.jpg"
        )

        os.remove(f"{safe_filename(video.title)}.mp4")
        os.remove('thumbnail.jpg')
        await v_url.delete()

def deEmojify(inputString):
    """ Remove emojis and other non-safe characters from string """
    return get_emoji_regexp().sub(u'', inputString)

CMD_HELP.update({
    'img': '.img <search_query>\
        \nUsage: Does an image search on Google and shows 5 images.'
})
CMD_HELP.update({
    'currency': '.currency <amount> <from> <to>\
        \nUsage: Converts various currencies for you.'
})
CMD_HELP.update({
    'carbon': '.carbon <text> [or reply]\
        \nUsage: Beautify your code using carbon.now.sh\nUse .crblang <text> to set language for your code.'
})
CMD_HELP.update({
    'search': '.search <query>\
        \nUsage: Does a search on StartPage.'
})
CMD_HELP.update({
    'wiki': '.wiki <query>\
        \nUsage: Does a search on Wikipedia.'
})
CMD_HELP.update({
    'ud': '.ud <query>\
        \nUsage: Does a search on Urban Dictionary.'
})
CMD_HELP.update({
    'ud': '.ud <query>\
        \nUsage: Does a search on Urban Dictionary.'
})
CMD_HELP.update({
    'tts': '.tts <text> [or reply]\
        \nUsage: Translates text to speech for the default language which is set.\nUse .lang <text> to set language for your TTS.'
})
CMD_HELP.update({
    'trt': '.trt <text> [or reply]\
        \nUsage: Translates text to the default language which is set.\nUse .lang <text> to set language for your TTS.'
})
CMD_HELP.update({
    'yt': '.yt <text>\
        \nUsage: Does a YouTube search.'
})
CMD_HELP.update({
    "imdb": ".imdb <movie-name>\nShows movie info and other stuffs"
})
CMD_HELP.update({
    'yt_dl': '.yt_dl <url> <quality>\
        \nUsage: Download videos from YouTube.If no quality is specified, the highest downloadable quality is downloaded. Will send the link if the video is larger than 50 MB.'
})
