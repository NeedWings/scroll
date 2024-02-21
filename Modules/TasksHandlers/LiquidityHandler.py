from Modules.Dexes.SyncSwap import SyncSwap
from Modules.Dexes.ScrollSwap import ScrollSwap
from Modules.Dexes.SpaceFi import SpaceFi
from Modules.Dexes.SkyDrome import Skydrome
from Modules.Dexes.SyncSwap import SyncSwap
from Modules.config import get_launch_settings, get_general_settings, get_slippage
from Modules.BaseClasses.BaseAccount import BaseAccount
from Modules.BaseClasses.BaseDeFi import BaseDex
from Modules.Utils.Token import Token
from random import shuffle
from random import choice
from Modules.Utils.token_stor import tokens, tokens_dict
from Modules.Utils.Logger import logger
from Modules.Utils.utils import get_random_value, get_random_value_int, sleeping_sync
from Modules.Utils.TokenChecker import token_checker

short_names = {
    "EchoDex": 'echo',
    "SyncSwap": 'sync',
    "LineaSwap": "linea",
    "LeetSwap": "leet"
}


class LiquidityHandler:
    def __init__(self, account: BaseAccount) -> None:
        self.scroll = ScrollSwap()
        self.space = SpaceFi()
        self.sky = Skydrome()

        self.liq_dexes = [self.scroll, self.space, self.sky]

        self.supported_dexes_for_liq = []
        

        self.LAUNCH_SETTINGS = get_launch_settings()
        self.GENERAL_SETTINGS = get_general_settings()

        for name in self.LAUNCH_SETTINGS["Liquidity"]["LiquidityDexes"]:
            for dex in self.liq_dexes:
                if dex.name == name and self.LAUNCH_SETTINGS["Liquidity"]["LiquidityDexes"][name]:
                    self.supported_dexes_for_liq.append(dex)
        self.account = account

    def supported_tokens_str_to_token(self, tokens):
        res = []
        for token in tokens:
            res.append(tokens_dict[token])

        return res
    
    def add_liquidity(self):
        liq_amount = get_random_value_int([self.LAUNCH_SETTINGS["Liquidity"]["add-liquidity-amounts-min"], self.LAUNCH_SETTINGS["Liquidity"]["add-liquidity-amounts-max"]])
        if liq_amount < 1:
            return
        
        for i in range(liq_amount):
            try:
                dex: BaseDex = choice(self.supported_dexes_for_liq)
                token1, usd_value = token_checker.get_max_valued_token(self.account, self.supported_tokens_str_to_token(dex.supported_tokens))
                if token1 == None:
                    logger.error(f"[{self.account.get_address()}] all balances is 0")
                    continue
                token1: Token = token1
                token2 = dex.get_pair_for_token(token1.symbol)

                if token2 == -5:
                    continue
                token2: Token = tokens_dict[token2]
                amount_to_add = usd_value * get_random_value([self.LAUNCH_SETTINGS["Liquidity"]["liquidity-percent-min"], self.LAUNCH_SETTINGS["Liquidity"]["liquidity-percent-max"]])/2
                token2_usd_value = token2.get_usd_value(self.account.get_balance(token2)[1])
                amount1 = amount_to_add/token1.get_price()
                amount2 = amount_to_add/token2.get_price()
                logger.info(f"[{self.account.get_address()}] going to add liquidity in {dex.name} in {token1.symbol}/{token2.symbol} pair for {amount1} {token1.symbol} and {amount2} {token2.symbol}")
                
                if token2_usd_value < amount_to_add*(2-get_slippage()+0.01):
                    logger.info(f"[{self.account.get_address()}] not enough second token for adding, will make swap")
                    
                    amount_to_swap = amount_to_add*(2-get_slippage()+0.01) - token2_usd_value
                    token1_amount_to_swap = amount_to_swap/token1.get_price()
                    amount_out = amount_to_swap/token2.get_price()
                    
                    logger.info(f"[{self.account.get_address()}] going to swap {token1_amount_to_swap} {token1.symbol} for {token2.symbol} in {dex.name}")
                    
                    swap_txn = dex.create_txn_for_swap(token1_amount_to_swap, token1, amount_out, token2, self.account)

                    if swap_txn == 5555:
                        logger.error(f"[{self.account.get_address()}] can't create txn for swap")
                        sleeping_sync(self.account.get_address(), True)
                        continue

                    if (self.account.send_txn(swap_txn, "scroll")) == 5555:
                        continue
                    sleeping_sync(self.account.get_address())
                liq_txn = dex.create_txn_for_liq(amount1, token1, amount2, token2, self.account)
                if liq_txn == 5555:
                    sleeping_sync(self.account.get_address(), True)
                    continue

                self.account.send_txn(liq_txn, "scroll")
                sleeping_sync(self.account.get_address())

            except Exception as e:
                logger.error(f"[{self.account.get_address()}] got erroor: {e}")
                sleeping_sync(self.account.get_address(), True)

    def remove_liquidity(self):
        dexes = self.supported_dexes_for_liq.copy()
        shuffle(dexes)
        for dex in dexes:
            dex: BaseDex
            lptokens = dex.lpts.copy()
            shuffle(lptokens)
            for lpt in lptokens:
                try:
                    lpt: Token
                    
                    if lpt.contract_address == "0x0000000000000000000000000000000000000000":
                        logger.info(f"[{self.account.get_address()}] {lpt.symbol} pool value is 0. Skip")
                        continue

                    balance = self.account.get_balance(lpt)[1]

                    if balance <= 0:
                        logger.info(f"[{self.account.get_address()}] {lpt.symbol} pool value is 0. Skip")
                        continue
                    logger.info(f"[{self.account.get_address()}] going to remove {lpt.symbol} from {dex.name}")
                    txn = dex.create_txn_for_remove_liq(lpt, self.account)

                    if txn == 5555:
                        continue
                    self.account.send_txn(txn, "scroll")
                    sleeping_sync(self.account.get_address())
                except Exception as e:
                    logger.error(f"[{self.account.get_address()}] got erroor: {e}")
                    sleeping_sync(self.account.get_address(), True)
    
