import telebot ### pip install pyTelegramBotAPI ###
from telebot import types
import sqlite3

######################## TELEGRAM API URL #################################
token = '1070073381:AAE1Hu8uysrlKkYhvY3QdkIS6Gh4miU343I'
bot = telebot.TeleBot(token)
########################## @mu3y3y_bot #################################### 


################### TELEGRAM KEYBOARD FUNCTIONS ###########################

@bot.message_handler(commands=['start']) 
def start(message):
    user_name = message.from_user.first_name
    print(user_name)
    print('start')
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(  
		telebot.types.InlineKeyboardButton('Назад', callback_data='back'))
    keyboard.row(
		telebot.types.InlineKeyboardButton('Рестарт', callback_data='restart'))  
    
    bot.send_message(  
        message.from_user.id,   
        'Все данные будут удалены,\nпосле "Рестарта".',  
        reply_markup=keyboard  
    )

@bot.message_handler(commands=['help']) ############ ПЕРЕДЕЛАТЬ!
def help(message):
    user_name = message.from_user.first_name
    print(user_name)
    print('help')
    bot_user_id = message.from_user.id
    bot.send_message(bot_user_id, 'Скоро будет, больше статистики!')
    readdb_for_user(bot_user_id)



################### TELEGRAM CALLBACK FUNCTIONS ###########################
@bot.callback_query_handler(func=lambda call: call.data == 'back')  
def back(query):
    print('back')
    bot_user_id = query.from_user.id
    message_id = query.message.message_id,
    bot.answer_callback_query(query.id)
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row( 
        telebot.types.InlineKeyboardButton('Статистика', callback_data='stats'))
    keyboard.row( 
        telebot.types.InlineKeyboardButton('Я заработал!', callback_data='income'),
        telebot.types.InlineKeyboardButton('Я потратил', callback_data='spent'))
    bot.edit_message_text(chat_id=bot_user_id,
                        message_id=message_id,
                        text='Что бы начать заново нажми\n/start',
                        reply_markup=keyboard)



@bot.callback_query_handler(func=lambda call: call.data == 'restart')  
def restart(query):
    print('restart')
    bot_user_id = query.from_user.id
    bot.answer_callback_query(query.id)
    user_name = query.from_user.first_name
    message_id = query.message.message_id
    print(user_name)
    recording_id(bot_user_id, user_name)
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton('Введи сумму своих сбережений', callback_data='storage'))
    keyboard.row(
        telebot.types.InlineKeyboardButton('У меня нет сбережений', callback_data='zero'))
    keyboard.row(
        telebot.types.InlineKeyboardButton('Введи сумму долга', callback_data='debt'))

    bot.edit_message_text(chat_id=bot_user_id,
                            message_id=message_id,
                            text='Выбери один из вариантов развития.',
                            reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == 'storage' or call.data == 'zero' or call.data == 'debt')  
def open_a_bank_account(query):
    choice = query.data
    message_id = query.message.message_id
    bot_user_id = query.from_user.id

    if choice == 'storage':
        bot_send = bot.edit_message_text(chat_id=bot_user_id,
                            message_id=message_id,
                            text='Введи сумму сбережений.',)
        bot.register_next_step_handler(bot_send, input_bank_value)
    
    elif choice == 'zero':
        bot_send = bot.edit_message_text(chat_id=bot_user_id,
                            message_id=message_id,
                            text='Начни копить!\nВведи то что ты заработал сегодня!')
        bot.register_next_step_handler(bot_send, input_bank_value)

    elif choice == 'debt':
        bot_send = bot.edit_message_text(chat_id=bot_user_id,
                            message_id=message_id,
                            text='Сколько ты задолжал бро?')
        bot.register_next_step_handler(bot_send, input_negativ_namber)


@bot.callback_query_handler(func=lambda call: call.data == 'income')
def income(query):
    bot_user_id = query.from_user.id
    bot.answer_callback_query(query.id)
    message_id = query.message.message_id
    bot_send = bot.edit_message_text(chat_id=bot_user_id,
                            message_id=message_id,
                            text='Сколько ты поднял?')
    bot.register_next_step_handler(bot_send, update_bank_value)




@bot.callback_query_handler(func=lambda call: call.data == 'spent')
def spent(query):
    bot_user_id = query.from_user.id
    bot.answer_callback_query(query.id)
    message_id = query.message.message_id
    bot_send = bot.edit_message_text(chat_id=bot_user_id,
                            message_id=message_id,
                            text='Сколько ты потратил?')
    bot.register_next_step_handler(bot_send, downgrade_bank_value)
################### TELEGRAM CALLBACK FUNCTIONS ###########################


########################## RECORDING DATA BASE ###################################
@bot.message_handler(func=lambda message: True, content_types=['text'])
def filter(message):
    user_name = message.from_user.first_name
    print(user_name)
    print('СПАМ')
    bot.reply_to(message, 'Не знаю что ты хотел этим сказать')
    spent_or_income(message)


