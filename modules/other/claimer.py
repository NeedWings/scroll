from random import choice
from time import sleep
import json
import os

from web3 import Web3
from eth_abi import encode
from curl_cffi import Curl
from curl_cffi.requests import Session

from modules.utils.txn_data_handler import TxnDataHandler
from modules.utils.account import Account
from modules.utils.Logger import logger
from modules.utils.token_stor import scr
from modules.utils.utils import get_pair_for_address_from_file, req_post, sleeping_sync

def override_where():
        """ overrides certifi.core.where to return actual location of cacert.pem"""
        # change this to match the location of cacert.pem
        return os.path.abspath("data/cacert.pem")

def buff(data):
    return bytes.fromhex(data[2::])

class Claimer:

    chrome_vers = [99, 100, 101, 104, 107, 110]
    windows_versions = [7, 8, 10, 11]
    def __init__(self, account: Account) -> None:
        self.curl = Curl(cacert=override_where())
        self.vers = choice(self.chrome_vers)
        self.windows_vers = choice(self.windows_versions)
        self.account = account
        self.session = Session(curl=self.curl, impersonate = f"chrome{self.vers}")
        self.session.proxies = account.proxies
        self.session.headers = {
            "Accept": "*/*",
            "content-type": "text/plain;charset=UTF-8",
            "Accept-Encoding": "utf-8",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive",
            "Origin": "https://claim.scroll.io",
            "Referer": "https://claim.scroll.io/",
            "Sec-Ch-Ua": f'"Google Chrome";v="{self.vers}", "Chromium";v="{self.vers}", "Not?A_Brand";v="24"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": f"Mozilla/5.0 (Windows NT {self.windows_vers}.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{self.vers}.0.0.0 Safari/537.36"
        }


    def check_allocation(self):
        while True:
            try:
                next_action = "2ab5dbb719cdef833b891dc475986d28393ae963"
                resp = self.session.post("https://claim.scroll.io/", data=f'["{self.account.address}"]', headers={"next-action": next_action})
                data = resp.text.split("1:")[1]
                if data == "null\n":
                    return 0, None
                data = json.loads(data)
                allocation = int(data["amount"])
                proof = data["proof"]
                return allocation, proof
            except Exception as e:
                logger.error(f"[{self.account.address}] can't get allocation: {e}")
                sleeping_sync(self.account.address, True)

    def checker(self):
        logger.info(f"[{self.account.address}] {self.check_allocation()[0]} SCR")

    def handle(self):
        w3 = self.account.get_w3("scroll")
        txn_data_handler = TxnDataHandler(self.account, "scroll", w3=w3)

        allocation = self.check_allocation()
        if allocation[0] == 0:
            logger.info(f"[{self.account.address}] not eligble :(")
            return
        logger.info(f"[{self.account.address}] allocation is {allocation[0]/1e18} SCR")

        data = "0x3d13f874" + encode(["address", "uint256", "bytes32[]"],
                        [self.account.address, allocation[0], list(map(buff, allocation[1]))]).hex()

        txn = txn_data_handler.get_txn_data()
        txn["data"] = data
        txn["to"] = "0xE8bE8eB940c0ca3BD19D911CD3bEBc97Bea0ED62"

        self.account.send_txn(txn, "scroll")
        return
    
    def send_to_address(self):
        address = get_pair_for_address_from_file("okx_wallet_pairs.txt", self.account.address)
        if address is None:
            logger.error(f"[{self.account.address}] can't find pair in okx_wallet_pairs")
            return

        scr.transfer(self.account, address)
        
