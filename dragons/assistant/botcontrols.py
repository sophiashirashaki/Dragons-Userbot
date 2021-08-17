import asyncio
from datetime import datetime

from telethon.errors import BadRequestError, FloodWaitError, ForbiddenError

from dragons import drgub

from ..Config import Config
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from ..helpers import reply_id, time_formatter
from ..helpers.utils import _format
from ..sql_helper.bot_blacklists import check_is_black_list, get_all_bl_users
from ..sql_helper.bot_starters import del_starter_from_db, get_all_starters
from ..sql_helper.globals import addgvar, delgvar, gvarstatus
from . import BOTLOG, BOTLOG_CHATID
from .botmanagers import (
    ban_user_from_bot,
    get_user_and_reason,
    progress_str,
    unban_user_from_bot,
)

LOGS = logging.getLogger(__name__)

plugin_category = "bot"
botusername = Config.TG_BOT_USERNAME
cmhd = Config.COMMAND_HAND_LER


@drgub.bot_cmd(
    pattern=f"^/help$",
    from_users=Config.OWNER_ID,
)
async def bot_help(event):
    await event.reply(
        f"""Perintah di bot adalah:
**Note : **__Perintah ini hanya berfungsi di bot ini__ {botusername}

• **Cmd : **/uinfo <reply to user message>
• **Info : **__Anda telah memperhatikan bahwa stiker/emoji yang diteruskan tidak memiliki tag penerusan sehingga Anda dapat mengidentifikasi pengguna yang mengirim pesan tersebut dengan cmd ini__
• **Note : **__Ini berfungsi untuk semua pesan yang diteruskan. bahkan untuk pengguna yang izin meneruskan pesan tidak ada__

• **Cmd : **/ban <reason> or /ban <username/userid> <reason>
• **Info : **__Balas pesan pengguna dengan alasan sehingga dia akan diberi tahu saat Anda diblokir dari bot dan pesannya tidak akan diteruskan ke Anda lebih lanjut__
• **Note : **__Alasan adalah keharusan, tanpa alasan itu tidak akan berhasil__

• **Cmd : **/unban <reason(optional)> or /unban <username/userid>
• **Info : **__Balas pesan pengguna atau berikan nama pengguna/id pengguna untuk membatalkan larangan dari bot__
• **Note : **__Untuk memeriksa daftar pengguna yang diblokir gunakan__ `{cmhd}bblist`.

• **Cmd : **/broadcast
• **Info : **__Balas pesan untuk disiarkan ke setiap pengguna yang memulai bot Anda. Untuk mendapatkan daftar pengguna gunakan__ `{cmhd}bot_users`
• **Note : **__jika pengguna menghentikan/memblokir bot maka dia akan dihapus dari database Anda yaitu dia akan dihapus dari daftar bot_starters__
"""
    )


@drgub.bot_cmd(
    pattern=f"^/broadcast$",
    from_users=Config.OWNER_ID,
)
async def bot_broadcast(event):
    replied = await event.get_reply_message()
    if not replied:
        return await event.reply("Membalas pesan untuk Siaran Pertama!")
    start_ = datetime.now()
    br_cast = await replied.reply("Menyiarkan ...")
    blocked_users = []
    count = 0
    bot_users_count = len(get_all_starters())
    if bot_users_count == 0:
        return await event.reply("`Belum ada yang memulai bot Anda`")
    users = get_all_starters()
    if users is None:
        return await event.reply("`Terjadi kesalahan saat mengambil daftar pengguna`")
    for user in users:
        try:
            await event.client.send_message(
                int(user.user_id), "🔊 Anda Menerima Pesan **Baru** Menyiarkan"
            )
            await event.client.send_message(int(user.user_id), replied)
            await asyncio.sleep(0.8)
        except FloodWaitError as e:
            await asyncio.sleep(e.seconds)
        except (BadRequestError, ValueError, ForbiddenError):
            del_starter_from_db(int(user.user_id))
        except Exception as e:
            LOGS.error(str(e))
            if BOTLOG:
                await event.client.send_message(
                    BOTLOG_CHATID, f"**Error saat siaran**\n`{str(e)}`"
                )
        else:
            count += 1
            if count % 5 == 0:
                try:
                    prog_ = (
                        "🔊 Menyiarkan ...\n\n"
                        + progress_str(
                            total=bot_users_count,
                            current=count + len(blocked_users),
                        )
                        + f"\n\n• ✔️ **Berhasil** :  `{count}`\n"
                        + f"• ✖️ **Gagal** :  `{len(blocked_users)}`"
                    )
                    await br_cast.edit(prog_)
                except FloodWaitError as e:
                    await asyncio.sleep(e.seconds)
    end_ = datetime.now()
    b_info = f"🔊  Berhasil menyiarkan pesan ke ➜  <b>{count} Pengguna</b>"
    if len(blocked_users) != 0:
        b_info += f"\n🚫  <b>{len(blocked_users)} Pengguna</b> memblokir bot Anda baru-baru ini, jadi telah dihapus"
    b_info += (
        f"\n⏳  <code>Proses mengambil : {time_formatter((end_ - start_).seconds)}</code>"
    )
    await br_cast.edit(b_info, parse_mode="html")


