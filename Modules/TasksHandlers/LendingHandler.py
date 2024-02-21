from Modules.Lends.LineaBank import LineaBank
from Modules.Lends.Velocore import Velocore
from Modules.config import get_general_settings, get_launch_settings
from Modules.BaseClasses.BaseAccount import BaseAccount
from Modules.BaseClasses.BaseDeFi import BaseLend
from Modules.Utils.Token import Token
from random import shuffle
from random import choice
from Modules.Utils.token_stor import tokens, tokens_dict, eth
from Modules.Utils.Logger import logger
from Modules.Utils.utils import get_random_value, get_random_value_int, sleeping_sync
from Modules.Utils.TokenChecker import token_checker



class LendingHandler:
    def __init__(self, account: BaseAccount) -> None:
        
        self.linea_bank = LineaBank()
        self.velocore = Velocore()

        self.LAUNCH_SETTINGS = get_launch_settings()
        self.GENERAL_SETTINGS = get_general_settings()

        self.lends = [self.linea_bank, self.velocore]
        self.supported_dexes_for_lend = []

        for name in self.LAUNCH_SETTINGS["Lendings"]["Lends"]:
            for lend in self.lends:
                if lend.name == name and self.LAUNCH_SETTINGS["Lendings"]["Lends"][name]:
                    self.supported_dexes_for_lend.append(lend)
        self.account = account

    def supported_tokens_str_to_token(self, tokens):
        res = []
        for token in tokens:
            res.append(tokens_dict[token])

        return res
    
    def add_to_lend(self):
        add_times = get_random_value_int([self.LAUNCH_SETTINGS["Lendings"]["add-to-lend-times-min"], self.LAUNCH_SETTINGS["Lendings"]["add-to-lend-times-max"]])
        lend: BaseLend = choice(self.supported_dexes_for_lend)
        for i in range(add_times):
            try:
                token, usd_value = token_checker.get_max_valued_token(self.account, self.supported_tokens_str_to_token(lend.supported_tokens))
                balance, human_balance = self.account.get_balance(token)
                availible_balance = human_balance - get_random_value([self.GENERAL_SETTINGS["TimeSleeps"]['save-eth-amount-min'], self.GENERAL_SETTINGS["TimeSleeps"]['save-eth-amount-max']])

                if availible_balance > 0:
                    add_amount = round(availible_balance*10**token.decimals * get_random_value([self.LAUNCH_SETTINGS["Lendings"]["add-to-lend-percent-min"], self.LAUNCH_SETTINGS["Lendings"]["add-to-lend-percent-max"]]))
                    logger.info(f"[{self.account.address}] going to add {add_amount/10**token.decimals} {token.symbol} to {lend.name}")
                    txn = lend.create_txn_for_adding_token(token, add_amount/10**token.decimals, self.account)
                    self.account.send_txn(txn, "scroll")
                    sleeping_sync(self.account.address)
                    
            except Exception as e:
                logger.error(f"[{self.account.get_address()}] got erroor: {e}")
                sleeping_sync(self.account.get_address(), True)

    def remove_from_lend(self):
        for lend in self.supported_dexes_for_lend.copy():
            for lend_token in lend.lend_tokens:
                try:
                    if lend.name != "Velocore":
                        balance, human_balance = self.account.get_balance(lend_token)
                    else:
                        balance = 123123123
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
        tokens = self.supported_tokens_str_to_token(self.linea_bank.supported_tokens_for_borrow)
        print(tokens)
        for _ in range(get_random_value_int([self.LAUNCH_SETTINGS["Lendings"]["borrow-times-min"], self.LAUNCH_SETTINGS["Lendings"]["borrow-times-max"]])):
            try:
                token: Token = choice(tokens)

                max_to_borrow = self.linea_bank.how_many_can_borrow(self.account)
                if max_to_borrow <= 0:
                    logger.error(f"[{self.account.address}] max to borrow is 0")
                    continue
                to_borrow = max_to_borrow*get_random_value([self.LAUNCH_SETTINGS["Lendings"]["borrow-percent-min"], self.LAUNCH_SETTINGS["Lendings"]["borrow-percent-max"]])

                to_borrow = to_borrow/self.linea_bank.get_price(self.linea_bank.lend_token_from_token[token.symbol], self.account)
                logger.info(f"[{self.account.address}] going to borrow {to_borrow/1e18} {token.symbol}")
                txn = self.linea_bank.create_txn_to_borrow_token(to_borrow/1e18, token, self.account)
                if txn == -1:
                    sleeping_sync(self.account.address, True)
                    continue
                self.account.send_txn(txn, "scroll")
                sleeping_sync(self.account.address)
            except Exception as e:
                logger.error(f"[{self.account.address}] got error: {e}")
                sleeping_sync(self.account.address, True)

    def repay(self):
        tokens = self.supported_tokens_str_to_token(self.linea_bank.supported_tokens_for_borrow).copy()
        shuffle(tokens)
        for token in tokens:
            try:
                txn = self.linea_bank.create_txn_to_repay_token(token, self.account)
                if txn == -1:
                    continue
                self.account.send_txn(txn, "scroll")
                sleeping_sync(self.account.address)
            except Exception as e:
                logger.error(f"[{self.account.address}] got error: {e}")
