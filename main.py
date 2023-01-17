import telebot
from telebot import types
import conf
import random
import pandas as pd
import copy

df_base = pd.read_csv('cities.csv', sep='\t')
df_base['played'] = 0

bot = telebot.TeleBot(conf.TOKEN)

#Словарь с пользователями, чтобы бот помнил для каждого пользователя свои настройки
users = {}
default_settings = {'game_status': 0, 'difficult': 1, 'threshold': 500000, 'key_letter': '', 'df': copy.deepcopy(df_base)}


@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    bot.send_message(user_id, "Привет! Этот бот знает все города России* и может сыграть с вами в них. Чтобы начать игру - отправьте /startgame. Если вы хотите узнать больше информации о городе - перешлите название города с командой /info. В начале игры вам надо будет выбрать сложность. Чем выше сложность - тем больше городов будет знать бот. Удачи! :)\n\n\n\n\n\n*Имеются в виду города, указанные на соответствующей странице Википедии, бот не оспаривает территориальную целостность России")


@bot.message_handler(commands=['info'])
def send_info(message):
    user_id = message.chat.id
    try:
        city = message.reply_to_message.text.lower()
        if is_city(bot, city, user_id):
            info = df_base[df_base['city'] == city]['description'].tolist()[0]
            bot.send_message(user_id, info)
    except AttributeError:
        bot.send_message(user_id, 'Перешлите название города, информацию о котором, хотите узнать')


@bot.message_handler(commands=['startgame'])
def send_welcome(message):
    user_id = message.chat.id
    users[user_id] = copy.deepcopy(default_settings)
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text="Просто", callback_data="button1")
    button2 = types.InlineKeyboardButton(text="Нормально", callback_data="button2")
    button3 = types.InlineKeyboardButton(text="Сложно", callback_data="button3")
    keyboard.add(button1)
    keyboard.add(button2)
    keyboard.add(button3)
    bot.send_message(message.chat.id, "Выберите, пожалуйста, сложность игры", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    user_id = call.message.chat.id
    if call.message:
        users[user_id]['game_status'] = 1
        if call.data == "button1":
            users[user_id]['difficult'] = 1
            users[user_id]['threshold'] = 500000
        if call.data == "button2":
            users[user_id]['difficult'] = 2
            users[user_id]['threshold'] = 100000
        if call.data == "button3":
            users[user_id]['difficult'] = 3
            users[user_id]['threshold'] = 0
        bot.send_message(user_id, 'Назовите город')

#Функции, проверяющие валидность инпута     

def is_city(bot, city, user_id):
    if city in df_base['city'].tolist():
        return True
    else:
        bot.send_message(user_id, 'Это не город')
        return False

def last_letter(city):
    if city.endswith('ый'):
        return city[-3]
    elif city[-1] not in ['ь', 'ы', 'й']:
        return city[-1]
    else:
        return city[-2]

def is_played(bot, city, user_id):
    df = users[user_id]['df']
    row = df[df['city'] == city].index
    if df['played'][row].tolist()[0] == 0:
        return True
    else:
        bot.send_message(user_id, 'Этот город уже называли')
        return False


def is_valid(bot, city, user_id):
    if users[user_id]['key_letter']:
        if city[0] == users[user_id]['key_letter']:
            return True
        else:
            bot.send_message(user_id, 'Не с той буквы начинается')
            return False
    else:
        return True


def mark_as_played(user_id, city):
    city = city.lower()
    df = users[user_id]['df']
    row = df[df['city'] == city].index
    df['played'][row] = 1
    users[user_id]['df'] = df


def bot_turn(bot, user_id):
    key_letter = users[user_id]['key_letter']
    df = users[user_id]['df']
    threshold = users[user_id]['threshold']
    sub_df = df[(df['first_letter'] == key_letter) & (df['population'] > threshold) & (df['played'] == 0)]
    if not sub_df.empty:
        city = random.choice(sub_df['City'].tolist())
        mark_as_played(user_id, city)
        users[user_id]['key_letter'] = last_letter(city)
        bot.send_message(user_id, city)
        bot.send_message(user_id, 'Тебе на ' + users[user_id]['key_letter'])
        
    else:
        bot.send_message(user_id, 'Я больше не знаю городов, победа за тобой! Поздравляю! \nНажми /startgame, чтобы начать новую игру')
        users[user_id]['game_status'] = 0


@bot.message_handler(content_types=['text'])
def echo(message):
    user_id = message.chat.id
    city = message.text.lower()
    if is_city(bot, city, user_id) and is_valid(bot, city, user_id) and is_played(bot, city, user_id):
        mark_as_played(user_id, city)
        users[user_id]['key_letter'] = last_letter(city)
        bot_turn(bot, user_id)

if __name__ == '__main__':
    bot.polling(none_stop=True)
