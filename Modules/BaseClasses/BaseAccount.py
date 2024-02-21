from abc import ABC, abstractmethod
from web3 import Web3

class BaseAccount(ABC):
    address: str = None
    proxies = None
    @abstractmethod
    def send_txn(self, txns, net):
        """sends transaction"""
        pass
    
    @abstractmethod
    def get_w3(self, net_name) -> Web3:
        pass

    @abstractmethod
    def get_address(self):
        "returns address"
        pass

    @abstractmethod
    def get_balance(self, token):
        pass