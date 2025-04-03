import telebot
from telebot import types
import sqlite3
import matplotlib.pyplot as plt
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
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT, 
            amount REAL, 
            category TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

    bot.send_message(message.chat.id, 'Добро пожаловать в финансовый бот!', reply_markup=main_menu())

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

@bot.message_handler(func=lambda message: message.text == '💸 Ввод трат')
def ask_expense_amount(message):
    bot.send_message(message.chat.id, "Введите сумму траты:")
    bot.register_next_step_handler(message, save_expense_amount)

def save_expense_amount(message):
    global expense_amount
    try:
        expense_amount = float(message.text.strip())
        bot.send_message(message.chat.id, "Введите категорию траты (например, еда, транспорт, развлечения):")
        bot.register_next_step_handler(message, save_expense_category)
    except ValueError:
        bot.send_message(message.chat.id, "Ошибка! Введите число.")
        bot.register_next_step_handler(message, save_expense_amount)

def save_expense_category(message):
    category = message.text.strip()
    user_id = message.chat.id

    conn = sqlite3.connect('tgfinbot.sql')
    cur = conn.cursor()
    cur.execute('INSERT INTO transactions (user_id, type, amount, category) VALUES (?, ?, ?, ?)',
                (user_id, 'expense', expense_amount, category))
    conn.commit()
    cur.close()
    conn.close()

    bot.send_message(message.chat.id, f"✅ Трата {expense_amount} руб. на {category} сохранена!", reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == '💰 Ввод дохода')
def ask_income_amount(message):
    bot.send_message(message.chat.id, "Введите сумму дохода:")
    bot.register_next_step_handler(message, save_income_amount)

def save_income_amount(message):
    try:
        income_amount = float(message.text.strip())
        user_id = message.chat.id

        conn = sqlite3.connect('tgfinbot.sql')
        cur = conn.cursor()
        cur.execute('INSERT INTO transactions (user_id, type, amount, category) VALUES (?, ?, ?, ?)',
                    (user_id, 'income', income_amount, None))  # Категория теперь NULL
        conn.commit()
        cur.close()
        conn.close()

        bot.send_message(message.chat.id, f"✅ Доход {income_amount} руб. сохранён!", reply_markup=main_menu())

    except ValueError:
        bot.send_message(message.chat.id, "Ошибка! Введите число.")
        bot.register_next_step_handler(message, save_income_amount)

    bot.send_message(message.chat.id, f"✅ Доход {income_amount} руб.  сохранён!", reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == '📊 Отчет')
def send_report(message):
    user_id = message.chat.id

    # Подключаемся к базе данных
    conn = sqlite3.connect('tgfinbot.sql')
    cur = conn.cursor()

    # Получаем доходы
    cur.execute("SELECT SUM(amount) FROM transactions WHERE user_id = ? AND type = 'income'", (user_id,))
    total_income = cur.fetchone()[0]
    total_income = total_income if total_income else 0  # Если нет доходов, ставим 0

    # Получаем расходы по категориям
    cur.execute("SELECT category, SUM(amount) FROM transactions WHERE user_id = ? AND type = 'expense' GROUP BY category", (user_id,))
    expenses = cur.fetchall()

    cur.close()
    conn.close()

    # Обрабатываем данные для отчета
    expense_categories = []
    expense_amounts = []

    for category, amount in expenses:
        if category and amount:
            expense_categories.append(category)
            expense_amounts.append(amount)

    total_expenses = sum(expense_amounts)

    # Считаем баланс
    balance = total_income - total_expenses

    # Создаем текст отчета
    report_text = f"📊 *Отчет за Апрель 2025*\n\n"
    report_text += f"*Доходы:* {total_income} руб.\n\n"
    report_text += "*Расходы:*\n"
    for cat, amt in zip(expense_categories, expense_amounts):
        report_text += f"  - {cat}: {amt} руб.\n"
    report_text += f"\n*Итого расходов:* {total_expenses} руб.\n"
    report_text += f"\n💰 *Баланс:* {balance} руб."

    # Строим диаграмму расходов
    if expense_categories:
        plt.figure(figsize=(6, 6))
        plt.pie(expense_amounts, labels=expense_categories, autopct='%1.1f%%', startangle=140, colors=['#ff9999','#66b3ff','#99ff99','#ffcc99'])
        plt.axis('equal')  # Круглая форма

        # Сохраняем диаграмму
        report_image_path = "report.png"
        plt.savefig(report_image_path, bbox_inches='tight')
        plt.close()

        # Отправляем отчет
        bot.send_photo(message.chat.id, open(report_image_path, 'rb'), caption=report_text, parse_mode="Markdown")

    else:
        bot.send_message(message.chat.id, report_text, parse_mode="Markdown")

bot.polling(none_stop=True)

