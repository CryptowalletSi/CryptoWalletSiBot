import logging
log = logging.getLogger('cryptobot')

import time
from pprint import pformat

from telegram.ext import Updater, Filters, InlineQueryHandler, CommandHandler, CallbackQueryHandler, MessageHandler
from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ParseMode

import requests

import config
from coin import get_coin
from errors import ShowUsage, UnknownTicker, RpcError
from util import round_price
import captcha

from config import COMMANDS, PUBLIC_COMMANDS, ADMIN_COMMANDS, ANON_COMMANDS

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
    'p': {
        'usage': '/p <ticker>',
    },
    'admin': {
        'usage': '\n'.join([
            'Admin commands:',
            '/admin balance <ticker> - show account balances',
        ]),
    },
}

TIP_DECIMAL_PLACES = 4

COMMAND_THROTTLE_USERS = {}


class Cryptobot(captcha.CaptchaMixin):
    def __init__(self, telegram_token=config.TELEGRAM_TOKEN):
        self.telegram_token = telegram_token
        self.updater = Updater(self.telegram_token)
        for cmd in COMMANDS:
            self.updater.dispatcher.add_handler(CommandHandler(cmd, self.command))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.command))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, self.new_chat_members_event))
    
    def loop(self):
        captcha.start_thread()
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
        if update.callback_query:
            update.message = update.callback_query.message
            update.message.text = update.callback_query.data
            update.message.from_user = update.callback_query.from_user
        msg = update.message
        chat_id = msg.chat_id
        cmd = None
        try:
            cmd = msg.text.split()[0][1:].split("@")[0]
            username = msg.from_user.username

            if cmd not in ANON_COMMANDS and not username:
                raise Exception("You must set a telegram username to use this bot")
            
            t = COMMAND_THROTTLE_USERS.get(username, 0)
            if time.time() < t:
                raise Exception(username + ', I need some time to relax. Wait ' + str(int(t - time.time()) + 1) + ' secs.')
            COMMAND_THROTTLE_USERS[username] = time.time() + config.COMMAND_THROTTLE_SECONDS

            if cmd in ADMIN_COMMANDS and msg.from_user.username not in config.ADMINS:
                return
            
            if msg.chat.type != 'private' and cmd not in PUBLIC_COMMANDS:
                raise Exception(username + ", that command is only available if you talk to me privately")
            
            group_cfg = config.GROUP_CONFIG.get(msg.chat.username)
            if group_cfg:
                if cmd in group_cfg.get('command_blacklist', []):
                    raise Exception(username + ", that command is currently disabled in this group")

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
        amount = None
        try:
            amount = parts[idx]
        except IndexError:
            raise ShowUsage()
        try:
            return self._format_amount(amount)
        except:
            raise Exception(f'Invalid amount: {amount}')

    def _format_amount(self, amount):
        return round(float(amount) * (10**TIP_DECIMAL_PLACES)) / (10**TIP_DECIMAL_PLACES)

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
        msg = update.message
        #chat_id = update.message.chat_id
        #bot.send_message(chat_id, config.BOT_START_MESSAGE)
        keyboard = ReplyKeyboardMarkup([[InlineKeyboardButton('/' + cmd, callback_data='/' + cmd) for cmd in ('balance', 'deposit', 'withdraw')]])
        msg.reply_text(config.BOT_START_MESSAGE, reply_markup=keyboard)

    def cmd_balance(self, bot, update):
        msg = update.message
        username = msg.from_user.username
        try:
            sym, coin = self._parse_sym_coin(msg, 1)
        except ShowUsage:
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(sym, callback_data='/balance ' + sym) for sym in config.COIN_SYMBOLS]])
            msg.reply_text("Choose coin:", reply_markup=keyboard)
            return
        amount = self._format_amount(coin.request('getbalance', [username, config.MINCONF])['result'])
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
        try:
            sym, coin = self._parse_sym_coin(msg, 1)
        except ShowUsage:
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(sym, callback_data='/deposit ' + sym) for sym in config.COIN_SYMBOLS]])
            msg.reply_text("Choose the coin you want to deposit:", reply_markup=keyboard)
            return
                                 
        addr = self.get_addr(coin, username)
        bot.send_message(msg.chat_id, f"Deposit {sym} to {addr}")
        #bot.send_photo(msg.chat_id, f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={addr}")
        bot.send_photo(msg.chat_id, f"https://chart.googleapis.com/chart?chs=150x150&cht=qr&chl={addr}")

    def cmd_withdraw(self, bot, update):
        msg = update.message
        username = msg.from_user.username
        amount = self._parse_amount(msg, 1)
        sym, coin = self._parse_sym_coin(msg, 2)
        toaddr = self._parse_addr(msg, 3)
        balance = self._format_amount(coin.request('getbalance', [username, config.MINCONF])['result'])
        if amount > balance:
            raise Exception(f"You only have {balance} {sym}.")
        result = coin.request('sendfrom', [username, toaddr, amount, config.MINCONF])
        bot.send_message(msg.chat_id, f"Sent {amount} {sym} to {toaddr}.")

    def cmd_tip(self, bot, update):
        msg = update.message
        parts = msg.text.split()
        if len(parts) < 4:
            raise ShowUsage("How to properly tip:\n")
        
        recipients = []
        for i in range(1, len(parts)):
            if parts[i].startswith('@'):
                recipients.append(parts[i][1:])
            else:
                break
        if not recipients:
            raise ShowUsage()

        username = msg.from_user.username
        amount = self._parse_amount(msg, i)
        sym, coin = self._parse_sym_coin(msg, i + 1)
        
        recipients = set(recipients)
        if username in recipients:
            raise Exception(f"\nPhase 1: @{username} tips themself\nPhase 2: ???\nPhase 3: Profit!")
        if amount * len(recipients) > coin.request('getbalance', [username, config.MINCONF])['result']:
            raise Exception(f"Not enough {sym} coins in your account")
        for recipient in recipients:
            toaddr = self.get_addr(coin, recipient)
            result = coin.request('sendfrom', [username, toaddr, amount, config.MINCONF])
            bot.send_message(msg.chat_id, f"Congratulations @{recipient}, you have been tipped {amount} {sym} by @{username}")

    def _get_prices(self, sym):
        try:
            p = config.COIN_PRICE[sym]()
        except:
            try:
                p = (float(requests.get("https://api.tokens.net/public/ticker/{}usdt/".format(sym.lower())).json()['ask']), 'USD')
            except:
                try:
                    p = (float(requests.get("https://api.tokens.net/public/ticker/{}btc/".format(sym.lower())).json()['ask']), 'BTC')
                except:
                    raise Exception(f'Unknown ticker: {sym}')
        p_btc = config.COIN_PRICE['BTC']()
        if p[1] == 'USD':
            return [(round_price(p[0]), p[1]), (int(p[0] / p_btc[0] * (10**8) * 100) / 100, 'sats')]
        elif p[1] == 'BTC':
            return [(round_price(p[0] * p_btc[0]), 'USD'), (int(p[0] * (10**8) * 100) / 100, 'sats')]

    def cmd_p(self, bot, update):
        msg = update.message
        syms = [x.upper() for x in msg.text.split()[1:]]
        if not syms:
            syms = config.GROUP_COINS.get(msg.chat.username, [])
        if not syms:
            raise ShowUsage()
        s = 'Prices from <a href="https://coinpaprika.com"><i>Coinpaprika API</i></a>\n'
        for sym in syms:
            prices = self._get_prices(sym)
            s += ('1 {} = '.format(sym) + ' or '.join('<b>{} {}</b>'.format(p[0], p[1]) for p in prices) + '\n')
        bot.send_message(msg.chat_id, text=s, parse_mode=ParseMode.HTML)

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

    def cmd_test1(self, bot, update):
        msg = update.message
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('LANA', callback_data='/balance LANA')]])
        msg.reply_text("Choose coin:", reply_markup=keyboard)
        #bot.send_message(msg.chat_id, "test1")


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('telegram.bot').setLevel(logging.INFO)
    cb = Cryptobot()
    cb.loop()
