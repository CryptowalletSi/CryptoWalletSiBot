import logging
log = logging.getLogger('cryptobot')

from telegram.ext import Updater, InlineQueryHandler, CommandHandler
import requests

import config
from coin import COINS


COMMANDS = ['start', 'balance', 'deposit', 'withdraw', 'tip']


class Cryptobot:
    def __init__(self, telegram_token=config.TELEGRAM_TOKEN):
        self.telegram_token = telegram_token
        self.updater = Updater(self.telegram_token)
        for cmd in COMMANDS:
            self.updater.dispatcher.add_handler(CommandHandler(cmd, self.command))

    def loop(self):
        self.updater.start_polling()
        self.updater.idle()
    
    def send_result(self, bot, update, result):
        chat_id = update.message.chat_id
        bot.send_message(chat_id, str(result))

    def command(self, bot, update):
        chat_id = update.message.chat_id
        try:
            if not update.message.from_user.username:
                raise Exception("You must set a telegram username to use this bot")
            cmd = update.message.text.split()[0][1:]
            f = getattr(self, 'cmd_' + cmd, None)
            if f:
                f(bot, update)
        except Exception as e:
            log.exception('command')
            bot.send_message(chat_id, f'Error: {e}')

    def cmd_start(self, bot, update):
        chat_id = update.message.chat_id
        bot.send_message(chat_id, config.BOT_START_MESSAGE)

    def cmd_balance(self, bot, update):
        msg = update.message
        username = msg.from_user.username
        sym = msg.text.split()[1].upper()
        coin = COINS[sym]
        result = coin.request('listaccounts', [config.MINCONF])
        self.send_result(bot, update, result)

    def get_addr(self, coin, username):
        result = coin.request('getaddressesbyaccount', [username])
        if result["result"]:
            return result["result"][0]
        result = coin.request('getnewaddress', [username])
        return result["result"]

    def cmd_deposit(self, bot, update):
        msg = update.message
        username = msg.from_user.username
        sym = msg.text.split()[1].upper()
        coin = COINS[sym]
        addr = self.get_addr(coin, username)
        bot.send_message(msg.chat_id, f"Deposit {sym} to {addr}")

    def cmd_withdraw(self, bot, update):
        msg = update.message
        username = msg.from_user.username
        sym = msg.text.split()[1].upper()
        coin = COINS[sym]
        toaddr = msg.text.split()[2]
        amount = coin.request('getbalance', [username, config.MINCONF])['result']
        result = coin.request('sendfrom', [username, toaddr, amount, config.MINCONF])
        self.send_result(bot, update, result)

    def cmd_tip(self, bot, update):
        msg = update.message
        username = msg.from_user.username
        if msg.entities[1].type != 'mention':
            raise Exception("First param must be recipient username")
        recipient = msg.text.split()[1][1:]
        amount = float(msg.text.split()[2])
        sym = msg.text.split()[3].upper()
        coin = COINS[sym]
        if amount > coin.request('getbalance', [username, config.MINCONF])['result']:
            raise Exception(f"Not enough {sym} coins in your account")
        toaddr = self.get_addr(coin, recipient)
        result = coin.request('sendfrom', [username, toaddr, amount, config.MINCONF])
        self.send_result(bot, update, result)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('telegram.bot').setLevel(logging.INFO)
    cb = Cryptobot()
    cb.loop()
