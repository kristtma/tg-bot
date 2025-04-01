import telebot
import sqlite3
bot = telebot.TeleBot('7810697763:AAH6k1LpjJXnAYjmFlQO-0WWhq8q2ON_Ld4')



@bot.message_handler(commands = ['start'])
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
    bot.send_message(message.chat.id, 'Привет! Авторизируйтесь для продолжения. Введите имя')
    bot.register_next_step_handler(message, user_name)
def user_name(message):
    global name
    name = message.text.strip()
    bot.send_message(message.chat.id, "Введите пароль")
    bot.register_next_step_handler(message, user_pass)
def user_pass(message):
    password = message.text.strip()
    conn = sqlite3.connect('tgfinbot.sql')
    cur = conn.cursor()
    cur.execute('INSERT INTO users (name, last_name) VALUES (?, ?)', (name, password))
    conn.commit()
    cur.close()
    conn.close()

    bot.send_message(message.chat.id, "Вы зарегистрированы!")
@bot.message_handler(commands = ['help'])
def main(message):
    bot.send_message(message.chat.id, 'Help information. Список комманд')

bot.polling(none_stop=True)