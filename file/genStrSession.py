#!/usr/bin/env python3
# (c) https://t.me/TelethonChat/37677
# This Source Code Form is subject to the terms of the GNU
# MIT TeamDragons If a copy of the developer was not distributed with this
# file, You can obtain one at https://www.gnu.org/licenses/MIT/TeamDragons


from telethon.sessions import StringSession
from telethon.sync import TelegramClient

print(
    """
  ╔═══╦═══╦═══╦═══╦═══╦═╗─╔╦═══╗
  ╚╗╔╗║╔═╗║╔═╗║╔═╗║╔═╗║║╚╗║║╔═╗║
  ─║║║║╚═╝║║─║║║─╚╣║─║║╔╗╚╝║╚══╗
  ─║║║║╔╗╔╣╚═╝║║╔═╣║─║║║╚╗║╠══╗║
  ╔╝╚╝║║║╚╣╔═╗║╚╩═║╚═╝║║─║║║╚═╝║
  ╚═══╩╝╚═╩╝─╚╩═══╩═══╩╝─╚═╩═══╝
)
print("")
print("""Telethon String Generator""")
print("")
API_KEY = "1273127"
API_HASH = "2626aee4ea587947c6a703f1a0d6a3cc"

while True:
    try:
        with TelegramClient(StringSession(), API_KEY, API_HASH) as client:
            print("")
            session = client.session.save()
            client.send_message(
                "me",
                f"Terimakasih Telah Menggunakan Dragons-Userbot\n\n `{session}` \n\n⚠️ Harap berhati-hati untuk melewati ini value kepada pihak ketiga",
            )
            print(
                "Telethon String Session Anda telah berhasil disimpan dalam akun telegram Anda, Silakan periksa Pesan Tersimpan Telegram Anda"
            )
            print("")
    except:
        print("")
        print("Nomor telepon salah \n pastikan dengan kode negara yang benar")
        print("")
        continue
    break
