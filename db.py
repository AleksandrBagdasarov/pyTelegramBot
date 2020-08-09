import telebot ### pip install pyTelegramBotAPI ### pyTelegramBotAPI==3.7.1, PY v 3.8
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
    bot_user_id = message.from_user.id
    dbase = sqlite3.connect('test.db')
    dbase.execute(''' CREATE TABLE IF NOT EXISTS records(
    CHATID INT PRIMARY KEY NOT NULL,
    NAME TEXT,
    BANK INT) ''')
    dbase.commit()
    dbase.close()
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(  
		telebot.types.InlineKeyboardButton('Назад', callback_data='back'))
    keyboard.row(
		telebot.types.InlineKeyboardButton('Начать с начала', callback_data='restart'))  
    
    pic = open('pic.jpg', 'rb')
    bot.send_photo(chat_id=bot_user_id, photo=pic)
    bot.send_message(chat_id=bot_user_id, text=f'Привет,{user_name}!', reply_markup=keyboard)







@bot.callback_query_handler(func=lambda call: call.data == 'back')  
def back(query):
    print('back')
    bot_user_id = query.from_user.id
    message_id = query.message.message_id,
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row( 
        telebot.types.InlineKeyboardButton('Статистика', callback_data='stats'))
    keyboard.row( 
        telebot.types.InlineKeyboardButton('Я заработал!', callback_data='income'),
        telebot.types.InlineKeyboardButton('Я потратил', callback_data='spent'))

    bot.delete_message(chat_id=bot_user_id,
                        message_id=message_id,)
    pic = open('pic.jpg', 'rb')
    bot.send_photo(chat_id=bot_user_id, photo=pic)
    bot.send_message(chat_id=bot_user_id,
                        text='Главное меню:',
                        reply_markup=keyboard)






