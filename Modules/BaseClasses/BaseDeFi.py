from abc import ABC, abstractmethod
from Modules.config import get_launch_settings
from Modules.Utils.utils import param_to_list_selected
from Modules.Utils.Token import Token
from Modules.BaseClasses.BaseAccount import BaseAccount
from Modules.Utils.Logger import logger
import random

class BaseDex(ABC):
    name = None
    supported_tokens = []
    lpts = []
    contract_address_lp = None
    def __init__(self) -> None:
        new_supported_tokens = []
        settings = get_launch_settings()
        selected_tokens = param_to_list_selected(settings["Swaps"]["SwapsTokens"])
        print(selected_tokens)
        for token in self.supported_tokens:
            if token in selected_tokens or ("WETH" in selected_tokens and token == "ETH"):
                new_supported_tokens.append(token)
        self.supported_tokens = new_supported_tokens

    @abstractmethod
    def create_txn_for_swap(self, amount_in: float, token1: Token, amount_out: float, token2: Token, sender: BaseAccount, full: bool = False):
        pass

    @abstractmethod
    def create_txn_for_liq(self, amount1: float, token1: Token, amount2: float, token2: Token, sender: BaseAccount):
        pass

    @abstractmethod
    def create_txn_for_remove_liq(self, lptoken: Token, sender: BaseAccount):
        pass

    def get_pair_for_token(self, token: str):
        for i in range(20):
            pair = random.choice(self.supported_tokens)
            if token != pair:
                return pair
        logger.error("Can't find pair for token")
        return -5
    
class BaseLend(ABC):
    contract_address = None
    name = None
    supported_tokens = []
    supported_tokens_for_borrow = []
    lend_tokens = []

    def __init__(self) -> None:
        new_supported_tokens = []
        settings = get_launch_settings()
        selected_tokens = param_to_list_selected(settings["Lendings"]["LendTokens"])
        for token in self.supported_tokens:
            if token in selected_tokens or ("WETH" in selected_tokens and token == "ETH"):
                new_supported_tokens.append(token)
        self.supported_tokens = new_supported_tokens

        new_supported_tokens_for_borrow = []
        for token in self.supported_tokens_for_borrow:
            if token in selected_tokens or ("WETH" in selected_tokens and token == "ETH"):
                new_supported_tokens_for_borrow.append(token)
        self.supported_tokens_for_borrow = new_supported_tokens_for_borrow

    @abstractmethod
    def create_txn_for_adding_token(self, token: Token, amount: float, sender: BaseAccount):
        pass

    @abstractmethod
    def create_txn_for_removing_token(self, token: Token, sender: BaseAccount):
        pass


