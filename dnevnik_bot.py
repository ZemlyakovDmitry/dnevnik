import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from netschoolapi import NetSchoolAPI
import pickle
import random
import re
import sys
import datetime
import time
from bs4 import BeautifulSoup
from keyboard import keyboard_menu, keyboard_shpora
from data import User, Account

logging.basicConfig(level=logging.INFO)
bot = Bot(token='TOKEN')
dp = Dispatcher(bot)

try:
    with open('user.pkl', 'rb') as f:
        user_dict = pickle.load(f)
    print('\n\nИмпортировал пользоваталей\n\n')
except Exception:
    print('\n\nСоздал пустых пользователей\n\n')
    user_dict = {}
try:
    with open('account.pkl', 'rb') as f:
        account_dict = pickle.load(f)
    print('\n\nИмпортировал аккаунты\n\n')
except Exception:
    print('\n\nСоздал пустые аккаунты\n\n')
    account_dict = {}

@dp.message_handler(commands=['start'])
async def _(message: types.Message):
    try:
        keyboard = InlineKeyboardMarkup()
        user = user_dict[message.from_user.id]
        for account in user.accounts:
            keyboard.add(InlineKeyboardButton(account_dict[account].login + ' ' + account_dict[account].dnevnik, callback_data=account))
        keyboard.add(InlineKeyboardButton('Новый аккаунт', callback_data='new_account'))
        await message.reply('Привет!\nНужно выбрать аккаунт или создать новый.', reply_markup=keyboard)
    except Exception as e:
        user_dict[message.from_user.id] = User(message.from_user.id)
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton('Новый аккаунт', callback_data='new_account'))
        await message.reply('Отлично!\nНужно создать аккаунт. :)', reply_markup = keyboard)

@dp.callback_query_handler(text='new_account')
async def _(message: types.CallbackQuery):
    await bot.answer_callback_query(message.id)
    user = user_dict[message.from_user.id]
    id = str(random.randint(1, 999999) * message.from_user.id)
    account_dict[id] = Account(id)
    user.accounts.append(id)
    account_dict[id].dnevnik = 'Сетевой город'
    user.logic = 'login'
    user.account_id = id
    await bot.send_message(message.from_user.id, 'Введи логин и пароль через пробел.\nПример: ВасяПупкин ПарольВаси')

@dp.message_handler(commands=['menu'])
async def _(message: types.Message):
    user = user_dict[message.from_user.id]
    await bot.send_message(message.from_user.id, 'Выбирай', reply_markup = keyboard_menu)

@dp.callback_query_handler(text='menu')
async def _(message: types.CallbackQuery):
    await bot.answer_callback_query(message.id)
    keyboard = InlineKeyboardMarkup()
    user = user_dict[message.from_user.id]
    for account in user.accounts:
        keyboard.add(InlineKeyboardButton(account_dict[account].login + ' ' + account_dict[account].dnevnik, callback_data=account))
    keyboard.add(InlineKeyboardButton('Новый аккаунт', callback_data='new_account'))
    await bot.send_message(message.from_user.id, 'Выбери аккаунт или создай новый', reply_markup=keyboard)

@dp.callback_query_handler(text='rasp')
async def _(message: types.CallbackQuery):
    await bot.answer_callback_query(message.id)
    user = user_dict[message.from_user.id]
    user.logic = 'rasp'
    keyboard = InlineKeyboardMarkup()
    tommorow = InlineKeyboardButton('Завтра', callback_data='tomorrow')
    today = InlineKeyboardButton('Сегодня', callback_data='today')
    yesterday = InlineKeyboardButton('Вчера', callback_data='yesterday')
    back = InlineKeyboardButton('Назад', callback_data='back')
    keyboard.row(tommorow, today, yesterday).row(back)
    await bot.send_message(message.from_user.id, 'Выбери дату за которую нужно предоставить расписание', reply_markup=keyboard)

