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
    - NETKO
    - NEVA

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
COIN_SYMBOLS = ['LANA', 'TAJ', 'OCP', 'ARCO', 'NETKO', 'NEVA']

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
    'NETKO': {
        'symbol': 'NETKO',
        'name': 'Netko',
        'rpc_url': 'http://user:pass@localhost:25970',
    },
    'NEVA': {
        'symbol': 'NEVA',
        'name': 'NevaCoin',
        'rpc_url': 'http://user:pass@localhost:3791',
    },
}

# Coin price fetching functions
COIN_PRICE = {
    'BTC': lambda: (float(requests.get("https://api.tokens.net/public/ticker/btcusdt/").json()['ask']), 'USD'),    
    'LANA': lambda: (float(requests.get("https://api.tokens.net/public/ticker/lanausdt/").json()['ask']), 'USD'),
    'TAJ': lambda: (float(requests.get("https://api.tokens.net/public/ticker/tajbtc/").json()['ask']), 'BTC'),
    'ARCO': lambda: (float(requests.get("https://api.tokens.net/public/ticker/arcobtc/").json()['ask']), 'BTC'),
    'NETKO': lambda: (float(requests.get("https://api.tokens.net/public/ticker/netkousdt/").json()['ask']), 'USD'),
    'NEVA': lambda: (float(requests.get("https://api.tokens.net/public/ticker/nevausdt/").json()['ask']), 'USD'),
    'C2O': lambda: (float(requests.get("https://api.tokens.net/public/ticker/c2ousdt/").json()['ask']), 'USD'),
    'DTR': lambda: (float(requests.get("https://api.tokens.net/public/ticker/dtrusdt/").json()['ask']), 'USD'),
    'ETH': lambda: (float(requests.get("https://api.tokens.net/public/ticker/ethusdt/").json()['ask']), 'USD'),
    'BCH': lambda: (float(requests.get("https://api.tokens.net/public/ticker/bchusdt/").json()['ask']), 'USD'),
    'LTC': lambda: (float(requests.get("https://api.tokens.net/public/ticker/ltcusdt/").json()['ask']), 'USD'),
    'XRP': lambda: (float(requests.get("https://api.tokens.net/public/ticker/xrpusdt/").json()['ask']), 'USD'),
    'XLM': lambda: (float(requests.get("https://api.tokens.net/public/ticker/xlmusdt/").json()['ask']), 'USD'),
}

# Prices to display on /price command
GROUP_COINS = {
    None: ['LANA', 'TAJ', 'ARCO', 'NETKO', 'NEVA'],
    'TokensNetExchange': ['BTC', 'LANA', 'ARCO', 'TAJ', 'C2O', 'DTR', 'ETH', 'NETKO', 'NEVA', 'XLM', 'LTC', 'XRP'],
    'LanaCoin': ['LANA'],
    'TajCoin': ['TAJ'],
    'AquariusCoin': ['ARCO'],
    'NetkoCoin': ['NETKO'],
    'neva_coin': ['NEVA'],
}

# Group specific config
GROUP_CONFIG = {
    'TokensNetExchange': {
        'command_blacklist': [],
    },
}

# Groups where captcha feature is active
CAPTCHA_GROUPS = ['botektest', 'CryptoWaterSi', 'TokensNetExchange', 'OCProtocol_OCP', 'LanaCoin', 'TajCoin', 'AquariusCoin', 'NetkoCoin', 'neva_coin']

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
