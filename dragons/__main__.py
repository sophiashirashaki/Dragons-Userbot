import sys

import dragons
from dragons import BOTLOG_CHATID, HEROKU_APP, PM_LOGGER_GROUP_ID

from .Config import Config
from .core.logger import logging
from .core.session import catub
from .utils import (
    add_bot_to_logger_group,
    ipchange,
    load_plugins,
    setup_bot,
    startupmessage,
    verifyLoggerGroup,
)

LOGS = logging.getLogger("DragonsUserbot")

print(dragons.__copyright__)
print("Licensed di bawah ketentuan " + dragons.__license__)

cmdhr = Config.COMMAND_HAND_LER

try:
    LOGS.info("Memulai Userbot")
    catub.loop.run_until_complete(setup_bot())
    LOGS.info("TG Bot Startup Berhasil")
except Exception as e:
    LOGS.error(f"{str(e)}")
    sys.exit()


class CatCheck:
    def __init__(self):
        self.sucess = True


Catcheck = CatCheck()


async def startup_process():
    check = await ipchange()
    if check is not None:
        Catcheck.sucess = False
        return
    await verifyLoggerGroup()
    await load_plugins("plugins")
    await load_plugins("assistant")
    print("➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖")
    print("Yay dragons userbot pengguna Anda secara resmi berfungsi!!!")
    print(
        f"Selamat, sekarang ketik {cmdhr}alive untuk melihat pesan jika dragons-userbot aktif\
        \nJika Anda membutuhkan bantuan, bisa ke https://t.me/KingUserbotSupport"
    )
    print("➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖")
    await verifyLoggerGroup()
    await add_bot_to_logger_group(BOTLOG_CHATID)
    if PM_LOGGER_GROUP_ID != -100:
        await add_bot_to_logger_group(PM_LOGGER_GROUP_ID)
    await startupmessage()
    Catcheck.sucess = True
    return


catub.loop.run_until_complete(startup_process())

if len(sys.argv) not in (1, 3, 4):
    catub.disconnect()
elif not Catcheck.sucess:
    if HEROKU_APP is not None:
        HEROKU_APP.restart()
else:
    try:
        catub.run_until_disconnected()
    except ConnectionError:
        pass
