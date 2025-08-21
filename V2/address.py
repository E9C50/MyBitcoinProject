import pymysql
import hashlib
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

# rpc_user and rpc_password are set in the bitcoin.conf file
rpc_user = "xxx"
rpc_password = "xxx"
rpc_connection = AuthServiceProxy(
    "http://%s:%s@127.0.0.1:8332" % (rpc_user, rpc_password)
)


# 连接数据库
connection = pymysql.connect(
    host="localhost",  # 替换为实际数据库主机地址
    user="root",  # 替换为实际用户名
    password="xxx",  # 替换为实际密码
    database="bitcoin",  # 对应的数据库名
    charset="utf8mb4",  # 推荐使用utf8mb4字符集
)


def save_transaction_data(type, amount, address, block_height, block_hash, tx_hash, block_time):
    try:
        id_str = f'{block_height}-{block_hash}-{tx_hash}-{type}-{address}-{amount}'
        
        sha512_hash = hashlib.sha512()
        sha512_hash.update(id_str.encode('utf-8'))
        id_hash = sha512_hash.hexdigest()

        with connection.cursor() as cursor:
            insert_query = f"""
                INSERT INTO transactions (id, type, amount, address, bloch_height, block_hash, tx_hash, block_time)
                VALUES ('{id_hash}', '{type}', {amount}, '{address}', {block_height}, '{block_hash}', '{tx_hash}', FROM_UNIXTIME({block_time}))
                ON DUPLICATE KEY UPDATE amount = VALUES(amount)
            """
            cursor.execute(insert_query)
            connection.commit()
    except pymysql.MySQLError as e:
        print(f"数据库操作出现错误: {e}")


def process_transaction(transaction, block_hash, block_height, tx_hash, block_time):
    total_in = 0
    total_out = 0
    for vin in transaction["vin"]:
        if vin.get("coinbase"):
            # print(f"VIN Block: {412232}, Amount: -, Address: coinbase")
            pass
        else:
            prev_txid = vin["txid"]
            prev_vout_index = vin["vout"]
            prev_tx = rpc_connection.getrawtransaction(prev_txid, 1)
            prev_output = prev_tx["vout"][prev_vout_index]

            if ("scriptPubKey" in prev_output and "address" in prev_output["scriptPubKey"]):
                sender = prev_output["scriptPubKey"]["address"]
                amount = prev_output["value"]
                # print(f"VIN Block: {412232}, Amount: {amount}, Address: {sender}")
                save_transaction_data('vin', amount, sender, block_height, block_hash, tx_hash, block_time)
                total_in += amount
            else:
                # print(f"VIN Block: {412232}, Amount: -, Address: coinbase")
                pass

    for vout in transaction["vout"]:
        receiver = vout["scriptPubKey"].get("address")
        if not receiver:
            # print(f"VOUT Block: {412232}, Amount: -, Address: coinbase")
            pass
        else:
            # print(f"VOUT Block: {412232}, Amount: {vout['value']}, Address: {receiver}, type: {vout['scriptPubKey']['type']}")
            save_transaction_data('vout', vout['value'], receiver, block_height, block_hash, tx_hash, block_time)
            total_out += vout["value"]


def process_block(height):
    # print('process block ' + str(height))
    block_hash = rpc_connection.getblockhash(height)
    block = rpc_connection.getblock(block_hash)
    for tx in block["tx"]:
        transaction = rpc_connection.getrawtransaction(tx, 1)
        process_transaction(transaction, block_hash, height, tx, block['time'])


def main():
    # Genesis Block 的第一笔交易无法访问，这里手动插入
    save_transaction_data('vout', 50.0, '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa', 0, 
                          '000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f', 
                          '4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b', 
                          1231006505)
    # 获取最新的区块高度
    latest_block_height = rpc_connection.getblockcount()
    for height in range(203179, latest_block_height + 1):
        process_block(height)


if __name__ == "__main__":
    main()
    # process_block(412232)