@drgub.drg_cmd(
    pattern=f"bot_users$",
    command=("bot_users", plugin_category),
    info={
        "header": "Untuk mendapatkan daftar pengguna yang memulai bot",
        "description": "Untuk mendapatkan daftar lengkap pengguna yang memulai bot Anda",
        "usage": "{tr}bot_users",
    },
)
async def ban_starters(event):
    "Untuk mendapatkan daftar pengguna yang memulai bot"
    ulist = get_all_starters()
    if len(ulist) == 0:
        return await edit_delete(event, "`Belum ada yang memulai bot Anda`")
    msg = "**Daftar pengguna yang memulai bot Anda adalah :\n\n**"
    for user in ulist:
        msg += f"• 👤 {_format.mentionuser(user.first_name , user.user_id)}\n**ID Pengguna :** `{user.user_id}`\n**Username :** @{user.username}\n**Tanggal : **__{user.date}__\n\n"
    await edit_or_reply(event, msg)


@drgub.bot_cmd(
    pattern=f"^/ban\s+([\s\S]*)",
    from_users=Config.OWNER_ID,
)
async def ban_botpms(event):
    user_id, reason = await get_user_and_reason(event)
    reply_to = await reply_id(event)
    if not user_id:
        return await event.client.send_message(
            event.chat_id, "`Saya tidak dapat menemukan pengguna untuk diblokir`", reply_to=reply_to
        )
    if not reason:
        return await event.client.send_message(
            event.chat_id, "`Untuk memblokir pengguna memberikan alasan terlebih dahulu`", reply_to=reply_to
        )
    try:
        user = await event.client.get_entity(user_id)
        user_id = user.id
    except Exception as e:
        return await event.reply(f"**Error :**\n`{str(e)}`")
    if user_id == Config.OWNER_ID:
        return await event.reply("Aku tidak bisa memblokirmu master")
    check = check_is_black_list(user.id)
    if check:
        return await event.client.send_message(
            event.chat_id,
            f"#Sudah_Diblokir\
            \nPengguna sudah ada di daftar Pengguna yang Diblokir\
            \n**Alasan untuk diblokir :** `{check.reason}`\
            \n**Tanggal :** `{check.date}`.",
        )
    msg = await ban_user_from_bot(user, reason, reply_to)
    await event.reply(msg)


@drgub.bot_cmd(
    pattern=f"^/unban(?:\s|$)([\s\S]*)",
    from_users=Config.OWNER_ID,
)
async def ban_botpms(event):
    user_id, reason = await get_user_and_reason(event)
    reply_to = await reply_id(event)
    if not user_id:
        return await event.client.send_message(
            event.chat_id, "`Saya tidak dapat menemukan pengguna untuk membatalkan pemblokiran`", reply_to=reply_to
        )
    try:
        user = await event.client.get_entity(user_id)
        user_id = user.id
    except Exception as e:
        return await event.reply(f"**Error :**\n`{str(e)}`")
    check = check_is_black_list(user.id)
    if not check:
        return await event.client.send_message(
            event.chat_id,
            f"#Pengguna_Tidak_Diblokir\
            \n• 👤 {_format.mentionuser(user.first_name , user.id)} tidak ada di daftar Pengguna Diblokir saya",
        )
    msg = await unban_user_from_bot(user, reason, reply_to)
    await event.reply(msg)


@drgub.drg_cmd(
    pattern=f"bblist$",
    command=("bblist", plugin_category),
    info={
        "header": "Untuk mendapatkan daftar pengguna yang diblokir di bot",
        "description": "Untuk mendapatkan daftar pengguna yang diblokir di bot",
        "usage": "{tr}bblist",
    },
)
async def ban_starters(event):
    "Untuk mendapatkan daftar pengguna yang diblokir di bot"
    ulist = get_all_bl_users()
    if len(ulist) == 0:
        return await edit_delete(event, "`Belum ada yang diblokir di bot Anda`")
    msg = "**Daftar pengguna yang diblokir di bot Anda adalah :\n\n**"
    for user in ulist:
        msg += f"• 👤 {_format.mentionuser(user.first_name , user.chat_id)}\n**ID Pengguna :** `{user.chat_id}`\n**Username :** @{user.username}\n**Tanggal : **__{user.date}__\n**Reason:** __{user.reason}__\n\n"
    await edit_or_reply(event, msg)


@drgub.drg_cmd(
    pattern=f"bot_antif (on|off)$",
    command=("bot_antif", plugin_category),
    info={
        "header": "Untuk mengaktifkan atau menonaktifkan bot antiflood",
        "description": "jika diaktifkan maka setelah 10 pesan atau 10 pengeditan pesan yang sama dalam waktu yang lebih singkat maka bot Anda akan menguncinya secara otomatis",
        "usage": [
            "{tr}bot_antif on",
            "{tr}bot_antif off",
        ],
    },
)
async def ban_antiflood(event):
    "Untuk mengaktifkan atau menonaktifkan bot antiflood"
    input_str = event.pattern_match.group(1)
    if input_str == "on":
        if gvarstatus("bot_antif") is not None:
            return await edit_delete(event, "`Bot Antiflood sudah diaktifkan`")
        addgvar("bot_antif", True)
        await edit_delete(event, "`Bot Antiflood Diaktifkan`")
    elif input_str == "off":
        if gvarstatus("bot_antif") is None:
            return await edit_delete(event, "`Bot Antiflood sudah dinonaktifkan`")
        delgvar("bot_antif")
        await edit_delete(event, "`Bot Antiflood Diaktifkan`")
