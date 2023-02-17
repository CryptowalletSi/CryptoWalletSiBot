import requests

# Telegram usernames of bot admins
ADMINS = []

# Message returned by the bot on /start command
BOT_START_MESSAGE = """
Hi, welcome to CryptoWalletSiBot.

Supported coins:
    - LANA
    - TAJ
    - OCP
    - ARCO

Available commands:
    /start - shows this message
    /balance <coin> - show balance
    /deposit <coin> - get deposit address
    /withdraw <amount> <coin> <addr> - withdraw your coins
    /tip <@user> <amount> <coin> - tip user
"""

# Telegram bot token
TELEGRAM_TOKEN = 'changeme'

# Minimum confirmed blocks when calculating account balances
MINCONF = 1

# Seconds you have to wait before sending next command to the bot
COMMAND_THROTTLE_SECONDS = 3

# Available bot commands
COMMANDS = ['start', 'balance', 'deposit', 'withdraw', 'tip', 'p', 'admin', 'test1']

# Commands available in groups
PUBLIC_COMMANDS = ['tip', 'p', 'captcha']

# Admin commands
ADMIN_COMMANDS = ['admin']

# Commands that don't require username set
ANON_COMMANDS = ['p', 'captcha']

# Implemented coins
COIN_SYMBOLS = ['LANA', 'TAJ', 'OCP', 'ARCO']

# Coin configuration
COIN_CONFIG = {
    'LANA': {
        'symbol': 'LANA',
        'name': 'LanaCoin',
        'rpc_url': 'http://user:pass@localhost:5706/',
    },
    'TAJ': {
        'symbol': 'TAJ',
        'name': 'TajCoin',
        'rpc_url': 'http://user:pass@localhost:12107/',
    },
    'OCP': {
        'symbol': 'OCP',
        'name': 'OC Protocol',
        'rpc_url': 'http://user:pass@localhost:8882/',
    },
    'ARCO': {
        'symbol': 'ARCO',
        'name': 'AquariusCoin',
        'rpc_url': 'http://user:pass@localhost:6206/',
    },
}

# Coin price fetching functions
COIN_PRICE = {    
    'LANA': lambda: (float(requests.get("https://api.coinpaprika.com/v1/tickers/lana-lanacoin?quotes=USD").json()['quotes']['USD']['price']), 'USD')
    'TAJ': lambda: (float(requests.get("https://api.coinpaprika.com/v1/tickers/taj-tajcoin?quotes=USD").json()['quotes']['USD']['price']), 'USD')
    'ARCO': lambda: (float(requests.get("https://api.coinpaprika.com/v1/tickers/arco-aquariuscoin?quotes=USD").json()['quotes']['USD']['price']), 'USD')
    'C2O': lambda: (float(requests.get("https://api.coinpaprika.com/v1/tickers/c2o-cryptowater?quotes=USD").json()['quotes']['USD']['price']), 'USD')
}

# Prices to display on /price command
GROUP_COINS = {
    None: ['LANA', 'TAJ', 'ARCO'],
    'LanaCoin': ['LANA'],
    'TajCoin': ['TAJ'],
    'AquariusCoin': ['ARCO'],
}

# Group specific config
GROUP_CONFIG = {
    'TokensNetExchange': {
        'command_blacklist': [],
    },
}

# Groups where captcha feature is active
CAPTCHA_GROUPS = ['OCProtocol_OCP', 'LanaCoin', 'TajCoin', 'AquariusCoin']

# Seconds until new user is kicked from a group
CAPTCHA_SECONDS = 1 * 60

# Captcha specific messages
CAPTCHA_MESSAGES = {
    None: {
        'new_user': "Hi {name}, please click the button below in {secs} seconds to verify you are not a bot:",
        'button': "I am not a bot",
        'user_verified': "Welcome to the group, {name}",
        'user_kicked': "",
    },
    'botektest': {
        'button': "Happy human button",
    },
}


try:
    from local_config import *
except:
    pass
