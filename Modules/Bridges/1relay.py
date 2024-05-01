from web3 import Web3

from modules.base_classes.base_account import BaseAccount
from modules.utils.Logger import logger
from modules.utils.utils import req_post, sleeping_sync

class Relay:

    chain_ids = {
        "arbitrum": 42161,
        "optimism": 10
    }
    def __init__(self, account: BaseAccount) -> None:
        self.account = account


    def bridge_to_eth(self, amount, net_from):
        try:
            w3 = self.account.get_w3(net_from)
            resp = req_post(
                "https://api.relay.link/execute/bridge", 
                json={
                    "user":self.account.address,
                    "recipient":self.account.address,
                    "originChainId":self.chain_ids[net_from],
                    "destinationChainId":1,
                    "currency":"eth",
                    "amount":str(int(amount*1e18)),
                    "source":"relay.link",
                    "usePermit":False,
                    "useExternalLiquidity":False
                }, proxies=self.account.proxies)
            nonce = w3.eth.get_transaction_count(self.account.address)
            bridge_txn = resp["steps"][0]["items"][0]["data"]
            bridge_txn["value"] = int(bridge_txn["value"])
            bridge_txn["maxFeePerGas"] = int(bridge_txn["maxFeePerGas"])
            bridge_txn["maxPriorityFeePerGas"] = int(bridge_txn["maxPriorityFeePerGas"])
            bridge_txn["to"] = Web3.to_checksum_address(bridge_txn["to"])
            bridge_txn["nonce"] = nonce
            self.account.send_txn(bridge_txn, net_from)
            return True
        except Exception as e:
            logger.error(f"[{self.account.address}] got error: {e}")
            sleeping_sync(self.account.address, True)
            return False

