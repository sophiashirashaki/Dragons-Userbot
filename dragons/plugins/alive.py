import random
import re
import time
import datetime

from platform import python_version
from telethon import version
from telethon.errors.rpcerrorlist import (
    MediaEmptyError,
    WebpageCurlFailedError,
    WebpageMediaEmptyError,
)
from telethon.events import CallbackQuery
from dragons import StartTime, drgub, drgversion

from ..Config import Config
from ..core.managers import edit_or_reply
from ..helpers.functions import drgalive, check_data_base_heal_th, get_readable_time
from ..helpers.utils import reply_id
from ..sql_helper.globals import gvarstatus
from . import mention

plugin_category = "utils"


@drgub.drg_cmd(
    pattern="alive$",
    command=("alive", plugin_category),
    info={
        "header": "Untuk memeriksa status hidup bot",
        "options": "Untuk menampilkan media dalam perintah ini, Anda perlu `set ALIVE_PIC` dengan tautan media, dapatkan ini dengan membalas media dengan `{tr}tgm`",
        "usage": [
            "{tr}alive",
        ],
    },
)
async def amireallyalive(event):
    "Semacam menampilkan detail bot"
    reply_to_id = await reply_id(event)
    uptime = await get_readable_time((time.time() - StartTime))
    start = datetime.now()
    await edit_or_reply(event, "Userbot Aktif...")
    end = datetime.now()
    ms = (end - start).microseconds / 1000
    _, check_sgnirts = check_data_base_heal_th()
    EMOJI = gvarstatus("ALIVE_EMOJI") or "✥"
    ALIVE_TEXT = gvarstatus("ALIVE_TEXT") or "**✮ DRAGONS-USERBOT ✮**"
    DRG_IMG = gvarstatus("ALIVE_PIC")
    drg_caption = gvarstatus("ALIVE_TEMPLATE") or temp
    caption = drg_caption.format(
        ALIVE_TEXT=ALIVE_TEXT,
        EMOJI=EMOJI,
        mention=mention,
        uptime=uptime,
        telever=version.__version__,
        drgver=drgversion,
        pyver=python_version(),
        dbhealth=check_sgnirts,
        ping=ms,
    )
    if DRG_IMG:
        DRG = [x for x in DRG_IMG.split()]
        PIC = random.choice(DRG)
        try:
            await event.client.send_file(
                event.chat_id, PIC, caption=caption, reply_to=reply_to_id
            )
            await event.delete()
        except (WebpageMediaEmptyError, MediaEmptyError, WebpageCurlFailedError):
            return await edit_or_reply(
                event,
                f"**Media Value Error!!**\n__Ubah tautan dengan__ `.setdv`\n\n**__Tidak bisa mendapatkan media dari tautan ini :-**__ `{PIC}`",
            )
    else:
        await edit_or_reply(
            event,
            caption,
        )


temp = """=============================
{ALIVE_TEXT} 
=============================
**{EMOJI} Database :** `{dbhealth}`
**{EMOJI} Telethon Version :** `{telever}`
**{EMOJI} Dragons-userbot Version :** `{drgver}`
**{EMOJI} Python Version :** `{pyver}`
**{EMOJI} Uptime :** `{uptime}`
**{EMOJI} Master :** {mention}
============================="""


@drgub.drg_cmd(
    pattern="ialive$",
    command=("ialive", plugin_category),
    info={
        "header": "Untuk memeriksa status hidup bot melalui mode inline",
        "options": "Untuk menampilkan media dalam hal ini perintah kamu butuh `set ALIVE_PIC` dengan tautan media, dapatkan ini dengan membalas media dengan `{tr}tgm`",
        "usage": [
            "{tr}alive",
        ],
    },
)
async def amireallyalive(event):
    "Semacam menampilkan detail bot oleh bot inline Anda"
    reply_to_id = await reply_id(event)
    EMOJI = gvarstatus("ALIVE_EMOJI") or "✥"
    ALIVE_TEXT = gvarstatus("ALIVE_TEXT") or "Dragons-Userbot Aktif"
    drg_caption = f"**{ALIVE_TEXT}**\n\n"
    drg_caption += f"**{EMOJI} Telethon version :** `{version.__version__}\n`"
    drg_caption += f"**{EMOJI} Dragons-userbot Version :** `{drgversion}`\n"
    drg_caption += f"**{EMOJI} Python Version :** `{python_version()}\n`"
    drg_caption += f"**{EMOJI} Master :** {mention}\n"
    results = await event.client.inline_query(Config.TG_BOT_USERNAME, drg_caption)
    await results[0].click(event.chat_id, reply_to=reply_to_id, hide_via=True)
    await event.delete()


@drgub.tgbot.on(CallbackQuery(data=re.compile(b"stats")))
async def on_plug_in_callback_query_handler(event):
    statstext = await drgalive(StartTime)
    await event.answer(statstext, cache_time=0, alert=True)
