from random import shuffle, choice

from modules.lends.layer_bank import LayerBank
from modules.base_classes.base_account import BaseAccount
from modules.base_classes.base_defi import BaseLend
from modules.utils.token import Token
from modules.utils.token_stor import tokens, tokens_dict, eth
from modules.utils.Logger import logger
from modules.utils.utils import get_random_value, get_random_value_int, sleeping_sync
from modules.utils.token_checker import token_checker
from modules.config import SETTINGS



class LendingHandler:
    def __init__(self, account: BaseAccount) -> None:
        
        self.layer_bank = LayerBank()

    
        self.lends = [self.layer_bank]
        self.supported_dexes_for_lend = []

        for name in self.SETTINGS["Lendings"]:
            for lend in self.lends:
                if lend.name == name:
                    self.supported_dexes_for_lend.append(lend)
        self.account = account

    def supported_tokens_str_to_token(self, tokens):
        res = []
        for token in tokens:
            res.append(tokens_dict[token])

        return res
    
    def add_to_lend(self):
        add_times = get_random_value_int(SETTINGS["Add To Lend Times"])
        lend: BaseLend = choice(self.supported_dexes_for_lend)
        for i in range(add_times):
            try:
                token, usd_value = token_checker.get_max_valued_token(self.account, self.supported_tokens_str_to_token(lend.supported_tokens))
                balance, human_balance = self.account.get_balance(token)
                availible_balance = human_balance

                if availible_balance > 0:
                    add_amount = availible_balance * get_random_value(SETTINGS["Add To Lend Percent"])
                    logger.info(f"[{self.account.address}] going to add {add_amount} {token.symbol} to {lend.name}")
                    txn = lend.create_txn_for_adding_token(token, add_amount, self.account)
                    self.account.send_txn(txn, "scroll")
                    sleeping_sync(self.account.address)
                    
            except Exception as e:
                logger.error(f"[{self.account.get_address()}] got erroor: {e}")
                sleeping_sync(self.account.get_address(), True)

    def remove_from_lend(self):
        for lend in self.supported_dexes_for_lend.copy():
            for lend_token in lend.lend_tokens:
                try:
                    balance, human_balance = self.account.get_balance(lend_token)
                    if balance > 10000:
                        logger.info(f"[{self.account.address}] going to remove {lend_token.symbol} from {lend.name}")
                        txn = lend.create_txn_for_removing_token(lend_token, self.account)
                        if txn == -1:
                            sleeping_sync(self.account.address, True)
                            continue
                        self.account.send_txn(txn, "scroll")
                        sleeping_sync(self.account.address)
                    else:
                        logger.info(f"[{self.account.address}] {lend_token.symbol} balance is 0. Skip")

                        
                except Exception as e:
                    logger.error(f"[{self.account.get_address()}] got erroor: {e}")
                    sleeping_sync(self.account.get_address(), True)

    def borrow(self):
        
        for _ in range(get_random_value_int(SETTINGS["Borrow Times"])):
            lend = choice(self.supported_dexes_for_lend)
            tokens = self.supported_tokens_str_to_token(lend.supported_tokens_for_borrow)
            try:
                token: Token = choice(tokens)

                max_to_borrow = lend.how_many_can_borrow(self.account)
                if max_to_borrow <= 0:
                    logger.error(f"[{self.account.address}] max to borrow is 0")
                    continue
                to_borrow = max_to_borrow*get_random_value(SETTINGS["Borrow Percent"])

                to_borrow = to_borrow/lend.get_price(lend.lend_token_from_token[token.symbol], self.account)
                logger.info(f"[{self.account.address}] going to borrow {to_borrow/1e18} {token.symbol}")
                txn = lend.create_txn_to_borrow_token(to_borrow/1e18, token, self.account)
                if txn == -1:
                    sleeping_sync(self.account.address, True)
                    continue
                self.account.send_txn(txn, "scroll")
                sleeping_sync(self.account.address)
            except Exception as e:
                logger.error(f"[{self.account.address}] got error: {e}")
                sleeping_sync(self.account.address, True)

    def repay(self):
        lends = self.supported_dexes_for_lend.copy()
        shuffle(lends)
        for lend in lends:
            tokens = self.supported_tokens_str_to_token(lend.supported_tokens_for_borrow).copy()
            shuffle(tokens)
            for token in tokens:
                try:
                    txn = lend.create_txn_to_repay_token(token, self.account)
                    if txn == -1:
                        continue
                    self.account.send_txn(txn, "scroll")
                    sleeping_sync(self.account.address)
                except Exception as e:
                    logger.error(f"[{self.account.address}] got error: {e}")
                    sleeping_sync(self.account.address, True)
