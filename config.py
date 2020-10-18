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
MINCONF = 0

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
}

# Prices to display on /price command
GROUP_COINS = {
    None: ['BTC', 'LANA', 'TAJ', 'ARCO', 'NETKO', 'NEVA'],
    'LanaCoin': ['LANA'],
    'TajCoin': ['TAJ'],
    'AquariusCoin': ['ARCO'],
    'NetkoCoin': ['NETKO'],
    'neva_coin': ['NEVA'],
}

# Group specific config
GROUP_CONFIG = {
    'TokensNetExchange': {
        'command_blacklist': ['tip'],
    },
}

# Groups where captcha feature is active
CAPTCHA_GROUPS = ['botektest', 'OCProtocol_OCP']

CAPTCHA_SECONDS = 3 * 60


try:
    from local_config import *
except:
    pass
