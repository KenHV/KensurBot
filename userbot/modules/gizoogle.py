import os, requests, time
import re
from asyncio.exceptions import TimeoutError
from userbot import CMD_HELP, bot
from userbot.events import register
from bs4 import BeautifulSoup
from urllib import parse

'''
adapted from https://github.com/chafla/gizoogle-py
'''

def gizoogletext(input_text: str) -> str:
    params = {"translatetext": input_text}
    target_url = "http://www.gizoogle.net/textilizer.php"
    resp = requests.post(target_url, data=params)
    soup_input = re.sub("/name=translatetext[^>]*>/", 'name="translatetext" >', resp.text)
    soup = BeautifulSoup(soup_input, "lxml")
    giz = soup.find_all(text=True)
    giz_text = giz[37].strip("\r\n")  # Hacky, but consistent.
    return giz_text

def gizooglelink(dest_url: str) -> str:
    params = {"search": dest_url}
    return ("http://www.gizoogle.net/tranzizzle.php?{}".format(parse.urlencode(params))+"&se=Gizoogle+Dis+Shiznit")

@register(outgoing=True, pattern=r"^\.gz(?: |$)(.*)")
async def gizoogle(gz_q):
    """Gizoogle dat shieet"""
    textx = await gz_q.get_reply_message()
    message = gz_q.pattern_match.group(1)

    if message:
        pass
    elif textx:
        message = textx.text
    else:
        await gz_q.edit("I require suttin' ta chizzle it dawg")
        return

    if message[0:4]=="link":
        gz_query = message[5:]
        gz_url = gizooglelink(gz_query)
        await gz_q.edit(f"here you go dawg. \n[{gz_query}]({gz_url})")
    else:
        await gz_q.edit(gizoogletext(message))

CMD_HELP.update(
    {
        "gizoogle": ">`\t.gz`\n"
        "Gizoogle dat shieet"
        "\nUsage:.gz [content] or .gz link [query]"
    }
)