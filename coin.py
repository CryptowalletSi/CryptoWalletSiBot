import logging
log = logging.getLogger('coin')

import json

import requests

import config


class Coin:
    def __init__(self, symbol, name, rpc_url):
        self.symbol = symbol
        self.name = name
        self.rpc_url = rpc_url

    def request(self, method, params=[]):
        result = {'error': 'Sorry, an unexpected error occured while trying to connect to node'}
        try:
            data = {'method': method, 'params': params}
            result = requests.post(self.rpc_url, data=json.dumps(data)).json()
        except Exception as e:
            result = {'error': str(e)}
        log.debug("request_result:" + str(result))
        return result


COINS = {
            sym: Coin(symbol=sym, name=config.COIN_CONFIG[sym]['name'], rpc_url=config.COIN_CONFIG[sym]['rpc_url'])
            for sym in config.COIN_SYMBOLS
        }
