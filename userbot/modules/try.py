# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# Credits: SpEcHiDe's UniBorg.
""" Userbot module to test bot functions as script. """

from telethon import events, errors, functions, types
import traceback
import sys
import io
from userbot.events import register, errors_handler
from userbot import CMD_HELP


@register(outgoing=True, pattern="^.try")
@errors_handler
async def test(event):
    await event.edit("Processing ...")
    cmd = event.text.split(' ', 1)[1]
    reply_to_id = event.message.id
    if event.reply_to_msg_id:
        reply_to_id = event.reply_to_msg_id

    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None

    try:
        await aexec(cmd, event)
    except Exception:
        exc = traceback.format_exc()

    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr

    evaluation = None
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"

    final_output = "**Query**:\n`{}`\n\n**Result**:\n`{}`".format(
        cmd, evaluation)

    if len(final_output) > 4096:
        with io.BytesIO(str.encode(final_output)) as out_file:
            out_file.name = "try.txt"
            await event.client.send_file(event.chat_id,
                                         out_file,
                                         force_document=True,
                                         allow_cache=False,
                                         caption=cmd,
                                         reply_to=reply_to_id)
            await event.delete()
    else:
        await event.edit(final_output)


async def aexec(code, event):
    exec(f'async def __aexec(event): ' + ''.join(f'\n {l}'
                                                 for l in code.split('\n')))
    return await locals()['__aexec'](event)


CMD_HELP.update({
    "try":
    ".try <userbot function code>\
    \nUsage: Executes the dynamically made userbot function, good for testing potential modules for userbot."
})
