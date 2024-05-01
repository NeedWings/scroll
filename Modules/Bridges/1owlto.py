from modules.base_classes.base_account import BaseAccount
from modules.utils.utils import req
from modules.utils.txn_data_handler import TxnDataHandler
from modules.utils.Logger import logger

class Owlto:
    supported_nets = ["ethereum", "arbitrum", "zksync", "base", "optimism", "linea"]

    chain_ids = {
        "ethereum": 1,
        "arbitrum": 42161,
        "zksync": 324,
        "base": 8453,
        "optimism": 10,
        "linea": 59144
    }

    owlto_ids = {
        "ethereum": "0001",
        "arbitrum": "0004",
        "zksync": "0002",
        "base": "0012",
        "optimism": "0003",
        "linea": "0007",
    }

    def __init__(self, account: BaseAccount) -> None:
        self.account = account

    def get_owlto_data(self, net_name):
        
        chain_id = self.chain_ids[net_name]
        r = req(f"https://owlto.finance/api/lp-info?token=ETH&from_chainid={chain_id}&to_chainid=534352&user={self.account.get_address()}")
        min_val = int(r["msg"]["min"])/1e18
        max_val = int(r["msg"]["max"])/1e18
        fee = int(r["msg"]["dtc"])/1e18
        maker = r["msg"]["maker_address"]
        return min_val, max_val, fee, maker
    

    def get_bridge_txn(self, net_name, amount):
        w3 = self.account.get_w3(net_name)

        txn_data_handler = TxnDataHandler(self.account, net_name, w3=w3)
        min_amount, max_amount, fee, maker = self.get_owlto_data(net_name)

        if amount < min_amount+fee or amount > max_amount+fee:
            logger.error(f"[{self.account.get_address()}] amount to bridge ({amount}) not in owlto limits (min: {min_amount+fee}, max: {max_amount+fee})")
            return -1

        str_amount = str(int(amount*1e18))

        str_amount = str_amount[:-4] + "0006"        

        value = int(str_amount)

        txn = txn_data_handler.get_txn_data(value)
        txn["to"] = maker

        return txn
    
    def get_owlto_data_withdraw(self, net_name):

        chain_id = self.chain_ids[net_name]
        r = req(f"https://owlto.finance/api/lp-info?token=ETH&from_chainid=534352&to_chainid={chain_id}&user={self.account.get_address()}")
        min_val = int(r["msg"]["min"])/1e18
        max_val = int(r["msg"]["max"])/1e18
        fee = int(r["msg"]["dtc"])/1e18
        maker = r["msg"]["maker_address"]

        return min_val, max_val, fee, maker


    def get_withdraw_txn(self, net_name, amount):
        w3 = self.account.get_w3("scroll")
        min_amount, max_amount, fee, maker = self.get_owlto_data_withdraw(net_name)
        

        txn_data_handler = TxnDataHandler(self.account, "scroll", w3=w3)

        if amount < min_amount+fee or amount > max_amount+fee:
            logger.error(f"[{self.account.get_address()}] amount to bridge ({amount}) not in owlto limits (min: {min_amount+fee}, max: {max_amount+fee})")
            return -1

        str_amount = str(int(amount*1e18))
        code = self.owlto_ids[net_name]
        str_amount = str_amount[:-4] + code       

        value = int(str_amount)

        txn = txn_data_handler.get_txn_data(value)
        txn["to"] = maker

        return txn    
