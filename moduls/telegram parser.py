import configparser
import json

from telethon import TelegramClient
from telethon import connection

# для корректного переноса времени сообщений в json
from datetime import date, datetime

# классы для работы с каналами
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

# класс для работы с сообщениями
from telethon.tl.functions.messages import GetHistoryRequest

# Присваиваем значения внутренним переменным
api_id   = 1593386
api_hash = 'ca3b8849912a60a06c467dcb883a2274'
username = 'bet_bot'

async def main() :
    client = TelegramClient(username, api_id, api_hash)
    client.start('+79162158810')
    client.send_message('me', 'Hello, myself!')




