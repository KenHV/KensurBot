# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.


"""
Lyrics Plugin Syntax:
       .lyrics <aritst name> - <song name>

"""
import os
import lyricsgenius

from userbot.events import register
from userbot import (CMD_HELP, GENIUS, lastfm, LASTFM_USERNAME)
from pylast import User

if GENIUS is not None:
    genius = lyricsgenius.Genius(GENIUS)


@register(outgoing=True, pattern=r"^\.lyrics (?:(now)|(.*) - (.*))")
async def lyrics(lyric):
    await lyric.edit("`Getting information...`")
    if GENIUS is None:
        await lyric.edit(
            "`Provide genius access token to Heroku ConfigVars...`")
        return False
    if lyric.pattern_match.group(1) == "now":
        playing = User(LASTFM_USERNAME, lastfm).get_now_playing()
        if playing is None:
            await lyric.edit(
                "`No information current lastfm scrobbling...`"
            )
            return False
        artist = playing.get_artist()
        song = playing.get_title()
    else:
        artist = lyric.pattern_match.group(2)
        song = lyric.pattern_match.group(3)
    await lyric.edit(f"`Searching lyrics for {artist} - {song}...`")
    songs = genius.search_song(song, artist)
    if songs is None:
        await lyric.edit(f"`Song`  **{artist} - {song}**  `not found...`")
        return False
    if len(songs.lyrics) > 4096:
        await lyric.edit("`Lyrics is too big, view the file to see it.`")
        with open("lyrics.txt", "w+") as f:
            f.write(f"Search query: \n{artist} - {song}\n\n{songs.lyrics}")
        await lyric.client.send_file(
            lyric.chat_id,
            "lyrics.txt",
            reply_to=lyric.id,
        )
        os.remove("lyrics.txt")
    else:
        await lyric.edit(
            f"**Search query**:\n`{artist}` - `{song}`"
            f"\n\n```{songs.lyrics}```"
        )

    return True


CMD_HELP.update({
    "lyrics":
    ">`.lyrics` **<artist name> - <song name>**"
    "\nUsage: Get lyrics matched artist and song."
    "\n\n>`.lyrics now`"
    "\nUsage: Get lyrics artist and song from current lastfm scrobbling."
})
