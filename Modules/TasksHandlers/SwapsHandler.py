from Modules.Dexes.SyncSwap import SyncSwap
from Modules.Dexes.ScrollSwap import ScrollSwap
from Modules.Dexes.SpaceFi import SpaceFi
from Modules.Dexes.SkyDrome import Skydrome
from Modules.config import get_launch_settings, get_general_settings
from Modules.BaseClasses.BaseAccount import BaseAccount
from Modules.BaseClasses.BaseDeFi import BaseDex
from Modules.Utils.Token import Token
from random import shuffle
from random import choice
from Modules.Utils.token_stor import tokens, tokens_dict
from Modules.Utils.Logger import logger
from Modules.Utils.utils import get_random_value, get_random_value_int, sleeping_sync
from Modules.Utils.TokenChecker import token_checker



class SwapsHandler:

    def __init__(self, account: BaseAccount) -> None:
        self.LAUNCH_SETTINGS = get_launch_settings()
        self.GENERAL_SETTINGS = get_general_settings()
        self.supported_dexes_for_swap = []
        self.suppotred_tokens = []
        self.scroll = ScrollSwap()
        self.space = SpaceFi()
        self.sky = Skydrome()
        self.sync = SyncSwap()
        self.dexes = [self.scroll, self.space, self.sky, self.sync]
        self.account = account
        for name in self.LAUNCH_SETTINGS["Swaps"]["Dex"]:
            for dex in self.dexes:
                if dex.name == name and self.LAUNCH_SETTINGS["Swaps"]["Dex"][name]:
                    self.supported_dexes_for_swap.append(dex)
        for name in self.LAUNCH_SETTINGS["Swaps"]["SwapsTokens"]:
            if name == "WETH":
                name = "ETH"
            for token in tokens:
                if token.symbol == name and self.LAUNCH_SETTINGS["Swaps"]["SwapsTokens"][name]:
                    self.suppotred_tokens.append(token)


    def supported_tokens_str_to_token(self, tokens):
        res = []
        for token in tokens:
            res.append(tokens_dict[token])
        print(res)
        return res

    def random_swaps(self):
        amount = get_random_value_int([self.LAUNCH_SETTINGS["Swaps"]["swap-amounts-min"], self.LAUNCH_SETTINGS["Swaps"]["swaps-amounts-max"]])
        for i in range(amount):
            try:
                dex: BaseDex = choice(self.supported_dexes_for_swap)
                token1, usd_value = token_checker.get_max_valued_token(self.account, self.supported_tokens_str_to_token(dex.supported_tokens))
                if token1 == None:
                    logger.error(f"[{self.account.get_address()}] all balances is 0")
                    continue
                token1: Token = token1
                token2: Token = tokens_dict[dex.get_pair_for_token(token1.symbol)]
                
                amount_to_swap = usd_value * get_random_value([self.LAUNCH_SETTINGS["Swaps"]["swaps-percent-min"], self.LAUNCH_SETTINGS["Swaps"]["swaps-percent-max"]])
                
                token1_val = amount_to_swap/token1.get_price()
                token2_val = amount_to_swap/token2.get_price()
                logger.info(f"[{self.account.get_address()}] going to swap {token1_val} {token1.symbol} for {token2.symbol} in {dex.name}")
                swap_txn = dex.create_txn_for_swap(token1_val, token1, token2_val, token2, self.account)
                if swap_txn == 5555:
                    sleeping_sync(self.account.get_address(), True)
                    continue

                self.account.send_txn(swap_txn, "scroll")
                sleeping_sync(self.account.get_address())

            except Exception as e:
                logger.error(f"[{self.account.get_address()}] got erroor: {e}")
                sleeping_sync(self.account.get_address(), True)

    def save_assets(self, to="ETH"):
        token = tokens_dict[to]
        tokens_for_swap = self.suppotred_tokens.copy() 
        shuffle(tokens_for_swap)
        for token_to_swap in tokens_for_swap:
            try:
                token_to_swap: Token
                if token == token_to_swap:
                    continue

                balance = self.account.get_balance(token_to_swap)[0]

                if token_to_swap.symbol == "ETH":
                    balance -= int(get_random_value([self.GENERAL_SETTINGS["TimeSleeps"]["save-eth-amount-min"], self.GENERAL_SETTINGS["TimeSleeps"]["save-eth-amount-max"]])*1e18)

                if balance <= 0:
                    logger.info(f"[{self.account.get_address()}] {token_to_swap.symbol} balance 0 or less MinTokensBalances. skip")
                    continue
                selected = False
                for i in range(10):
                    dex: BaseDex = choice(self.supported_dexes_for_swap)
                    if token_to_swap.symbol in dex.supported_tokens:
                        selected = True
                        break
                
                if not selected:
                    logger.error(f"[{self.account.get_address()}] can't find dex for {token_to_swap.symbol}")
                    continue

                usd_val = token_to_swap.get_usd_value(balance/10**token_to_swap.decimals)

                amount_out = usd_val/token.get_price()
                logger.info(f"[{self.account.get_address()}] going to swap {balance/10**token_to_swap.decimals} {token_to_swap.symbol} for {token.symbol} in {dex.name}")

                
                swap_txn = dex.create_txn_for_swap(balance/10**token_to_swap.decimals, token_to_swap, amount_out, token, self.account, full = True)
                if swap_txn != 5555:
                    self.account.send_txn(swap_txn, "scroll")
                    sleeping_sync(self.account.get_address())

            except Exception as e:
                logger.error(f"[{self.account.get_address()}] got error: {e}")
                sleeping_sync(self.account.get_address(), True)
        