import telebot
from telebot import types
import sqlite3

######################## TELEGRAM API URL #################################
token = '1070073381:AAE1Hu8uysrlKkYhvY3QdkIS6Gh4miU343I'
bot = telebot.TeleBot(token)
########################## @mu3y3y_bot ####################################


class DataBase:

    def __init__(self, user_id, user_name, user_bank):
        self.user_id = user_id
        self.user_name = user_name
        self.user_bank = user_bank


    def create(self):
        dbase = sqlite3.connect('new.db')
        dbase.execute(''' CREATE TABLE IF NOT EXISTS records(
        ID INT PRIMARY KEY NOT NULL,
        NAME TEXT,
        BANK INT) ''')
        dbase.commit()
        dbase.execute('''INSERT OR IGNORE INTO records (ID, NAME, BANK) VALUES(?,?,?)''', (self.user_id, self.user_name, self.user_bank))
        dbase.close()


    def restart(self):
        dbase = sqlite3.connect('new.db')
        dbase.execute('''INSERT OR REPLACE INTO records 
        (ID, NAME, BANK) VALUES(?,?,?)''',
        (self.user_id, self.user_name, self.user_bank))
        dbase.commit()
        dbase.close()


    def get_bank(self):
        dbase = sqlite3.connect('new.db')
        return tuple(dbase.execute(''' SELECT BANK FROM records 
                            WHERE ID = ?''',
                            (self.user_id,)))[0][0]


    def update_bank(self):
        dbase = sqlite3.connect('new.db')
        dbase.execute(''' UPDATE records SET BANK=BANK+? 
                    WHERE ID=?''',
                    (self.user_bank, self.user_id))
        dbase.commit()
        dbase.close()


    def downgrade_bank(self):
        dbase = sqlite3.connect('new.db')
        dbase.execute(''' UPDATE records SET BANK=BANK-? 
                        WHERE ID=?''',
                        (self.user_bank, self.user_id))
        dbase.commit()
        dbase.close()
        

class InLineKeyBoard:

    def spent_or_income(self):
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(telebot.types.InlineKeyboardButton('Статистика', callback_data='stats'))
        keyboard.row(telebot.types.InlineKeyboardButton('Я заработал!', callback_data='income'),
                    telebot.types.InlineKeyboardButton('Я потратил', callback_data='spent'))
        return keyboard


    def home(self):
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(telebot.types.InlineKeyboardButton('Главное меню', callback_data='back'))
        keyboard.row(telebot.types.InlineKeyboardButton('Начать с начала', callback_data='restart'))
        return keyboard


@bot.callback_query_handler(func=lambda call: call.data == 'back')
def spent_or_income(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    user_bank = DataBase(user_id=user_id, user_name=user_name, user_bank=None).get_bank()
    try:
        message_id = message.message_id
    except:
        message_id = message.message.message_id   
    keyboard = InLineKeyBoard().spent_or_income()

    bot.delete_message(chat_id=user_id, message_id=message_id-1)
    bot.delete_message(chat_id=user_id, message_id=message_id)
    bot.send_message(chat_id=user_id,
                    text=f'На твоём счету : {user_bank}',
                    reply_markup=keyboard)


@bot.message_handler(func=lambda message: True, content_types=['text'])
@bot.callback_query_handler(func=lambda call: call.data == 'restart')
def start(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    db = DataBase(user_id=user_id, user_name=user_name, user_bank='0')
    db.create()
    try:
        if message.data == 'restart':
            db.restart()
    except AttributeError:
        pass
    spent_or_income(message)


@bot.callback_query_handler(func=lambda call: call.data == 'spent' or call.data == 'income')
def spent_or_income_2(query):
    choice = query.data
    user_id = query.from_user.id
    message_id = query.message.message_id
    bot.delete_message(chat_id=user_id, message_id=message_id)
    if choice == 'spent':        
        bot_send = bot.send_message(chat_id=user_id, text='Сколько ты потратил?')
        bot.register_next_step_handler(bot_send, downgrade_bank)
    else:
        bot_send = bot.send_message(chat_id=user_id, text='Сколько ты заработал?')
        bot.register_next_step_handler(bot_send, update_bank)


@bot.callback_query_handler(func=lambda call: call.data == 'stats')  
def stats(query):
    user_id = query.from_user.id
    user_name = query.from_user.first_name
    message_id = query.message.message_id
    user_bank = DataBase(user_id=user_id, user_name=user_name, user_bank=None).get_bank()
    keyboard = InLineKeyBoard().home()

    bot.delete_message(chat_id=user_id, message_id=message_id)
    bot.send_message(chat_id=user_id,
                    text= f'На твоем счету: {user_bank}.',
                    reply_markup=keyboard)


def update_bank(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    message_id = message.message_id
    user_bank = message.text

    if user_bank.isdigit() == True: 
        DataBase(user_id=user_id, user_name=user_name, user_bank=user_bank).update_bank()

        spent_or_income(message)
    else:
        bot.delete_message(chat_id=user_id, message_id=message_id-1)
        bot.delete_message(chat_id=user_id, message_id=message_id)
        bot_send = bot.send_message(user_id, f'{user_name} введи сумму целыми числами.\nНапример вот так: 80')
        bot.register_next_step_handler(bot_send, update_bank)


def downgrade_bank(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    message_id = message.message_id
    user_bank = message.text
    
    if user_bank.isdigit() == True:
        DataBase(user_id=user_id, user_name=user_name, user_bank=user_bank).downgrade_bank()

        spent_or_income(message)
    else:
        bot.delete_message(chat_id=user_id, message_id=message_id-1)
        bot.delete_message(chat_id=user_id, message_id=message_id)
        bot_send = bot.send_message(user_id, f'{user_name} введи сумму целыми числами.\nНапример вот так: 80')
        bot.register_next_step_handler(bot_send, downgrade_bank)



############################ TELEGRAM BOT POLLING ######################################
bot.polling(none_stop=True)