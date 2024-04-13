import requests

from modules.utils.account import Account
from modules.utils.Logger import logger
from modules.utils.txn_data_handler import TxnDataHandler
from modules.utils.utils import sleeping_sync

class RouterNitro:

    chain_ids = {
        "ethereum": 1,
        "arbitrum": 42161,
        "scroll": 534352,
        "zksync": 324,
        "linea": 59144,
        "optimism": 10
    }

    def __init__(self, account: Account) -> None:
        self.account = account
        self.proxy = account.proxies

    def get_bridge_txn(self, net_from: str, amount: float):
        while True:
            try:
                w3 = self.account.get_w3(net_from)
                txn_data_handler = TxnDataHandler(self.account, net_from, w3=w3)
                r = requests.get(f"https://api-beta.pathfinder.routerprotocol.com/api/v2/quote?fromTokenAddress=0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE&toTokenAddress=0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE&amount={int(amount*1e18)}&fromTokenChainId={self.chain_ids[net_from]}&toTokenChainId={self.chain_ids['scroll']}&partnerId=1&destFuel=0",
                                 proxies=self.proxy)
                try:
                    data = r.json()
                except:
                    logger.error(f"[{self.account.address}] can't get bridge data: {r.text}")
                    sleeping_sync(self.account.address, True)
                    continue
                data["receiverAddress"] = self.account.address
                data["senderAddress"] = self.account.address
                bridge_resp = requests.post("https://api-beta.pathfinder.routerprotocol.com/api/v2/transaction", json=data, proxies=self.proxy)
                txn = bridge_resp.json()["txn"]
                txn_data = txn["data"]
                value = txn["value"]
                to = txn["to"]
                real_txn = txn_data_handler.get_txn_data(int(value, 16))
                real_txn["to"] = w3.to_checksum_address(to)
                real_txn['data'] = txn_data
                return real_txn
            except Exception as e:
                logger.error(f"[{self.account.address}] can't get bridge data: {e}")
                sleeping_sync(self.account.address, True)

    def get_withdraw_txn(self, net_to: str, amount: float):
        while True:
            try:
                w3 = self.account.get_w3("scroll")
                txn_data_handler = TxnDataHandler(self.account, "scroll", w3=w3)
                r = requests.get(f"https://api-beta.pathfinder.routerprotocol.com/api/v2/quote?fromTokenAddress=0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE&toTokenAddress=0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE&amount={int(amount*1e18)}&fromTokenChainId={self.chain_ids['scroll']}&toTokenChainId={self.chain_ids[net_to]}&partnerId=1&destFuel=0",
                                 proxies=self.proxy)
                try:
                    data = r.json()
                except:
                    logger.error(f"[{self.account.address}] can't get bridge data: {r.text}")
                    sleeping_sync(self.account.address, True)
                    continue
                data["receiverAddress"] = self.account.address
                data["senderAddress"] = self.account.address
                bridge_resp = requests.post("https://api-beta.pathfinder.routerprotocol.com/api/v2/transaction", json=data, proxies=self.proxy)
                txn = bridge_resp.json()["txn"]
                txn_data = txn["data"]
                value = txn["value"]
                to = txn["to"]
                real_txn = txn_data_handler.get_txn_data(int(value, 16))
                real_txn["to"] = w3.to_checksum_address(to)
                real_txn['data'] = txn_data
                return real_txn
            except Exception as e:
                logger.error(f"[{self.account.address}] can't get bridge data: {e}")
                sleeping_sync(self.account.address, True)

