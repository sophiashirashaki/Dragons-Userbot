import asyncio

from telethon.errors.rpcerrorlist import YouBlockedUserError

from dragons import drgub

from ..core.managers import edit_delete, edit_or_reply
from ..helpers import get_user_from_event, sanga_seperator
from ..helpers.utils import _format

plugin_category = "utils"


@drgub.drg_cmd(
    pattern="sg(u)?(?:\s|$)([\s\S]*)",
    command=("sg", plugin_category),
    info={
        "header": "Untuk mendapatkan history pergantian nama.",
        "flags": {
            "u": "Untuk mendapatkan pergantian nama pengguna.",
        },
        "usage": [
            "{tr}sg <username/userid/reply>",
            "{tr}sgu <username/userid/reply>",
        ],
        "examples": "{tr}sg @missrose_bot",
    },
)
async def _(event):  # sourcery no-metrics
    "To get name/username history."
    input_str = "".join(event.text.split(maxsplit=1)[1:])
    reply_message = await event.get_reply_message()
    if not input_str and not reply_message:
        await edit_delete(
            event,
            "`reply ke pengguna untuk mendapatkan history nama/pengguna atau bisa menggunakan ID/username pengguna`",
        )
    user, rank = await get_user_from_event(event, secondgroup=True)
    if not user:
        return
    uid = user.id
    chat = "@SangMataInfo_bot"
    drgevent = await edit_or_reply(event, "`Processing...`")
    async with event.client.conversation(chat) as conv:
        try:
            await conv.send_message(f"/search_id {uid}")
        except YouBlockedUserError:
            await edit_delete(drgevent, "`mohon buka blokiran @Sangmatainfo_bot dan coba lagi`")
        responses = []
        while True:
            try:
                response = await conv.get_response(timeout=2)
            except asyncio.TimeoutError:
                break
            responses.append(response.text)
        await event.client.send_read_acknowledge(conv.chat_id)
    if not responses:
        await edit_delete(drgevent, "`botnya ga bisa baca historynya, jelek:v`")
    if "No records found" in responses:
        await edit_delete(drgevent, "`Tidak ditemukan pergantian nama dari pengguna ini`")
    names, usernames = await sanga_seperator(responses)
    cmd = event.pattern_match.group(1)
    dragons = None
    check = usernames if cmd == "u" else names
    for i in check:
        if dragons:
            await event.reply(i, parse_mode=_format.parse_pre)
        else:
            dragons = True
            await drgevent.edit(i, parse_mode=_format.parse_pre)
