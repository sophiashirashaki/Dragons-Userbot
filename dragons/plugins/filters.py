
# ported from paperplaneExtended by avinashreddy3108 for media support
import re

from telethon.utils import get_display_name

from dragons import drgub

from ..core.managers import edit_or_reply
from ..sql_helper.filter_sql import (
    add_filter,
    get_filters,
    remove_all_filters,
    remove_filter,
)
from . import BOTLOG, BOTLOG_CHATID

plugin_category = "utils"


@drgub.drg_cmd(incoming=True)
async def filter_incoming_handler(event):  # sourcery no-metrics
    if event.sender_id == event.client.uid:
        return
    name = event.raw_text
    filters = get_filters(event.chat_id)
    if not filters:
        return
    a_user = await event.get_sender()
    chat = await event.get_chat()
    me = await event.client.get_me()
    title = get_display_name(await event.get_chat()) or "this chat"
    participants = await event.client.get_participants(chat)
    count = len(participants)
    mention = f"[{a_user.first_name}](tg://user?id={a_user.id})"
    my_mention = f"[{me.first_name}](tg://user?id={me.id})"
    first = a_user.first_name
    last = a_user.last_name
    fullname = f"{first} {last}" if last else first
    username = f"@{a_user.username}" if a_user.username else mention
    userid = a_user.id
    my_first = me.first_name
    my_last = me.last_name
    my_fullname = f"{my_first} {my_last}" if my_last else my_first
    my_username = f"@{me.username}" if me.username else my_mention
    for trigger in filters:
        pattern = r"( |^|[^\w])" + re.escape(trigger.keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            file_media = None
            filter_msg = None
            if trigger.f_mesg_id:
                msg_o = await event.client.get_messages(
                    entity=BOTLOG_CHATID, ids=int(trigger.f_mesg_id)
                )
                file_media = msg_o.media
                filter_msg = msg_o.message
                link_preview = True
            elif trigger.reply:
                filter_msg = trigger.reply
                link_preview = False
            await event.reply(
                filter_msg.format(
                    mention=mention,
                    title=title,
                    count=count,
                    first=first,
                    last=last,
                    fullname=fullname,
                    username=username,
                    userid=userid,
                    my_first=my_first,
                    my_last=my_last,
                    my_fullname=my_fullname,
                    my_username=my_username,
                    my_mention=my_mention,
                ),
                file=file_media,
                link_preview=link_preview,
            )


@drgub.drg_cmd(
    pattern="filter (.*)",
    command=("filter", plugin_category),
    info={
        "header": "To save filter for the given keyword.",
        "description": "If any user sends that filter then your bot will reply.",
        "option": {
            "{mention}": "Untuk mention pengguna",
            "{title}": "Untuk menampilkan nama grup",
            "{count}": "Untuk menampilkan member ke berapa pengguna masuk",
            "{first}": "Untuk menampilkan nama depan",
            "{last}": "Untuk menampilkan nama belakang",
            "{fullname}": "Untuk menampilkan nama panjang",
            "{userid}": "Untuk menampilkan ID pengguna",
            "{username}": "Untuk menampilkan nama pengguna",
            "{my_first}": "Untuk menampilkan nama anda",
            "{my_fullname}": "Untuk menampilkan nama panjang anda",
            "{my_last}": "Untuk menampilkan nama belakang anda",
            "{my_mention}": "Untuk mention diri sendiri",
            "{my_username}": "Untuk menggunakan username diri sendiri.",
        },
        "usage": "{tr}filter <kata kunci>",
    },
)
async def add_new_filter(event):
    "To save the filter"
    keyword = event.pattern_match.group(1)
    string = event.text.partition(keyword)[2]
    msg = await event.get_reply_message()
    msg_id = None
    if msg and msg.media and not string:
        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID,
                f"#FILTER\
            \nCHAT ID: {event.chat_id}\
            \nTRIGGER: {keyword}\
            \n\nIni adalah filter yang disimpan, DIMOHON UNTUK TIDAK MENGHAPUSNYA !!",
            )
            msg_o = await event.client.forward_messages(
                entity=BOTLOG_CHATID,
                messages=msg,
                from_peer=event.chat_id,
                silent=True,
            )
            msg_id = msg_o.id
        else:
            await edit_or_reply(
                event,
                "__Saving media as reply to the filter requires the__ `PRIVATE_GROUP_BOT_API_ID` __to be set.__",
            )
            return
    elif msg and msg.text and not string:
        string = msg.text
    elif not string:
        return await edit_or_reply(event, "__What should i do ?__")
    success = "`Filter` **{}** `{} berhasil disimpan di gc ini.`"
    if add_filter(str(event.chat_id), keyword, string, msg_id) is True:
        return await edit_or_reply(event, success.format(keyword, "added"))
    remove_filter(str(event.chat_id), keyword)
    if add_filter(str(event.chat_id), keyword, string, msg_id) is True:
        return await edit_or_reply(event, success.format(keyword, "Updated"))
    await edit_or_reply(event, f"Error untuk menyimpan kata kunci {keyword}")


@drgub.drg_cmd(
    pattern="filters$",
    command=("filters", plugin_category),
    info={
        "header": "Untuk melihat daftar filter di grup ini.",
        "description": "Melihat daftar filter (filter userbot anda) di grup ini.",
        "usage": "{tr}filters",
    },
)
async def on_snip_list(event):
    "To list all filters in that chat."
    OUT_STR = "There are no filters in this chat."
    filters = get_filters(event.chat_id)
    for filt in filters:
        if OUT_STR == "Tidak ada filter tersimpan disini.":
            OUT_STR = "Filter yang aktif disini:\n"
        OUT_STR += "👉 `{}`\n".format(filt.keyword)
    await edit_or_reply(
        event,
        OUT_STR,
        caption="Filter yang tersedia di chat ini",
        file_name="filters.text",
    )


@drgub.drg_cmd(
    pattern="stop ([\s\S]*)",
    command=("stop", plugin_category),
    info={
        "header": "Untuk menghapus filter yang anda simpan.",
        "usage": "{tr}stop <keyword>",
    },
)
async def remove_a_filter(event):
    "Stops the specified keyword."
    filt = event.pattern_match.group(1)
    if not remove_filter(event.chat_id, filt):
        await event.edit("Filter` {} `doesn't exist.".format(filt))
    else:
        await event.edit("Filter `{} `Telah berhasil dihapus".format(filt))


@dgub.drg_cmd(
    pattern="rmfilters$",
    command=("rmfilters", plugin_category),
    info={
        "header": "Untuk menghapus semua filter di grup ini.",
        "usage": "{tr}rmfilters",
    },
)
async def on_all_snip_delete(event):
    "Untuk menghapus sekua filter didalam grup ini."
    filters = get_filters(event.chat_id)
    if filters:
        remove_all_filters(event.chat_id)
        await edit_or_reply(event, "Filter di grup ini telah dihapus")
    else:
        await edit_or_reply(event, "Tidak ada filter tersimpan disini")
