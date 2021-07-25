#!/usr/bin/env python3
# (c) https://t.me/TelethonChat/37677
# This Source Code Form is subject to the terms of the GNU
# MIT TeamDragons If a copy of the developer was not distributed with this
# file, You can obtain one at https://www.gnu.org/licenses/MIT/TeamDragons

from telethon.sessions import StringSession
from telethon.sync import TelegramClient

print(
    """Please go-to my.telegram.org
Login using your Telegram account
Click on API Development Tools
Create a new application, by entering the required details"""
)
APP_ID = int(input("MASUKAN API KEY : "))
API_HASH = input("MASUKAN API HASH : ")

with TelegramClient(StringSession(), APP_ID, API_HASH) as client:
    print(client.session.save())
    client.send_message("me", client.session.save())