@dp.callback_query_handler(text='dz')
async def _(message: types.CallbackQuery):
    await bot.answer_callback_query(message.id)
    user = user_dict[message.from_user.id]
    user.logic = 'dz'
    keyboard = InlineKeyboardMarkup()
    tommorow = InlineKeyboardButton('Завтра', callback_data='tomorrow')
    today = InlineKeyboardButton('Сегодня', callback_data='today')
    yesterday = InlineKeyboardButton('Вчера', callback_data='yesterday')
    back = InlineKeyboardButton('Назад', callback_data='back')
    keyboard.row(tommorow, today, yesterday).row(back)
    await bot.send_message(message.from_user.id, 'Выбери дату за которую нужно предоставить домашнее задание', reply_markup=keyboard)

@dp.callback_query_handler(text='ball')
async def _(message: types.CallbackQuery):
    await bot.answer_callback_query(message.id)
    user = user_dict[message.from_user.id]
    user.logic = 'ball'
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton('Сегодня', callback_data='today'), InlineKeyboardButton('Вчера', callback_data='yesterday'))
    keyboard.add(InlineKeyboardButton('Назад', callback_data='back'))
    await bot.send_message(message.from_user.id, 'Выбери дату за которую нужно предоставить оценку', reply_markup=keyboard)

@dp.callback_query_handler(text='tomorrow')
async def _(message: types.CallbackQuery):
    await bot.answer_callback_query(message.id)
    user = user_dict[message.from_user.id]
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    account = account_dict[user.account_id]
    result = ''
    async with NetSchoolAPI(account.url, account.login, account.password, (account.oblast, account.okrug, account.sity, account.type, account.school)) as api:
        diary = await api.get_diary(week_start=tomorrow, week_end=tomorrow)
    if user.logic == 'rasp':
        try:
            for lesson in diary['weekDays'][0]['lessons']:
                result += '\n'+str(lesson['number'])+'.'+str(lesson['subjectName']) + '(' + str(lesson['startTime']) + '-' + str(lesson['endTime']) + ')'
        except IndexError:
            result = 'На завтра расписания нету!'
    elif user.logic == 'dz':
        try:
            for lesson in diary['weekDays'][0]['lessons']:
                try:
                    result += '\n'+str(lesson['subjectName'])+': '+str(lesson['assignments'][0]['assignmentName'])
                except KeyError:
                    pass
        except IndexError:
            result = 'На завтра дз нету!'
    try:
        await bot.send_message(message.from_user.id, result)
    except Exception:
        await bot.send_message(message.from_user.id, 'Пусто')

@dp.callback_query_handler(text='today')
async def _(message: types.CallbackQuery):
    await bot.answer_callback_query(message.id)
    user = user_dict[message.from_user.id]
    today = datetime.date.today()
    account = account_dict[user.account_id]
    result = ''
    async with NetSchoolAPI(account.url,account.login,account.password,(account.oblast, account.okrug, account.sity, account.type, account.school)) as api:
        diary = await api.get_diary(week_start=today, week_end=today)
    if user.logic == 'rasp':
        try:
            for lesson in diary['weekDays'][0]['lessons']:
                result += '\n'+str(lesson['number'])+'.'+str(lesson['subjectName']) + '(' + str(lesson['startTime']) + '-' + str(lesson['endTime']) + ')'
        except IndexError:
            result = 'На сегодня расписания нету!'
    elif user.logic == 'dz':
        try:
            for lesson in diary['weekDays'][0]['lessons']:
                try:
                    result += '\n'+str(lesson['subjectName'])+': '+str(lesson['assignments'][0]['assignmentName'])
                except KeyError:
                    pass
        except IndexError:
            result = 'На сегодня дз нету!'
    elif user.logic == 'ball':
        ball = {}
        try:
            for lesson in diary['weekDays'][0]['lessons']:
                try:
                    for assignment in lesson['assignments']:
                        try:
                            ball[lesson['subjectName']] += str(assignment['mark']['mark']) + ' '
                        except KeyError:
                            ball[lesson['subjectName']] = str(assignment['mark']['mark']) + ' '
                except KeyError:
                    pass
            result = 'Оценки за сегодня:\n ' + str(ball).replace('{', '').replace('}', '').replace(',', '\n').replace("'", '')
        except Exception:
            result = 'На сегодня оценок нету!'
    try:
        await bot.send_message(message.from_user.id, result)
    except Exception:
        await bot.send_message(message.from_user.id, 'Пусто')

