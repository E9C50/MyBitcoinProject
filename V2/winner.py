import json
import bitcoin
import requests
import threading
import pandas as pd


# 生成一个随机的密钥
def demo_generate_private_key():
    # 生成一个用十六进制表示的长 256 位的私钥（str类型）
    private_key = bitcoin.random_key()
    # 解码为十进制的整形密钥
    decoded_private_key = bitcoin.decode_privkey(private_key, 'hex')
    if not 0 < decoded_private_key < bitcoin.N:
        return demo_generate_private_key()

    # 用 WIF 格式编码密钥
    wif_encoded_private_key = bitcoin.encode_privkey(decoded_private_key, 'wif')
    # 用 01 标识的压缩密钥
    compressed_private_key = private_key + '01'
    # 生成 WIF的压缩格式
    wif_compressed_private_key = bitcoin.encode_privkey(bitcoin.decode_privkey(compressed_private_key, 'hex'), 'wif')
    return private_key, decoded_private_key, wif_encoded_private_key, compressed_private_key, wif_compressed_private_key


# 私钥转公钥
def demo_private_to_public(decoded_private_key):
    # 计算公钥坐标 K = k * G
    public_key = bitcoin.fast_multiply(bitcoin.G, decoded_private_key)
    # 计算公钥
    hex_encoded_public_key = bitcoin.encode_pubkey(public_key, 'hex')
    # 计算压缩公钥
    # if public_key[1] % 2 == 0:  # 两种方式均可
    compressed_prefix = '02' if public_key[1] & 1 == 0 else '03'
    # 转十六也可用 bitcoin_core.encode(xxx, 16)
    hex_compressed_public_key = compressed_prefix + hex(public_key[0])[2:]
    return public_key, hex_encoded_public_key, compressed_prefix, hex_compressed_public_key


# 公钥转地址
def demo_public_to_address(public_key, hex_compressed_public_key):
    # 计算地址
    # 传入公钥坐标对象/十六进制公钥值，输出同样的地址
    # 传入压缩公钥值，输出与⬆️不同的地址
    address = bitcoin.pubkey_to_address(public_key)
    compressed_address = bitcoin.pubkey_to_address(hex_compressed_public_key)
    return address, compressed_address


# def get_address_balance(address):
#     url_block = "https://bitcoin.atomicwallet.io/address/" + str(address)
#     response_block = requests.get(url_block)
#     byte_string = response_block.content
#     source_code = html.fromstring(byte_string)
#     tree_txid = source_code.xpath('/html/body/main/div/div/div[1]/h4/div/span')
#     return str(tree_txid[0].text_content())


# def get_address_balance(address):
#     # url_block = "https://blockchain.info/q/addressbalance/bc1qeyhhvdcx3ppe7jkhr8xqavy0xgmjxn9rw7n687"
#     url_block = "https://blockchain.info/q/addressbalance/" + str(address)
#     response_block = requests.get(url_block)
#     byte_string = response_block.text
#     return int(byte_string)


# def get_address_balance(address):
#     url_block = "https://api.blockcypher.com/v1/btc/main/addrs/" + str(address) + '/balance'
#     response_block = requests.get(url_block)
#     print(response_block.text)
#     json_info = json.loads(response_block.text)
#     check_result = json_info['balance'] > 0 or json_info['unconfirmed_balance'] > 0 or json_info['total_received'] > 0 or json_info['total_sent'] > 0
#     print(check_result + ' ' + json_info['balance'])
#     return check_result, json_info['balance']


def get_address_balance(address):
    balance = all_balance.get(address)
    if balance is None:
        balance = 0
    return int(balance)


# 获取余额账户信息
def get_all_balance():
    balance = pd.read_csv('./addresses_with_balance.csv')[['address', 'value_satoshi']]
    balance['balance'] = balance['value_satoshi'] * 0.00000001
    balance = balance.set_index('address')['balance'].to_dict()
    return balance


# 发送邮件通知
def send_qq_message(message_content):
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({"user_id": '2250795018', "message": message_content})
    requests.post('http://10.1.1.50:3000/send_private_msg', data=data, headers=headers)


def send_message():
    requests.get('https://api2.pushdeer.com/message/push?pushkey=xxxxxx&text=挖到Bitcoin啦！！！')


# 写入本地文件备份
def write_txt(file_name, message_content):
    with open(file_name, mode='a', encoding='utf-8') as file:
        file.write(message_content)
        file.close()


