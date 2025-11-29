import sqlite3
import telebot
from telebot import types

bot = telebot.TeleBot("YOUR-TELEGRAM-BOT-TOKEN")
database = sqlite3.connect("test.db", check_same_thread=False)
cursor = database.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS friends (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    hobby TEXT
)
""")

database.commit()

# main menu (creating inliine buttons)
@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("About", callback_data="about")
    btn2 = types.InlineKeyboardButton("Add friend to database", callback_data="add_to_base")
    btn3 = types.InlineKeyboardButton("Print all database", callback_data="print_all")
    btn4 = types.InlineKeyboardButton("Search in database", callback_data="search_in_database")
    btn5 = types.InlineKeyboardButton("delete person from database", callback_data="delete")
    keyboard.add(btn1, btn2, btn3, btn4, btn5)
    bot.send_message(message.chat.id, "Choose option to do from menu", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda Call: True)
def buttons_calls(call):
    if call.data == "about":
        bot.send_message(call.message.chat.id, "this is bot was created specialy for my portfolio")
    elif call.data == "add_to_base":
        user_add_input = bot.send_message(call.message.chat.id, "Enter name, age, hobby")
        bot.register_next_step_handler(user_add_input, add_to_database)
    elif call.data == "print_all":
        cursor.execute("SELECT * FROM friends")
        rows = cursor.fetchall()

        if len(rows) == 0:
            bot.send_message(call.message.chat.id, "Database is empty.")
            return
        
        text = ""
        for row in rows:
            text += f"ID: {row[0]}\nName: {row[1]}\nAge: {row[2]}\nHobby: {row[3]}\n\n"

        bot.send_message(call.message.chat.id, text)
    

    elif call.data == "search_in_database":
        name_to_search_input = bot.send_message(call.message.chat.id, "Enter name to search: ")
        bot.register_next_step_handler(name_to_search_input, search_friend)
    
    elif call.data == "delete":
        delete_name_input = bot.send_message(call.message.chat.id, "Enter friend name to delete: ")
        bot.register_next_step_handler(delete_name_input, delete_from_database)


def add_to_database(message):
    try:
        name, age, hobby = message.text.split(",")
        database.execute(
            "INSERT INTO friends (name, age, hobby) VALUES (?, ?, ?)",
            (name.strip(), int(age), hobby.strip())
        )
        database.commit()
        bot.send_message(message.chat.id, f'Friend {name.strip()} have been added')

    except Exception as error:
        bot.send_message(message.chat.id, f'Error: {error}')

def search_friend(message):
    name = message.text.strip()
    cursor.execute("SELECT * FROM friends WHERE name = ?", (name,))
    row = cursor.fetchone()

    if row:
        bot.send_message(message.chat.id, f"Found:\nName: {row[1]}\nAge: {row[2]}\nHobby: {row[3]}")

    else:
        bot.send_message(message.chat.id, "User not found.")
    
def delete_from_database(message):
    try:
        name = message.text.strip()
        cursor.execute("SELECT * FROM friends WHERE name = ?", (name,))
        rows = cursor.fetchall()
        if len(rows) == 0:
            bot.send_message(message.chat.id, "User not found.")
            return
            
        cursor.execute("DELETE FROM friends WHERE name = ?", (name,)) 
        database.commit()
        bot.send_message(message.chat.id, f"Deleted {len(rows)} record(s) with name '{name}'.")
    
    except Exception as error:
        bot.send_message(message.chat.id, f'Error: {error}')



bot.polling(True)
