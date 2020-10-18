import logging
log = logging.getLogger('captcha')

import time, threading

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

import config


PENDING = {}

def get_name(user):
    if user.username:
        return '@' + user.username
    return user.first_name

def start_thread():
    def thread_f():
        bot = Bot(config.TELEGRAM_TOKEN)
        while True:
            for (chat_id, user_id), (t, user) in list(PENDING.items()):
                if time.time() > t:
                    bot.send_message(chat_id, "Bye bye, " + get_name(user))
                    try:
                        del PENDING[(chat_id, user_id)]
                        bot.kickChatMember(chat_id, user_id)
                        bot.unbanChatMember(chat_id, user_id)
                    except:
                        log.exception('failed to kick ' + get_name(user))
            time.sleep(1)
    thread = threading.Thread(target=thread_f)
    thread.start()

class CaptchaMixin:
    def cmd_captcha(self, bot, update):
        msg = update.message
        if msg.chat.username not in config.CAPTCHA_GROUPS:
            return
        user_id = int(msg.text.split()[1])
        if user_id != msg.from_user.id:
            bot.send_message(msg.chat_id, get_name(msg.from_user) + " pressed the happy button -_-")
            return
        
        try:
            del PENDING[(msg.chat_id, user_id)]
            bot.send_message(msg.chat_id, get_name(msg.from_user) + " pressed the happy button! Welcome to the group.")
        except:
            log.exception('cmd_captcha')

    def new_chat_members_event(self, bot, update):
        msg = update.message
        if msg.chat.username not in config.CAPTCHA_GROUPS:
            return
        for user in msg.new_chat_members:
            if msg.from_user.id != user.id:
                continue
            bot.send_message(msg.chat_id, "Hello, " + get_name(user))
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Happy human button", callback_data='/captcha ' + str(user.id))]])
            msg.reply_text("Click here to verify you are not a bot:", reply_markup=keyboard)
            PENDING[(msg.chat_id, user.id)] = (time.time() + config.CAPTCHA_SECONDS, user)
        
