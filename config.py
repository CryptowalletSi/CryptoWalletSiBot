ADMINS = []

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
TELEGRAM_TOKEN = 'changeme'

# Implemented coins
COIN_SYMBOLS = ['LANA', 'TAJ']

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
}

# Minimum confirmed blocks when calculating account balances
MINCONF = 0



try:
    from local_config import *
except:
    pass