@bot.callback_query_handler(func=lambda call: call.data == 'restart')
def restart(query):
    bot_user_id = query.from_user.id
    user_name = query.from_user.first_name
    default_bank = '0'
    message_id = query.message.message_id
    
    dbase = sqlite3.connect('test.db')
    
    dbase.execute(''' CREATE TABLE IF NOT EXISTS records(
    CHATID INT PRIMARY KEY NOT NULL,
    NAME TEXT,
    BANK INT) ''')
    dbase.execute('''INSERT OR REPLACE INTO records (CHATID, NAME, BANK) VALUES(?,?,?)''',(bot_user_id, user_name, default_bank))
    dbase.commit()
    
    dbase.close()
    

    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton('Введи сумму своих сбережений', callback_data='storage'))
    keyboard.row(
        telebot.types.InlineKeyboardButton('У меня нет сбережений', callback_data='back'))
    keyboard.row(
        telebot.types.InlineKeyboardButton('Введи сумму долга', callback_data='debt'))

    bot.delete_message(chat_id=bot_user_id,
                        message_id=message_id)
    pic = open('pic_open_a_bank_account.jpg', 'rb')
    bot.send_photo(chat_id=bot_user_id, photo=pic)

    bot.send_message(chat_id=bot_user_id,
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

    elif choice == 'debt':
        bot_send = bot.edit_message_text(chat_id=bot_user_id,
                            message_id=message_id,
                            text='Сколько ты задолжал бро?')
        bot.register_next_step_handler(bot_send, input_negativ_bank_value)






@bot.callback_query_handler(func=lambda call: call.data == 'spent' or call.data == 'income')
def spent_or_income_2(query):
    choice = query.data
    bot_user_id = query.from_user.id
    message_id = query.message.message_id
    if choice == 'spent':

        bot.delete_message(chat_id=bot_user_id,
                        message_id=message_id)
        pic = open('pic_downgrade.jpg', 'rb')
        bot.send_photo(chat_id=bot_user_id, photo=pic)
        bot_send = bot.send_message(chat_id=bot_user_id, text='Сколько ты потратил?')
        bot.register_next_step_handler(bot_send, downgrade_bank_value)
    else:

        bot.delete_message(chat_id=bot_user_id,
                        message_id=message_id)
        pic = open('pic_income_2.jpg', 'rb')
        bot.send_photo(chat_id=bot_user_id, photo=pic)
        bot_send = bot.send_message(chat_id=bot_user_id, text='Сколько ты заработал?')
        bot.register_next_step_handler(bot_send, update_bank_value)







@bot.callback_query_handler(func=lambda call: call.data == 'stats')  
def stats(query):
    bot_user_id = query.from_user.id
    user_name = query.from_user.first_name
    message_id = query.message.message_id
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row( 
        telebot.types.InlineKeyboardButton('Главное меню', callback_data='back'))

    dbase = sqlite3.connect('test.db')
    dbase.execute(''' CREATE TABLE IF NOT EXISTS records(
    CHATID INT PRIMARY KEY NOT NULL,
    NAME TEXT,
    BANK INT) ''')
    user_bank = dbase.execute(''' SELECT BANK FROM records WHERE CHATID = ?''', (bot_user_id,))
    bot.delete_message(chat_id=bot_user_id,
                        message_id=message_id)
    pic = open('pic_stats.jpg', 'rb')
    bot.send_photo(chat_id=bot_user_id, photo=pic)
    bot.send_message(bot_user_id, user_bank)
    bot.send_message(chat_id=bot_user_id,
                        text=f'Такие дела, {user_name}.',
                        reply_markup=keyboard)
    dbase.close()









@bot.message_handler(func=lambda message: True, content_types=['text'])
def filter(message):
    bot_user_id = message.from_user.id
    user_name = message.from_user.first_name
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row( 
            telebot.types.InlineKeyboardButton('Главное меню', callback_data='back'))
    bot.send_message(chat_id=bot_user_id,
                         text=f'Привет, {user_name}!',
                         reply_markup=keyboard)


def input_bank_value(message):
    bank = message.text
    bot_user_id = message.from_user.id
    user_name = message.from_user.first_name
    if bank.isdigit() == True:
        dbase = sqlite3.connect('test.db')
        dbase.execute(''' UPDATE records SET BANK=? WHERE CHATID=?''',(bank, bot_user_id))
        dbase.commit()  
        
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row( 
            telebot.types.InlineKeyboardButton('Статистика', callback_data='stats'))
        keyboard.row( 
            telebot.types.InlineKeyboardButton('Я заработал!', callback_data='income'),
            telebot.types.InlineKeyboardButton('Я потратил', callback_data='spent'))

        
        dbase.close()
        pic = open('pic_open_a_bank_account.jpg', 'rb')
        bot.send_photo(chat_id=bot_user_id, photo=pic)
        bot.reply_to(message, 'Записал!')   
        bot.send_message(chat_id=bot_user_id,
                         text='Главное меню:',
                         reply_markup=keyboard)

    else:
        bot_send = bot.send_message(bot_user_id, f'{user_name} введи сумму целыми числами.\nНапример вот так: 80')
        bot.register_next_step_handler(bot_send, input_bank_value)


def input_negativ_bank_value(message):
    bank = message.text
    bot_user_id = message.from_user.id
    user_name = message.from_user.first_name
    print(user_name)
    print('input_negativ_bank_value')
    if bank.isdigit() == True:
        #negativ_bank = (int(bank)*-1)
        #str_negative_bank = str(negativ_bank)
        dbase = sqlite3.connect('test.db')
        print('dbase opened')
        dbase.execute(''' UPDATE records SET BANK=BANK-? WHERE CHATID=?''',(bank, bot_user_id))
        print('dbase update bank')
        dbase.commit()
        print('dbase commit')
        #user_bank = dbase.execute(''' SELECT BANK FROM records WHERE CHATID = ?''', (bot_user_id,))
        print('dbase read')  
        
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row( 
            telebot.types.InlineKeyboardButton('Статистика', callback_data='stats'))
        keyboard.row( 
            telebot.types.InlineKeyboardButton('Я заработал!', callback_data='income'),
            telebot.types.InlineKeyboardButton('Я потратил', callback_data='spent'))
        #bot.send_message(bot_user_id, user_bank)
        dbase.close()
        print('dbase close')
        pic = open('pic_debt.png', 'rb')
        bot.send_photo(chat_id=bot_user_id, photo=pic)
        bot.reply_to(message, 'Разберемся!')
        bot.send_message(chat_id=bot_user_id,
                         text='Главное меню:',
                         reply_markup=keyboard)
    else:
        bot_send = bot.send_message(bot_user_id, f'{user_name} введи сумму целыми числами.\nНапример вот так: 80')
        bot.register_next_step_handler(bot_send, input_negativ_bank_value)







def downgrade_bank_value(message):
    bank = message.text
    bot_user_id = message.from_user.id
    user_name = message.from_user.first_name
    print(user_name)
    print('downgrade_bank_value')
    if bank.isdigit() == True:
        dbase = sqlite3.connect('test.db')
        print('dbase opened')
        
        dbase.execute(''' CREATE TABLE IF NOT EXISTS records(
        CHATID INT PRIMARY KEY NOT NULL,
        NAME TEXT,
        BANK INT) ''')
        dbase.execute(''' UPDATE records SET BANK=BANK-? WHERE CHATID=?''',(bank, bot_user_id))
        print('dbase update bank')
        dbase.commit()
        print('dbase commit')
        dbase.close()
        print('dbase close')

        
        
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row( 
            telebot.types.InlineKeyboardButton('Статистика', callback_data='stats'))
        keyboard.row( 
            telebot.types.InlineKeyboardButton('Я заработал!', callback_data='income'),
            telebot.types.InlineKeyboardButton('Я потратил', callback_data='spent'))
        
        #bot.send_message(bot_user_id, user_bank)
        
        pic = open('pic_stats.jpg', 'rb')
        bot.send_photo(chat_id=bot_user_id, photo=pic)
        bot_send = bot.reply_to(message, 'Потрачено!')
        bot.send_message(chat_id=bot_user_id,
                         text='Главное меню:',
                         reply_markup=keyboard)
    else:
        bot_send = bot.send_message(bot_user_id, f'{user_name} введи целое число.\nНапример вот так: 80')
        bot.register_next_step_handler(bot_send, downgrade_bank_value)


def update_bank_value(message):
    bank = message.text
    bot_user_id = message.from_user.id
    user_name = message.from_user.first_name
    if bank.isdigit() == True:
        dbase = sqlite3.connect('test.db')
        
        dbase.execute(''' CREATE TABLE IF NOT EXISTS records(
        CHATID INT PRIMARY KEY NOT NULL,
        NAME TEXT,
        BANK INT) ''')
        dbase.execute(''' UPDATE records SET BANK=BANK+? WHERE CHATID=?''',(bank, bot_user_id))
        dbase.commit()
        dbase.close()
        
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row( 
            telebot.types.InlineKeyboardButton('Статистика', callback_data='stats'))
        keyboard.row( 
            telebot.types.InlineKeyboardButton('Я заработал!', callback_data='income'),
            telebot.types.InlineKeyboardButton('Я потратил', callback_data='spent'))
        #bot.send_message(bot_user_id, user_bank)
        pic = open('pic_stats.jpg', 'rb')
        bot.send_photo(chat_id=bot_user_id, photo=pic)
        bot_send = bot.reply_to(message, 'Добавлено!')

        ######
        bot.send_message(chat_id=bot_user_id,
                         text='Главное меню:',
                         reply_markup=keyboard)
    else:
        bot_send = bot.send_message(bot_user_id, f'{user_name}Попробуй ввести целое число.\nНапример вот так: 80')
        bot.register_next_step_handler(bot_send, update_bank_value)












############################ TELEGRAM BOT POLLING ######################################
bot.polling(none_stop=True)