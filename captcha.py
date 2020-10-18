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

def get_msg(key, group, d={}):
    try:
        msg = config.CAPTCHA_MESSAGES[group][key]
    except:
        msg = config.CAPTCHA_MESSAGES[None][key]
    msg = msg.format(**d)
    return msg

def start_thread():
    def thread_f():
        bot = Bot(config.TELEGRAM_TOKEN)
        while True:
            for (chat_id, user_id), d in list(PENDING.items()):
                if time.time() > d['time']:
                    try:
                        del PENDING[(chat_id, user_id)]
                        bot.kickChatMember(chat_id, user_id)
                        bot.unbanChatMember(chat_id, user_id)
                        kick_msg = get_msg('user_kicked', d['group'].username, {'name': get_name(d['user'])})
                        if kick_msg:
                            bot.send_message(chat_id, kick_msg)
                        bot.delete_message(chat_id=d['group'].id, message_id=d['captcha_msg'].message_id)
                    except:
                        log.exception('failed to kick ' + get_name(d['user']))
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
            return 
        try:
            bot.send_message(msg.chat_id, get_msg('user_verified', msg.chat.username, {'name': get_name(msg.from_user)}))
            bot.delete_message(chat_id=msg.chat_id, message_id=PENDING[(msg.chat_id, user_id)]['captcha_msg'].message_id)
        except:
            log.exception('cmd_captcha')
        del PENDING[(msg.chat_id, user_id)]
    
    def new_chat_members_event(self, bot, update):
        msg = update.message
        if msg.chat.username not in config.CAPTCHA_GROUPS:
            return
        for user in msg.new_chat_members:
            if msg.from_user.id != user.id:
                continue
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(get_msg('button', msg.chat.username), callback_data='/captcha ' + str(user.id))]])
            captcha_msg = msg.reply_text(get_msg('new_user', msg.chat.username, {'name': get_name(user), 'secs': config.CAPTCHA_SECONDS}), reply_markup=keyboard)
            PENDING[(msg.chat_id, user.id)] = {
                'time': time.time() + config.CAPTCHA_SECONDS,
                'group': msg.chat,
                'user': user,
                'captcha_msg': captcha_msg,
            }
        
