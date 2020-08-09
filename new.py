import telebot ### pip install pyTelegramBotAPI ### pyTelegramBotAPI==3.7.1, PY v 3.8
from telebot import types
import sqlite3

######################## TELEGRAM API URL #################################
token = '1070073381:AAE1Hu8uysrlKkYhvY3QdkIS6Gh4miU343I'
bot = telebot.TeleBot(token)
########################## @mu3y3y_bot ####################################

bot_dict = {
    'hello': 'Hello ',
    'back': 'Back',
}


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


    def start(self):
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
                    WHERE CHATID=?''',
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

    # def start(self):
    #     keyboard = telebot.types.InlineKeyboardMarkup()
    #     keyboard.row(telebot.types.InlineKeyboardButton('Введи сумму своих сбережений', callback_data='storage'))
    #     keyboard.row(telebot.types.InlineKeyboardButton('У меня нет сбережений', callback_data='back'))
    #     keyboard.row(telebot.types.InlineKeyboardButton('Введи сумму долга', callback_data='debt'))
        # return keyboard


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



def spent_or_income(user_id, user_name, message_id):
    
    keyboard = InLineKeyBoard().spent_or_income()


    bot.delete_message(chat_id=user_id, message_id=message_id-1)
    bot.delete_message(chat_id=user_id, message_id=message_id)
    bot.send_message(chat_id=user_id,
                    text='spent or income',
                    reply_markup=keyboard)



@bot.callback_query_handler(func=lambda call: call.data == 'restart')
@bot.message_handler(commands=['start']) 
def start(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    try:
        message_id = message.message_id
    except:
        message_id = message.message.message_id

    db = DataBase(user_id=user_id, user_name=user_name, user_bank='0')
    db.create()
    db.start()
    spent_or_income(user_id, user_name, message_id)


# @bot.callback_query_handler(func=lambda call: call.data == 'restart')
# def restart(query):
#     user_id = query.from_user.id
#     user_name = query.from_user.first_name
#     message_id = query.message.message_id
#     db = DataBase(user_id=user_id, user_name=user_name, user_bank='0')
#     db.start()
#     spent_or_income(user_id, user_name, message_id)


@bot.callback_query_handler(func=lambda call: call.data == 'storage' or call.data == 'zero' or call.data == 'debt')  
def open_a_bank_account(query):
    choice = query.data
    message_id = query.message.message_id
    user_id = query.from_user.id

    if choice == 'storage':
        bot_send = bot.edit_message_text(chat_id=user_id,
                            message_id=message_id,
                            text='Введи сумму сбережений.',)
        bot.register_next_step_handler(bot_send, update_bank)
    
    elif choice == 'zero':
        bot_send = bot.edit_message_text(chat_id=user_id,
                            message_id=message_id,
                            text='Начни копить!\nВведи то что ты заработал сегодня!')

    elif choice == 'debt':
        bot_send = bot.edit_message_text(chat_id=user_id,
                            message_id=message_id,
                            text='Сколько ты задолжал бро?')
        bot.register_next_step_handler(bot_send, downgrade_bank)


@bot.callback_query_handler(func=lambda call: call.data == 'spent' or call.data == 'income')
def spent_or_income_2(query):
    choice = query.data
    user_id = query.from_user.id
    message_id = query.message.message_id
    if choice == 'spent':

        bot.delete_message(chat_id=user_id, message_id=message_id)
        bot_send = bot.send_message(chat_id=user_id, text='Сколько ты потратил?')
        bot.register_next_step_handler(bot_send, downgrade_bank)
    else:

        bot.delete_message(chat_id=user_id, message_id=message_id)
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
                    text= f'Такие дела, {user_bank}.',
                    reply_markup=keyboard)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def filter(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    message_id = message.message_id
    keyboard = InLineKeyBoard().spent_or_income()

    bot.delete_message(chat_id=user_id, message_id=message_id-1)
    bot.delete_message(chat_id=user_id, message_id=message_id)
    bot.send_message(chat_id=user_id,
                    text=f'Привет, {user_name}!',
                    reply_markup=keyboard)


def update_bank(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    message_id = message.message_id
    user_bank = message.text
    keyboard = InLineKeyBoard().spent_or_income()

    if user_bank.isdigit() == True: 
        DataBase(user_id=user_id, user_name=user_name, user_bank=user_bank)


        bot.delete_message(chat_id=user_id, message_id=message_id-1)
        bot.delete_message(chat_id=user_id, message_id=message_id)
        bot.reply_to(message, 'Записал!')   
        bot.send_message(chat_id=user_id,
                         text='Главное меню:',
                         reply_markup=keyboard)

    else:
        bot_send = bot.send_message(user_id, f'{user_name} введи сумму целыми числами.\nНапример вот так: 80')
        bot.register_next_step_handler(bot_send, update_bank)


def downgrade_bank(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    message_id = message.message_id
    user_bank = message.text
    keyboard = InLineKeyBoard().spent_or_income()
    
    if user_bank.isdigit() == True:
        DataBase(user_id=user_id, user_name=user_name, user_bank=user_bank).downgrade_bank()

        bot.delete_message(chat_id=user_id, message_id=message_id-1)
        bot.delete_message(chat_id=user_id, message_id=message_id)
        bot.send_message(chat_id=user_id,
                         text='Главное меню:',
                         reply_markup=keyboard)
    else:
        bot_send = bot.send_message(user_id, f'{user_name} введи сумму целыми числами.\nНапример вот так: 80')
        bot.register_next_step_handler(bot_send, downgrade_bank)



############################ TELEGRAM BOT POLLING ######################################
bot.polling(none_stop=True)