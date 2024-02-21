from Modules.BaseClasses.BaseAccount import BaseAccount
from Modules.config import get_rpc_list, get_general_settings
from Modules.Utils.Logger import logger
from Modules.Utils.utils import sleeping_sync
from Modules.Utils.Token import Token
import json
from eth_account import Account as ethAccount
from web3 import Web3
import random
import time
from time import sleep

class Account(BaseAccount):
    w3 = {}
    def __init__(self, private_key: str, proxy = None):
        self.private_key = private_key
        self.address = ethAccount.from_key(private_key).address
        self.formatted_hex_address = self.address
        self.proxy = proxy
        self.setup_w3(proxy=proxy)
        self.active = False
        print(self)

    def __str__(self) -> str:
        return f"private key: {self.private_key}\naddress: {self.address}\nis_active: {self.active}\nproxy: {self.proxies}\t{self.proxy}\nw3: {self.w3}"

    def is_active(self):
        return self.active

    def set_proxy(self, proxy):
        if proxy == "-" or proxy is None:
            return
        self.setup_w3(proxy)

    def setup_w3(self, proxy=None):
        rpc_list = get_rpc_list()
        if proxy == "-":
            proxy = None
        if proxy:
            req_proxy = {
                "proxies": {
                    "http"  : proxy,
                    "https" : proxy
                },
                "timeout": 10
            }
            self.proxies = req_proxy["proxies"]
            for chain in rpc_list:
                self.w3[chain] =  Web3(Web3.HTTPProvider(rpc_list[chain][0]["address"], request_kwargs=req_proxy))
        else:
            for chain in rpc_list:
                self.w3[chain] =  Web3(Web3.HTTPProvider(rpc_list[chain][0]["address"]))

    def get_w3(self, net_name):
        return self.w3[net_name]

    def get_address(self):
        return self.address
    
    def get_balance(self, token: Token):
        return token.balance_of(self.address, w3=self.get_w3(token.net_name))
    
    def wait_for_better_eth_gwei(self):
        w3 = self.w3["linea"]
        while True:
            max_gas = Web3.to_wei(float(get_general_settings()["TimeSleeps"]["max-ETH-gwei"]), 'gwei')
            try:
                gas_price = w3.eth.gas_price
                if gas_price > max_gas:
                    h_gas, h_max = Web3.from_wei(gas_price, 'gwei'), Web3.from_wei(max_gas, 'gwei')
                    logger.error(f'[{self.address}] Current gasPrice in eth: {h_gas} | Max gas price in eth: {h_max}')
                    sleeping_sync(self.address, True)
                else:
                    return round(gas_price)
                
            except Exception as error:
                logger.error(f'[{self.address}] Error: {error}')
                sleeping_sync(self.address, True)

    def send_without_wait(self, txn, net):
        self.wait_for_better_eth_gwei()
            
        w3 = self.w3[net]

        gasEstimate = w3.eth.estimate_gas(txn)

        txn['gas'] = round(gasEstimate*1.5) 
        signed_txn = w3.eth.account.sign_transaction(txn, private_key=self.private_key)
        tx_token = w3.to_hex(w3.eth.send_raw_transaction(signed_txn.rawTransaction))

        logger.success(f"[{self.address}] sending txn: {tx_token}")
        return True, signed_txn, tx_token
        
    def send_txn(self, txn, net):
        for i in range(10):
            try:
                self.wait_for_better_eth_gwei()
                w3: Web3 = self.w3[net]
                gasEstimate = w3.eth.estimate_gas(txn)
                
                txn['gas'] = round(gasEstimate*1.5) 
                signed_txn = w3.eth.account.sign_transaction(txn, private_key=self.private_key)
                tx_token = w3.to_hex(w3.eth.send_raw_transaction(signed_txn.rawTransaction))

                logger.success(f"[{self.address}] sending txn: {tx_token}")
                success = self.wait_until_txn_finished(tx_token, net)
                return success, signed_txn, tx_token
            except Exception as e:
                logger.error(f"[{self.address}] got error: {e}")
                sleeping_sync(self.address, True)
        return False, "0x0", "0x0"

    
    def wait_until_txn_finished(self, hash, net, max_time = 500):
        w3 = self.w3[net]
        start_time = time.time()
        while True:
            try:
                if time.time() - start_time > max_time:
                    logger.error(f'[{self.address}] {hash} transaction is failed (timeout)')
                    return False
                receipts = w3.eth.get_transaction_receipt(hash)
                status = receipts.get("status")

                if status == 1:
                    logger.success(f"[{self.address}] {hash} is completed")
                    return True
                elif status is None:
                    #print(f'[{hash}] still processed') #DEBUG
                    sleep(0.3)
                elif status != 1:
                    logger.error(f'[{self.address}] [{hash}] transaction is failed')
                    return False
            except:
                #print(f"[{hash}] still in progress") #DEBUG
                sleep(1)         
