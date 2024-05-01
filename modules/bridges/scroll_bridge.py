from eth_abi import encode

from modules.base_classes.base_account import BaseAccount
from modules.utils.txn_data_handler import TxnDataHandler

class ScrollBridge:

    def __init__(self, account: BaseAccount) -> None:
        self.acount = account

    def estimate_fee(self):
        w3 = self.acount.get_w3("scroll")
        gwei = w3.eth.gas_price
        gas = w3.eth.estimate_gas({
            "from": w3.to_checksum_address("0x7885bcbd5cecef1336b5300fb5186a12ddd8c478"),
            "to": w3.to_checksum_address("0x781e90f1c8fc4611c9b7497c3b47f99ef6969cbc"),
            "data": "0x8ef1332e00000000000000000000000079a49a6edc7888632ed61b72a70d1ce1cca25e9c00000000000000000000000079a49a6edc7888632ed61b72a70d1ce1cca25e9c0000000000000000000000000000000000000000000000000000000000000001ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff00000000000000000000000000000000000000000000000000000000000000a00000000000000000000000000000000000000000000000000000000000000000"
        })

        return int(gas*1.4), int(gas*1.4*gwei*1.2)


    def get_bridge_txn(self, amount):
        w3 = self.acount.get_w3("ethereum")
        txn_data_handler = TxnDataHandler(self.acount, "ethereum", w3=w3)
        gas, fee = self.estimate_fee()
        value = int(amount*1e18) + fee
        txn = txn_data_handler.get_txn_data(value)
        txn["to"] = "0x6774Bcbd5ceCeF1336b5300fb5186a12DDD8b367"
        txn["data"] = "0xb2267a7b" + encode(["address", "uint256", "bytes", "uint256"], [self.acount.address, int(amount*1e18), b'', gas]).hex()
        return txn