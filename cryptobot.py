import logging
log = logging.getLogger('cryptobot')

from pprint import pformat

from telegram.ext import Updater, InlineQueryHandler, CommandHandler
import requests

import config
from coin import get_coin
from errors import ShowUsage, UnknownTicker, RpcError

COMMANDS = ['help', 'start', 'balance', 'deposit', 'withdraw', 'tip', 'admin']
PUBLIC_COMMANDS = ['help', 'tip']
ADMIN_COMMANDS = ['admin']

COMMAND_CONFIG = {
    'help': {
        'usage': '/help',
    },
    'start': {
        'usage': '/start',
    },
    'balance': {
        'usage': '/balance <ticker>',
    },
    'deposit': {
        'usage': '/deposit <ticker>',
    },
    'withdraw': {
        'usage': '/withdraw <amount> <ticker> <address>',
    },
    'tip': {
        'usage': '/tip <@username> <amount> <ticker>',
    },
    'admin': {
        'usage': '\n'.join([
            'Admin commands:',
            '/admin balance <ticker> - show account balances',
        ]),
    },
}


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
        try:
            if result['error']:
                bot.send_message(chat_id, "Error: " + result["error"]["message"])
            else:
                bot.send_message(chat_id, "OK")
        except:
            bot.send_message(chat_id, str(result))

    def command(self, bot, update):
        msg = update.message
        chat_id = msg.chat_id
        cmd = None
        try:
            if not msg.from_user.username:
                raise Exception("You must set a telegram username to use this bot")
            cmd = msg.text.split()[0][1:].split("@")[0]
            if cmd in ADMIN_COMMANDS and msg.from_user.username not in config.ADMINS:
                return
            if msg.chat.type != 'private' and cmd not in PUBLIC_COMMANDS:
                raise Exception(msg.from_user.username + ", that command is only available if you talk to me privately")
            f = getattr(self, 'cmd_' + cmd, None)
            if f:
                f(bot, update)
        except ShowUsage as e:
            s = str(e) if str(e) else "Usage: "
            if cmd and cmd in COMMAND_CONFIG:
                bot.send_message(chat_id, s + COMMAND_CONFIG[cmd]['usage'])
        except UnknownTicker as e:
            bot.send_message(chat_id, f"Unknown coin: {e}")
        except RpcError as e:
            bot.send_message(chat_id, f'RpcError: {e}')
        except Exception as e:
            log.exception('command')
            bot.send_message(chat_id, f'Error: {e}')

    def _parse_sym_coin(self, msg, idx):
        sym = None
        try:
            sym = msg.text.split()[idx].upper()
        except:
            raise ShowUsage()
        return sym, get_coin(sym)

    def _parse_amount(self, msg, idx):
        parts = msg.text.split()
        if idx >= len(parts):
            raise ShowUsage()
        amount = parts[idx]
        try:
            return int(amount)
        except:
            raise Exception(f'Invalid amount: {amount}')

    def _parse_addr(self, msg, idx):
        try:
            return msg.text.split()[idx]
        except:
            raise ShowUsage()

    def _parse_str(self, msg, idx):
        try:
            return msg.text.split()[idx]
        except:
            raise ShowUsage()

    def cmd_help(self, bot, update):
        return self.cmd_start(bot, update)

    def cmd_start(self, bot, update):
        chat_id = update.message.chat_id
        bot.send_message(chat_id, config.BOT_START_MESSAGE)

    def cmd_balance(self, bot, update):
        msg = update.message
        username = msg.from_user.username
        sym, coin = self._parse_sym_coin(msg, 1)
        amount = int(coin.request('getbalance', [username, config.MINCONF])['result'])
        bot.send_message(msg.chat_id, f"You have {amount} {sym}")

    def get_addr(self, coin, username):
        result = coin.request('getaddressesbyaccount', [username])
        if result["result"]:
            return result["result"][0]
        result = coin.request('getnewaddress', [username])
        return result["result"]

    def cmd_deposit(self, bot, update):
        msg = update.message
        username = msg.from_user.username
        sym, coin = self._parse_sym_coin(msg, 1)
        addr = self.get_addr(coin, username)
        bot.send_message(msg.chat_id, f"Deposit {sym} to {addr}")

    def cmd_withdraw(self, bot, update):
        msg = update.message
        username = msg.from_user.username
        amount = self._parse_amount(msg, 1)
        sym, coin = self._parse_sym_coin(msg, 2)
        toaddr = self._parse_addr(msg, 3)
        balance = int(coin.request('getbalance', [username, config.MINCONF])['result'])
        if amount > balance:
            raise Exception(f"You only have {balance} {sym}.")
        result = coin.request('sendfrom', [username, toaddr, amount, config.MINCONF])
        bot.send_message(msg.chat_id, f"Sent {amount} {sym} to {toaddr}.")

    def cmd_tip(self, bot, update):
        msg = update.message
        parts = msg.text.split()
        if len(parts) < 4:
            raise ShowUsage("How to properly tip:\n")
        amount = self._parse_amount(msg, -2)
        sym, coin = self._parse_sym_coin(msg, -1)
        username = msg.from_user.username
        recipients = []
        for e, val in msg.parse_entities().items():
            if e.type == 'mention':
                recipients.append(val[1:])
        if not recipients:
            raise ShowUsage()
        if amount * len(recipients) > coin.request('getbalance', [username, config.MINCONF])['result']:
            raise Exception(f"Not enough {sym} coins in your account")
        for recipient in recipients:
            toaddr = self.get_addr(coin, recipient)
            result = coin.request('sendfrom', [username, toaddr, amount, config.MINCONF])
            bot.send_message(msg.chat_id, f"Congratulations @{recipient}, you have been tipped {amount} {sym} by @{username}")

    def cmd_admin(self, bot, update):
        msg = update.message
        cmd = self._parse_str(msg, 1)
        f = getattr(self, 'adm_' + cmd, None)
        if f:
            f(bot, update)

    def adm_balance(self, bot, update):
        msg = update.message
        sym, coin = self._parse_sym_coin(msg, -1)
        result = coin.request('listaccounts', [config.MINCONF])
        bot.send_message(msg.chat_id, pformat(result))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('telegram.bot').setLevel(logging.INFO)
    cb = Cryptobot()
    cb.loop()