@dp.callback_query_handler(text='yesterday')
async def _(message: types.CallbackQuery):
    await bot.answer_callback_query(message.id)
    user = user_dict[message.from_user.id]
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=+-1)
    account = account_dict[user.account_id]
    result = ''
    async with NetSchoolAPI(account.url,account.login,account.password,(account.oblast, account.okrug, account.sity, account.type, account.school)) as api:
        diary = await api.get_diary(week_start=tomorrow, week_end=tomorrow)
    if user.logic == 'rasp':
        try:
            for lesson in diary['weekDays'][0]['lessons']:
                result += '\n'+str(lesson['number'])+'.'+str(lesson['subjectName']) + '(' + str(lesson['startTime']) + '-' + str(lesson['endTime']) + ')'
        except IndexError:
            result = 'На вчера расписания нету!'
    elif user.logic == 'dz':
        try:
            for lesson in diary['weekDays'][0]['lessons']:
                try:
                    result += '\n'+str(lesson['subjectName'])+': '+str(lesson['assignments'][0]['assignmentName'])
                except KeyError:
                    pass
        except IndexError:
            result = 'На вчера домашнего задания нету!'
    elif user.logic == 'ball':
        ball = {}
        try:
            for lesson in diary['weekDays'][0]['lessons']:
                try:
                    for assignment in lesson['assignments']:
                        try:
                            ball[lesson['subjectName']] += str(assignment['mark']['mark']) + ' '
                        except KeyError:
                            ball[lesson['subjectName']] = str(assignment['mark']['mark']) + ' '
                except Exception:
                    pass
            result = 'Оценки за вчера:\n ' + str(ball).replace('{', '').replace('}', '').replace(',', '\n').replace("'", '')
        except IndexError:
            result = 'На вчера оценок нету!'
    try:
        await bot.send_message(message.from_user.id, result)
    except Exception:
        await bot.send_message(message.from_user.id, 'Пусто')

@dp.callback_query_handler(text='week')
async def _(message: types.CallbackQuery):
    await bot.answer_callback_query(message.id)
    user = user_dict[message.from_user.id]
    account = account_dict[user.account_id]
    result = ''
    async with NetSchoolAPI(account.url,account.login,account.password,(account.oblast, account.okrug, account.sity, account.type, account.school)) as api:
        diary = await api.get_diary()
    if user.logic == 'rasp':
        for day in diary['weekDays']:
            reg_ex = re.search('(.*)-(.*)-).*)T00:00:00', day['date'])
            result += '\n\nДень: ' + reg_ex.group(2) + '-' + reg_ex.group(3)
            for lesson in day['lessons']:
                result += '\n' + str(lesson['number'])+'.'+str(lesson['subjectName']) + '(' + str(lesson['startTime']) + '-' + str(lesson['endTime']) + ')'
    elif user.logic == 'dz':
        for day in diary['weekDays']:
            reg_ex = re.search('(.*)-(.*)-).*)T00:00:00', day['date'])
            result += '\n\nДень: ' + reg_ex.group(2) + '-' + reg_ex.group(3)
            for lesson in day['lessons']:
                try:
                    result += '\n'+str(lesson['subjectName'])+': '+str(lesson['assignments'][0]['assignmentName'])
                except KeyError:
                    pass
    elif user.logic == 'ball':
        ball = {}
        for day in diary['weekDays']:
            reg_ex = re.search('(.*)-(.*)-).*)T00:00:00', day['date'])
            result += '\n\nДень: ' + reg_ex.group(2) + '-' + reg_ex.group(3)
            for lesson in day['lessons']:
                try:
                    for assignment in lesson['assignments']:
                        try:
                            ball[lesson['subjectName']] += str(assignment['mark']['mark']) + ' '
                        except KeyError:
                            ball[lesson['subjectName']] = str(assignment['mark']['mark']) + ' '
                except Exception:
                    pass
        result = 'Оценки за неделю:\n ' + str(ball).replace('{', '').replace('}', '').replace(',', '\n').replace("'", '')
    try:
        await bot.send_message(message.from_user.id, result)
    except Exception:
        await bot.send_message(message.from_user.id, 'Пусто')

