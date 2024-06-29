import requests
from eth_abi import encode

from modules.utils.txn_data_handler import TxnDataHandler
from modules.utils.account import Account
from modules.utils.utils import req, sleeping_sync
from modules.utils.Logger import logger
from modules.config import SETTINGS_PATH

class AlphaKey:

    def __init__(self, account: Account) -> None:
        self.account = account
        self.proxies = self.account.proxies

    def get_sig(self):
        while True:
            try:
                resp = requests.get(f"https://api.rhino.fi/activity-trackers/nftSignature/SCROLL?address={self.account.address}&nftType=ALPHAKEY", proxies=self.proxies)
                if str(resp.status_code).startswith("2"):
                    break
                elif str(resp.status_code) == "401":
                    logger.info(f"[{self.account.address}] Not Eligble. Skip")
                    return None
                else:
                    logger.error(f"[{self.account.address}] Bad status code. RESP: {resp.text}")
                    pass
            except Exception as error:
                logger.error(f"[{self.account.address}] Requests error: {error}")
            sleeping_sync(self.account.address, True)
        sig = resp.text.replace("\"", "")

        return sig
    
    def mint(self):
        logger.info(f"[{self.account.address}] going to mint Alpha Key")

        sig = self.get_sig()
        if sig is None:
            return
        
        w3 = self.account.get_w3('scroll')
        txn_data_handler = TxnDataHandler(self.account, 'scroll', w3=w3)
        txn = txn_data_handler.get_txn_data()
        txn["to"] = "0x16539E3CDc43c5b8e6De0511Aa81F6FA7248A5Eb"
        txn["data"] = "0xb510391f" + encode(["address", "bytes"], [self.account.address, bytes.fromhex(sig[2::])]).hex()
        return txn


