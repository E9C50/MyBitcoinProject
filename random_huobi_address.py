import os

import bitcoin


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
    return wif_encoded_private_key, wif_compressed_private_key


if __name__ == '__main__':
    while True:
        wif_encoded_private_key, wif_compressed_private_key = demo_generate_private_key()
        print(wif_encoded_private_key + ',')