@dp.callback_query_handler(text='back')
async def _(message: types.CallbackQuery):
    await bot.answer_callback_query(message.id)
    user = user_dict[message.from_user.id]
    user.logic = None
    await bot.send_message(message.from_user.id, 'Выбирай', reply_markup = keyboard_menu)

@dp.callback_query_handler(text='announcements')
async def _(message: types.CallbackQuery):
    await bot.answer_callback_query(message.id)
    user = user_dict[message.from_user.id]
    account = account_dict[user.account_id]
    async with NetSchoolAPI(account.url,account.login,account.password,(account.oblast, account.okrug, account.sity, account.type, account.school)) as api:
        announcements = await api.get_announcements()
    result = 'Объявления:\n'
    for announcement in announcements:
        result += announcement['name'] + ':\n' + str(announcement['description']) + '\nЗапостили: ' + str(announcement['postDate']) + '\nУдален: ' + str(announcement['deleteDate']) + '\nАвтор: ' + str(announcement['author']['fio']) + '\n\n'
    cleantext = BeautifulSoup(result, "lxml").text
    await bot.send_message(message.from_user.id, cleantext, parse_mode='HTML')

@dp.callback_query_handler(text='remove')
async def _(message: types.CallbackQuery):
    await bot.answer_callback_query(message.id)
    user = user_dict[message.from_user.id]
    try:
        user.accounts.remove(int(user.account_id))
    except ValueError:
        user.accounts.remove(user.account_id)
    user.account_id = None
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('Меню', callback_data='menu'))
    await bot.send_message(message.from_user.id, 'Успешно!\nПерейдите в меню', reply_markup = keyboard)

@dp.message_handler()
async def _(message: types.Message):
    try:
        user = user_dict[message.from_user.id]
        if user.logic == 'login':
            reg_ex = re.search('(.*) (.*)', message.text)
            if reg_ex:
                account_dict[user.account_id].login = reg_ex.group(1)
                account_dict[user.account_id].password = reg_ex.group(2)
                user.logic = None
                try:
                    account = account_dict[user.account_id]
                    account_dict[user.account_id].url = 'ССЫЛКА НА САЙТ ДНЕВНИКА'
                    account_dict[user.account_id].oblast = 'Регион'
                    account_dict[user.account_id].okrug = 'Городской округ / Муниципальный район'
                    account_dict[user.account_id].sity = 'Населённый пункт'
                    account_dict[user.account_id].type = 'Тип ОО'
                    account_dict[user.account_id].school = 'Образовательная организация"'
                    async with NetSchoolAPI(account.url,account.login,account.password,(account.oblast, account.okrug, account.sity, account.type, account.school)) as api:
                        diary = await api.get_diary(week_start=datetime.date.today(), week_end=datetime.date.today())
                    user.account_id = None
                    keyboard = InlineKeyboardMarkup()
                    keyboard.add(InlineKeyboardButton('Меню', callback_data='menu'))
                    await bot.send_message(message.from_user.id, 'Успешно!\nТеперь перейдите в меню и выберите там новый аккаунт', reply_markup=keyboard)
                except Exception as e:
                    user.accounts.remove(user.account_id)
                    user.account_id = None
                    keyboard = InlineKeyboardMarkup()
                    keyboard.add(InlineKeyboardButton('Новый аккаунт', callback_data='new_account'))
                    await bot.send_message(message.from_user.id, 'Ошибка: ' + str(e) + '\nЗаполните по новой', reply_markup = keyboard)
            else:
                await bot.send_message(message.from_user.id, 'Не могу найти в твоем сообщении логин или пароль')
    except Exception as e:
        pass

@dp.callback_query_handler()
async def _(message: types.CallbackQuery):
    await bot.answer_callback_query(message.id)
    user = user_dict[message.from_user.id]
    try:
        account = account_dict[message.data]
        user.account_id = str(message.data)
    except KeyError:
        pass
    await bot.send_message(message.from_user.id, 'Выбирай', reply_markup = keyboard_menu)

try:
    executor.start_polling(dp, skip_updates=True)
except KeyboardInterrupt:
    with open('user.pkl', 'wb') as f:
        pickle.dump(user_dict, f)
    with open('account.pkl', 'wb') as f:
        pickle.dump(account_dict, f)
    print("\nВыполнил сохранение!\n")
    sys.exit()
    
# Made with love by FSB