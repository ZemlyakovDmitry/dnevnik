from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

keyboard_shpora = InlineKeyboardMarkup()
keyboard_shpora.add(InlineKeyboardButton('Шпаргалка', callback_data='shpora'))

keyboard_menu = InlineKeyboardMarkup()
keyboard_menu = InlineKeyboardMarkup()
keyboard_menu.row(InlineKeyboardButton('Расписание', callback_data='rasp'), InlineKeyboardButton('ДЗ', callback_data='dz'))
keyboard_menu.row(InlineKeyboardButton('Оценки', callback_data='ball'), InlineKeyboardButton('Меню', callback_data='menu'))
keyboard_menu.row(InlineKeyboardButton('Доска объявлений', callback_data='announcements'))
keyboard_menu.add(InlineKeyboardButton('Удалить аккаунт', callback_data='remove'))