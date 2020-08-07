# Message returned by the bot on /start command
BOT_START_MESSAGE = """
Hi, welcome to CryptoWalletSiBot.

Supported coins:
    - LANA
    - TAJ

Available commands:
    /start - shows this message
    /balance <coin> - show balance
    /deposit <coin> - get deposit address
    /withdraw <coin> <addr> - withdraw your coins
    /tip <@user> <amount> <coin> - tip user
"""

# Telegram bot token
TELEGRAM_TOKEN = '1084265308:AAE4KO9J2OEc4RFG1d4SvhxxPnCMR4fo5zM'

# Implemented coins
COIN_SYMBOLS = ['LANA', 'TAJ']

# Coin configuration
COIN_CONFIG = {
    'LANA': {
        'symbol': 'LANA',
        'name': 'LanaCoin',
        'rpc_url': 'http://cryptobot:idkfa123@localhost:5706/',
    },
    'TAJ': {
        'symbol': 'TAJ',
        'name': 'TajCoin',
        'rpc_url': 'http://cryptobot:idkfa123@localhost:12107/',
    },
}

# Minimum confirmed blocks when calculating account balances
MINCONF = 0



try:
    from local_config import *
except:
    pass