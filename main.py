from aiogram import Dispatcher, executor, Bot
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import sqlite3
import requests

from Configs import *

STORAGE = MemoryStorage()
BOT = Bot(token=TOKEN)
DB = Dispatcher(BOT, storage=STORAGE)


@DB.message_handler(commands=['start', 'help', 'about', 'history'])
async def StartProgram(message: Message):
    if message.text == '/start':
        await message.answer('Введите город чтобы узнать погоду.')
    elif message.text == '/help':
        await message.answer('По вопросам обращаться к @shavkatov3.')
    elif message.text == '/about':
        await message.answer('Engine WeatherBot - бот поможет узнать погоду.')
    elif message.text == '/history':
        ChatId = message.chat.id
        await SelectFromDataBase(ChatId)
    else:
        await message.answer('Произошла ошибка. Убедитесь что данные корректны')


@DB.message_handler(content_types=['text'])
async def GetInfo(message: Message):
    if message.text in ['/start', '/help', '/about', '/history']:
        await StartProgram(message)
    else:
        ChatId = message.chat.id
        PARAMETERS['q'] = message.text
        try:
            Data = requests.get('https://api.openweathermap.org/data/2.5/weather', params=PARAMETERS).json()
            ChatId = ChatId
            Name = Data['name']
            Temp = Data['main']['temp']
            FeelsLike = Data['main']['feels_like']
            Weather = Data['weather'][0]['description']
            Wind = Data['wind']['speed']
            await SaveToData(ChatId, Name, Temp, FeelsLike, Weather, Wind)
            await message.answer(f'''В городе {Name} сейчас {Temp} °C
            Ощущается как {FeelsLike} °C
            Описание погоды: {Weather}
            Скорость ветра составляет: {Wind} м/с
            ''')
        except:
            await StartProgram(message)


async def SaveToData(ChatId, Name, Temp, FeelsLike, Weather, Wind):
    DataBase = sqlite3.connect('WeatherDataBase.db')
    Cursor = DataBase.cursor()
    Cursor.execute('''
    INSERT INTO history(chatId, city, temp, feelsLike, weather, wind) VALUES (?,?,?,?,?,?)
    ''', (ChatId, Name, Temp, FeelsLike, Weather, Wind))
    DataBase.commit()
    DataBase.close()


async def SelectFromDataBase(ChatId):
    ChatId = ChatId
    DataBase = sqlite3.connect('WeatherDataBase.db')
    Cursor = DataBase.cursor()
    Cursor.execute('''
    SELECT city, temp, feelsLike, weather, wind from history WHERE chatId = ?
    ''', (ChatId, ))
    History = Cursor.fetchall()
    History = History[::-1]
    for Name, Temp, FeelsLike, Weather, Wind in History[:5]:
        await BOT.send_message(ChatId, f'''  История запросов
В городе {Name} сейчас {Temp} °C
Ощущается как {FeelsLike} °C
Описание погоды: {Weather}
Скорость ветра составляет: {Wind} м/с
''')










executor.start_polling(DB)