def process():
    while True:
        try:
            private_key, decoded_private_key, wif_encoded_private_key, compressed_private_key, wif_compressed_private_key = demo_generate_private_key()
            public_key, hex_encoded_public_key, compressed_prefix, hex_compressed_public_key = demo_private_to_public(decoded_private_key)
            address, compressed_address = demo_public_to_address(public_key, hex_compressed_public_key)
            
            address_balance = get_address_balance(address)
            compressed_address_balance = get_address_balance(compressed_address)
        except:
            continue

        if address_balance is None and compressed_address_balance is None:
            print(f'【empty address】{address}')
            continue

        address_info = '====================================================================================================\n'
        address_info += f'密钥（十六进制）： {private_key} （长 256 位）\n'
        address_info += f'密钥（十进制）： {decoded_private_key} （0 到 1.158*10**77 之间）\n'
        address_info += f'密钥（WIF）： {wif_encoded_private_key} （5 开头，长 51 字符）\n'
        address_info += f'压缩密钥（十六进制）： {compressed_private_key} （01 结尾，长 264 位）\n'
        address_info += f'压缩密钥（WIF）： {wif_compressed_private_key} （L/K 开头）\n'
        address_info += '\n'

        address_info += f'公钥（坐标）： {public_key}\n'
        address_info += f'公钥（坐标的十六进制）： {tuple(hex(i) for i in public_key)}\n'  # 转十六也可用 bitcoin_core.encode(xxx, 16)
        address_info += f'公钥（十六进制）： {hex_encoded_public_key} （04 x y）\n'
        address_info += f'压缩公钥（十六进制）： {hex_compressed_public_key}（02 开头代表 y 是偶数，03 开头代表 y 是奇数）\n'
        address_info += '\n'

        address_info += f'地址（b58check）： {address} （1 开头）\n'
        address_info += f'压缩地址（b58check）： {compressed_address} （1 开头）\n'
        address_info += f'地址余额： {address_balance}\n'
        address_info += f'压缩地址余额： {compressed_address_balance}\n'
        address_info += '====================================================================================================\n'

        print(address_info)
        if address_balance != 0 or compressed_address_balance != 0:
            write_txt('winner.txt', address_info)
            send_message()
            # send_qq_message(address_info)
        # else:
        #     failed_raw = f'{private_key},{decoded_private_key},{wif_encoded_private_key},{compressed_private_key},{wif_compressed_private_key},{public_key},{hex_encoded_public_key},{hex_compressed_public_key},{address},{compressed_address},{address_balance},{compressed_address_balance}\n'
        #     write_txt('failed.csv', failed_raw)


if __name__ == '__main__':
    all_balance = get_all_balance()
    num_threads = 64
    threads = []

    for i in range(num_threads):
        thread = threading.Thread(target=process)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()



# if __name__ == '__main__':
#     all_balance = get_all_balance()
#     process()


# ====================================================================================================
# 密钥（十六进制）： d5446e6ef4688469b0fa5dee42f24d410e32bfdcdd428c8a56ae935fc8c1ae3a （长 256 位）
# 密钥（十进制）： 96463544532072146271392022730337709728828796264685013938263473065260736425530 （0 到 1.158*10**77 之间）
# 密钥（WIF）： 5KSDD4MXdm1kdpRvit6QbFWGtxz7U4pc8aKZm8dakkscT1rzGZq （5 开头，长 51 字符）
# 压缩密钥（十六进制）： d5446e6ef4688469b0fa5dee42f24d410e32bfdcdd428c8a56ae935fc8c1ae3a01 （01 结尾，长 264 位）
# 压缩密钥（WIF）： L4NGtDocDFGKbWM27rWs8B2DAN75YTs84S4wbngTz8ePTTcaYM6F （L/K 开头）

# 公钥（坐标）： (41904956895999193556637845217544731195949273853916853865471078000575931304306, 8555476727034004746321506999909773110886852329015240330012788214419557058439)
# 公钥（坐标的十六进制）： ('0x5ca55d76a11ac6c7ba3f1202fa0c9be0a49ceaebcd6b5214484c81f355454972', '0x12ea3a6cfad29cd3afb5986dcf5829fd4e9bc94005720c1cdfed80603f7a0787')
# 公钥（十六进制）： 045ca55d76a11ac6c7ba3f1202fa0c9be0a49ceaebcd6b5214484c81f35545497212ea3a6cfad29cd3afb5986dcf5829fd4e9bc94005720c1cdfed80603f7a0787 （04 x y）
# 压缩公钥（十六进制）： 035ca55d76a11ac6c7ba3f1202fa0c9be0a49ceaebcd6b5214484c81f355454972（02 开头代表 y 是偶数，03 开头代表 y 是奇数）

# 地址（b58check）： 19ZdkokqBiVRGRJgU22NCPii5bpTHMcdqp （1 开头）
# 压缩地址（b58check）： 152S2dVY3Mo6KpkGGcQerDCDpkdvA6Sxxy （1 开头）
# 地址余额： 0 BTC
# 压缩地址余额： 0 BTC
# ====================================================================================================
