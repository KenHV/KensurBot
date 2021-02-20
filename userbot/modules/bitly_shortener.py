from re import match

from bitlyshortener import Shortener

from userbot import BITLY_TOKEN, BOTLOG, BOTLOG_CHATID, CMD_HELP
from userbot.events import register


@register(outgoing=True, pattern=r"^\.bitly(?: |$)(.*)")
async def shortener(short):
    """
        Shorten link using bit.ly API
    """
    if BITLY_TOKEN is not None:
        token = [f"{BITLY_TOKEN}"]
        reply = await short.get_reply_message()
        message = short.pattern_match.group(1)
        if message:
            pass
        elif reply:
            message = reply.text
        else:
            await short.edit("`Error! No URL given!`")
            return
        link_match = match(r"\bhttps?://.*\.\S+", message)
        if not link_match:
            await short.edit(
                "`Error! Please provide valid url!`\nexample: https://google.com"
            )
            return
        urls = [f"{message}"]
        bitly = Shortener(tokens=token, max_cache_size=8192)
        raw_output = bitly.shorten_urls(urls)
        string_output = f"{raw_output}"
        output = string_output.replace("['", "").replace("']", "")
        paraboy = f'<a href="{output}">Successfully Shortener to Bitly</a>'
        await short.edit(paraboy, parse_mode="HTML", link_preview=False)
        if BOTLOG:
            await short.client.send_message(
                BOTLOG_CHATID, f"`#SHORTLINK \nThis Your Link!`\n[Klik Disini Gan]({output})"
            )
    else:
        await short.edit(
            "Set bit.ly API token first\nGet from [here](https://bitly.com/a/sign_up)"
        )


CMD_HELP.update(
    {
        "bitly": ">`.bitly` <url> or reply to message contains url"
        "\nUsage: Shorten link using bit.ly API"
    }
)
