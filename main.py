import new
import datetime
import threading
import types
import telebot
from telebot import types
import requests

api_key = "5720580673:AAE0B84CqzcHewcIVrInhrpbA4g8VLd8Yvo"

TOKEN = '5720580673:AAE0B84CqzcHewcIVrInhrpbA4g8VLd8Yvo'

bot = telebot.TeleBot(token=TOKEN)


# редактируем кнопку старт, т.е после нажатия старт в чате появиться текст с приветствием и кнопкой для добавления напоминания
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     'Привет! Я бот, который с радостью напомнит о событиях, заданиях и так далее. Вы можете создать таймер или посмотреть все назначенные события GoogleCalendar',
                     reply_markup=get_keyboard())


# создаем кнопку установки напоминания
def get_keyboard():
    keyboard = telebot.types.InlineKeyboardMarkup()
    button = telebot.types.InlineKeyboardButton('Создать напоминание', callback_data='set timer')
    button_google = telebot.types.InlineKeyboardButton('Создать напоминание для Calendar', callback_data='set reminder')
    keyboard.add(button, button_google)
    return keyboard


def get_last_message():
    url = "https://api.telegram.org/bot{}/getUpdates".format(api_key)
    response = requests.get(url)
    data = response.json()
    last_msg = data['result'][len(data['result']) - 1]['message']['text']
    chat_id = data['result'][len(data['result']) - 1]['message']['chat']['id']
    update_id = data['result'][len(data['result']) - 1]['update_id']
    if len(data['result']) < 100:
        return last_msg, chat_id, update_id
    else:
        print('offseting updates limit...')
        url = "https://api.telegram.org/bot{}/getUpdates?offset={}".format(api_key, update_id)
        response = requests.get(url)
        data = response.json()
        last_msg = data['result'][len(data['result']) - 1]['message']['text']
        chat_id = data['result'][len(data['result']) - 1]['message']['chat']['id']
        update_id = data['result'][len(data['result']) - 1]['update_id']
        return last_msg, chat_id, update_id


# функция запроса (кнопки), которая просит ввести время, а также выведет пример ввода
@bot.callback_query_handler(func=lambda x: x.data == 'set timer')
def pre_set_timer(query):
    message = query.message
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("30 сек")
    btn2 = types.KeyboardButton("1 мин")
    btn3 = types.KeyboardButton("30 мин")
    btn4 = types.KeyboardButton("1 час")
    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(message.chat.id,
                     'Введите время для установки таймера.\n'
                     'Пример ввода: 30 сек',
                     reply_markup=markup)
    bot.register_next_step_handler(message, set_time)


# функция, которая будет принимать число
def set_time(message):
    times = {
        'сек': 0,
        'мин': 0,
        'час': 0
    }

    quantity, type_time = message.text.split()

    if type_time not in times.keys():
        bot.send_message(message.chat.id,
                         'Вы ввели неправильный тип времени.')
        return

    if not quantity.isdigit():
        bot.send_message(message.chat.id,
                         'Вы ввели не число')

    times[type_time] = int(quantity)

    pre_set_text(message, times)


def pre_set_text(message, times):
    bot.send_message(message.chat.id,
                     'Введите текст, который придёт после'
                     ' истечения таймера.')
    bot.register_next_step_handler(message, set_text, times)


def set_text(message, times):
    cur_date = datetime.datetime.now()

    timedelta = datetime.timedelta(days=0, seconds=times['сек'],
                                   minutes=times['мин'], hours=times['час'])

    cur_date += timedelta

    users[message.chat.id] = (cur_date, message.text)
    bot.send_message(message.chat.id,
                     'Спасибо! Через заданное время вам'
                     ' придёт уведомление.')


def check_date():
    now_date = datetime.datetime.now()
    users_to_delete = []
    for chat_id, value in users.items():
        user_date = value[0]
        msg = value[1]
        if now_date >= user_date:
            bot.send_message(chat_id, msg)
            users_to_delete.append(chat_id)
    for user in users_to_delete:
        del users[user]
    threading.Timer(1, check_date).start()


@bot.callback_query_handler(func=lambda x: x.data == 'set reminder')
def pre_set_reminder(query):
    message = query.message
    bot.send_message(message.chat.id, 'Напомнить события GoogleCalendar\n')
    bot.register_next_step_handler(message, new.main())


if __name__ == '__main__':
    users = {}
    while True:
        try:
            check_date()
            bot.polling()
        except:
            print('Что-то сломалось. Перезагрузка')

