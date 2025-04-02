import telebot
from telebot import types
import sqlite3

bot = telebot.TeleBot('7810697763:AAH6k1LpjJXnAYjmFlQO-0WWhq8q2ON_Ld4')

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('📊 Отчет')
    btn2 = types.KeyboardButton('💸 Ввод трат')
    btn3 = types.KeyboardButton('💰 Ввод дохода')
    markup.add(btn1, btn2, btn3)
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    conn = sqlite3.connect('tgfinbot.sql')
    cur = conn.cursor()
    cur.execute('''
               CREATE TABLE IF NOT EXISTS users (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name VARCHAR(50),
                   pass VARCHAR(50)
               )
           ''')
    conn.commit()
    cur.close()
    conn.close()

    bot.send_message(message.chat.id, 'Привет! Авторизируйтесь для продолжения. Введите имя', reply_markup=main_menu())
    bot.register_next_step_handler(message, user_name)

def user_name(message):
    global name
    name = message.text.strip()
    bot.send_message(message.chat.id, "Введите пароль", reply_markup=main_menu())
    bot.register_next_step_handler(message, user_pass)

def user_pass(message):
    password = message.text.strip()
    conn = sqlite3.connect('tgfinbot.sql')
    cur = conn.cursor()
    cur.execute('INSERT INTO users (name, pass) VALUES (?, ?)', (name, password))
    conn.commit()
    cur.close()
    conn.close()

    bot.send_message(message.chat.id, "Вы зарегистрированы!", reply_markup=main_menu())

@bot.message_handler(commands=['help'])
def main(message):
    bot.send_message(message.chat.id, 'Help information. Список команд', reply_markup=main_menu())

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text == '📊 Отчет':
        bot.send_message(message.chat.id, 'Вы выбрали отчет', reply_markup=main_menu())
    elif message.text == '💸 Ввод трат':
        bot.send_message(message.chat.id, 'Вы выбрали ввод трат', reply_markup=main_menu())
    elif message.text == '💰 Ввод дохода':
        bot.send_message(message.chat.id, 'Вы выбрали ввод дохода', reply_markup=main_menu())
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, выберите одну из опций', reply_markup=main_menu())

bot.polling(none_stop=True)
