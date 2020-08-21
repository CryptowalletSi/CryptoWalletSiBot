import logging
log = logging.getLogger('coin')

import json

import requests

import config
from errors import UnknownTicker, RpcError

class Coin:
    def __init__(self, symbol, name, rpc_url):
        self.symbol = symbol
        self.name = name
        self.rpc_url = rpc_url

    def request(self, method, params=[]):
        data = {'method': method, 'params': params}
        result = requests.post(self.rpc_url, data=json.dumps(data)).json()
        log.debug("request_result:" + str(result))
        if result.get('error'):
            raise RpcError(result['error'])
        return result


COINS = {
    sym: Coin(symbol=sym, name=config.COIN_CONFIG[sym]['name'], rpc_url=config.COIN_CONFIG[sym]['rpc_url'])
    for sym in config.COIN_SYMBOLS
}

def get_coin(sym):
    if sym in COINS:
        return COINS[sym]
    raise UnknownTicker(sym)

