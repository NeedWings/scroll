import random

from web3 import Web3

from modules.config import get_rpc_list, get_launch_settings, get_general_settings
from modules.utils.Logger import logger
from modules.utils.utils import sleeping_sync

class TxnDataHandler:
      
    def __init__(self, sender, net_name, w3 = None) -> None:
        self.address = sender.get_address()
        self.net_name = net_name
        if w3:
            self.w3 = w3
        else:
            self.w3 = Web3(Web3.HTTPProvider(get_rpc_list()[net_name][0]["address"]))
    
    def get_gas_price(self):
        
        max_gas = Web3.to_wei(float(get_general_settings()["max-gwei"].get(self.net_name)), 'gwei')

        while True:
            try:
                gas_price = self.w3.eth.gas_price
                if gas_price > max_gas:
                    h_gas, h_max = Web3.from_wei(gas_price, 'gwei'), Web3.from_wei(max_gas, 'gwei')
                    logger.error(f'[{self.address}] Sender net: {self.net_name}. Current gasPrice: {h_gas} | Max gas price: {h_max}')
                    sleeping_sync(f'[{self.address}] Waiting best gwei. Update after ')
                else:
                    return round(gas_price)
                
            except Exception as error:
                logger.error(f'[{self.address}] Error: {error}')
                sleeping_sync(f'[{self.address}] Error fault. Update after ')


    def get_txn_data(self, value=0):
        gas_price = self.get_gas_price()


        data = {
            'chainId': self.w3.eth.chain_id, 
            'nonce': self.w3.eth.get_transaction_count(self.address),  
            'from': self.address, 
            "value": value
        }


        if self.net_name in ["avalanche", "polygon", "arbitrum", "ethereum", "base", "optimism", "linea"]:
            data["type"] = "0x2"
            data["maxFeePerGas"] = gas_price
            if self.net_name == "polygon":
                data["maxPriorityFeePerGas"] = Web3.to_wei(30, "gwei")
            elif self.net_name == "avalanche" or self.net_name == "base" or self.net_name == "optimism" or self.net_name == "linea":
                data["maxPriorityFeePerGas"] = gas_price
            elif self.net_name == "ethereum":
                data["maxPriorityFeePerGas"] = Web3.to_wei(0.05, "gwei")
            elif self.net_name == "arbitrum":
                data["maxPriorityFeePerGas"] = Web3.to_wei(0.01, "gwei")
        else:
            data["gasPrice"] = gas_price


           
        
    
        return data