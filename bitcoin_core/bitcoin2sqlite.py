import sqlite3

import pandas as pd

from bitcoin_core.bitcoin_core_util import *


def init_sqlite():
    conn = sqlite3.connect('../bitcoin.db')
    conn.close()


def loop_block(block_hash):
    while True:
        print(block_hash)
        block_info = get_block(block_hash)
        for txid in block_info['tx']:
            tx_info = pd.DataFrame((block_hash, txid)).T
            tx_info.to_csv('tx_hash.csv', mode='a', header=False, index=False)
        block_hash = block_info['nextblockhash']


if __name__ == '__main__':
    # init_sqlite()
    loop_block('000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f')
