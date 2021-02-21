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
from pylast import User

from userbot import CMD_HELP, GENIUS, LASTFM_USERNAME, lastfm
from userbot.events import register

if GENIUS is not None:
    genius = lyricsgenius.Genius(GENIUS)


@register(outgoing=True, pattern=r"^\.lyrics (?:(now)|(.*) - (.*))")
async def lyrics(lyric):
    await lyric.edit("**Processing...**")

    if GENIUS is None:
        return await lyric.edit("**Add Genius access token to config vars.**")

    if lyric.pattern_match.group(1) == "now":
        playing = User(LASTFM_USERNAME, lastfm).get_now_playing()
        if playing is None:
            return await lyric.edit(
                "**LastFM says you're not playing anything right now.**"
            )
        artist = playing.get_artist()
        song = playing.get_title()
    else:
        artist = lyric.pattern_match.group(2)
        song = lyric.pattern_match.group(3)

    await lyric.edit(f"**Searching lyrics for** `{artist} - {song}`**...**")
    songs = genius.search_song(song, artist)

    if songs is None:
        return await lyric.edit(
            f"**Couldn't find lyrics for** `{artist} - {song}`**.**"
        )

    if len(songs.lyrics) > 4096:
        await lyric.edit("**Uploading lyrics as file...**")
        with open("lyrics.txt", "w+") as f:
            f.write(f"Search query: \n{artist} - {song}\n\n{songs.lyrics}")
        await lyric.client.send_file(lyric.chat_id, "lyrics.txt", reply_to=lyric.id)
        os.remove("lyrics.txt")
    else:
        await lyric.edit(
            f"**Search query**:\n`{artist}` - `{song}`" f"\n\n{songs.lyrics}"
        )


CMD_HELP.update(
    {
        "lyrics": ">`.lyrics` **<artist name> - <song name>**"
        "\nUsage: Gets lyrics for given song."
        "\n\n>`.lyrics now`"
        "\nUsage: Gets lyrics for current LastFM scrobble."
    }
)
