import json

import requests

url = 'http://127.0.0.1:8332'
username, password = 'e9c50', '516200'


def bitcoin_cli(method, params):
    payload = json.dumps({'jsonrpc': '2.0', 'id': 'minebet', 'method': method, 'params': params})
    return requests.post(url, auth=(username, password), data=payload).json()['result']


def get_block_hash(block_id):
    block_hash = bitcoin_cli('getblockhash', [block_id])
    return block_hash


def get_block(block_hash):
    block_info = bitcoin_cli('getblock', [block_hash])
    return block_info


def get_hex_transaction(txid):
    transaction_hex = bitcoin_cli('getrawtransaction', [txid])
    return transaction_hex


def decode_hex_transaction(hex_transaction):
    transaction_info = bitcoin_cli('decoderawtransaction', [hex_transaction])
    return transaction_info


def my_test():
    block_hash = get_block_hash(1)
    print(f'block_hash: {block_hash}')

    block_info = get_block(block_hash)
    print(f'block_info: {block_info}')

    for txid in block_info['tx']:
        hex_transaction = get_hex_transaction(txid)
        print(f'hex_transaction: {hex_transaction}')

        transaction_info = decode_hex_transaction(hex_transaction)
        print(f'transaction_info: {transaction_info}')


if __name__ == '__main__':
    my_test()
