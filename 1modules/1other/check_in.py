from datetime import datetime

from eth_abi import encode

from modules.utils.account import Account
from modules.utils.txn_data_handler import TxnDataHandler

class CheckIn:
    
    def owlto(self, sender: Account):
        now_time = datetime.now()
        for_checkin = int(f"{now_time.year}{str(now_time.month).rjust(2, '0')}{str(now_time.day).rjust(2, '0')}")
        w3 = sender.get_w3('scroll')
        txn_data_handler = TxnDataHandler(sender, 'scroll', w3=w3)
        txn = txn_data_handler.get_txn_data()
        txn["to"] = "0xE6FEcA764B7548127672C189D303eb956c3Ba372"
        txn["data"] = "0xe95a644f" + encode(['uint256'], [for_checkin]).hex()
        return txn
    
    def rubyscore(self, sender: Account):
        w3 = sender.get_w3('scroll')
        txn_data_handler = TxnDataHandler(sender, 'scroll', w3=w3)
        txn = txn_data_handler.get_txn_data()
        txn["to"] = "0xe10Add2ad591A7AC3CA46788a06290De017b9fB4"
        txn["data"] = "0x632a9a52"
        return txn