def spent_or_income(message):
    bot_user_id = message.from_user.id
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row( 
        telebot.types.InlineKeyboardButton('Статистика', callback_data='stats'))
    keyboard.row( 
        telebot.types.InlineKeyboardButton('Я заработал!', callback_data='income'),
        telebot.types.InlineKeyboardButton('Я потратил', callback_data='spent'))
 
    bot.send_message(
        bot_user_id,
        'Есть какие-то изменения?.',
        reply_markup=keyboard  
    )


def downgrade_bank_value(message):
    bank = message.text
    bot_user_id = message.from_user.id
    user_name = message.from_user.first_name
    print(user_name)
    print('downgrade_bank_value')
    if bank.isdigit() == True:
        dbase = sqlite3.connect('test.db')
        print('dbase opened')
        dbase.execute(''' UPDATE records SET BANK=BANK-? WHERE CHATID=?''',(bank, bot_user_id))
        print('dbase update bank')
        dbase.commit()
        print('dbase commit')
        dbase.close()
        print('dbase close')

        bot.reply_to(message, 'Потрачено!')
        readdb_for_user(bot_user_id)
    else:
        bot_send = bot.send_message(bot_user_id, 'Попробуй ввести целое число.\nНапример вот так: 80')
        bot.register_next_step_handler(bot_send, downgrade_bank_value)


def update_bank_value(message):
    bank = message.text
    bot_user_id = message.from_user.id
    user_name = message.from_user.first_name
    print(user_name)
    print('update_bank_value')
    if bank.isdigit() == True:
        dbase = sqlite3.connect('test.db')
        print('dbase opened')
        dbase.execute(''' UPDATE records SET BANK=BANK+? WHERE CHATID=?''',(bank, bot_user_id))
        print('dbase update bank')
        dbase.commit()
        print('dbase commit')
        dbase.close()
        print('dbase close')

        bot_send = bot.reply_to(message, 'Добавлено!')
        readdb_for_user(bot_user_id)
        bot.register_next_step_handler(bot_send, spent_or_income)
    else:
        bot_send = bot.send_message(bot_user_id, 'Попробуй ввести целое число.\nНапример вот так: 80')
        bot.register_next_step_handler(bot_send, update_bank_value)

def input_negativ_namber(message):
    bank = message.text
    bot_user_id = message.from_user.id
    user_name = message.from_user.first_name
    print(user_name)
    print('input_negativ_namber')
    if bank.isdigit() == True:
        negativ_bank = (int(bank)*-1)
        str_negative_bank = str(negativ_bank)
        recording_bank(bot_user_id, str_negative_bank)
        bot_send = bot.reply_to(message, 'Давай с этим что то делать!')
        bot.register_next_step_handler(bot_send, spent_or_income)
    else:
        bot_send = bot.send_message(bot_user_id, 'Попробуй ввести сумму целыми числами.\nНапример вот так: 80')
        bot.register_next_step_handler(bot_send, input_bank_value)



def input_bank_value(message):
    bank = message.text
    bot_user_id = message.from_user.id
    user_name = message.from_user.first_name
    print(user_name)
    print('input_bank_value')
    if bank.isdigit() == True:
        recording_bank(bot_user_id,bank)
        bot.reply_to(message, 'Сохранил!')
        bot.register_next_step_handler('Можно добавить',spent_or_income)
    else:
        bot_send = bot.send_message(bot_user_id, 'Попробуй ввести сумму целыми числами.\nНапример вот так: 80')
        bot.register_next_step_handler(bot_send, input_bank_value)



def readdb_for_user(bot_user_id):
    dbase = sqlite3.connect('test.db')
    print('dbase opened')
    user_bank = dbase.execute(''' SELECT BANK FROM records WHERE CHATID = ? ''', (bot_user_id,))
    print('dbase read')
    bot.send_message(bot_user_id, 'Сейчас у тебя в запасе:')
    bot.send_message(bot_user_id, user_bank)
    dbase.close()
    print('dbase close')




def recording_id(bot_user_id,user_name):
    dbase = sqlite3.connect('test.db')
    print('dbase opened')
    dbase.execute(''' CREATE TABLE IF NOT EXISTS records(
    CHATID INT PRIMARY KEY NOT NULL,
    NAME TEXT,
    BANK INT) ''')
    print('dbase create tbale if not exist')
    default = '0'
    dbase.execute('''INSERT OR REPLACE INTO records (CHATID, NAME, BANK) VALUES(?,?,?)''',(bot_user_id, user_name, default))
    print('dbase insert id')
    dbase.commit()
    print('dbase commit')
    dbase.close()
    print('dbase close')


def recording_bank(bot_user_id,bank):
    dbase = sqlite3.connect('test.db')
    print('dbase opened')
    dbase.execute(''' UPDATE records SET BANK=? WHERE CHATID=?''',(bank, bot_user_id))
    print('dbase update bank')
    dbase.commit()
    print('dbase commit')
    dbase.close()
    print('dbase close')

############################ TELEGRAM BOT POLLING ######################################
bot.polling(none_stop=True)