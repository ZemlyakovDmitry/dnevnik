Изменённая версия бота https://github.com/0ladyshek/dnevnik для личного пользования (для учеников 1-ой школы, заданной в настройках бота. Ниже подробнее)

Баги фикситься не будут (возможно). Мне лень, а ещё у меня лапки и ОГЭ перед носом.

Отличия от оригинала:
1) Авторизация
2) Некоторые изменения под капотом

Что именно отличается: 
1) Изменена авторизация (Нужно указать логин и пароль, кучу данных не надо указывать)

Как настроить?:
1. Установить либы
pip3 install aiogram netschoolapi bs4


2. В либе netschoolapi изменить файл client.py:

Строка 53: return data.Diary.from_dict(dairy) > return dairy 


3. Изменить файл dnevnik_bot.py:
В строку 16 вставить токен тг бота вместо TOKEN (Получать у t.me/BotFather) 
В строках 319 - 324 изменить следующее: 

                    account_dict[user.account_id].url = 'ССЫЛКА НА САЙТ ДНЕВНИКА'
                    account_dict[user.account_id].oblast = 'Регион'
                    account_dict[user.account_id].okrug = 'Городской округ / Муниципальный район'
                    account_dict[user.account_id].sity = 'Населённый пункт'
                    account_dict[user.account_id].type = 'Тип ОО'
                    account_dict[user.account_id].school = 'Образовательная организация"'
УКАЗЫВАТЬ ВСЁ В ТОЧНОСТИ С САЙТОМ ВАШЕГО СЕТЕВОГО ГОРОДА! ОТ ЗАПЯТОЙ ДО БУКВЫ Ё!!!!!

4. Запуск: python3 dnevnik_bot.py

Ответственности за бота никто не несёт. Всё на ваш страх и риск. 

GNU GPL v3.0

