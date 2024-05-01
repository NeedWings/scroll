import time

from eth_abi import encode

from modules.base_classes.base_account import BaseAccount
from modules.base_classes.base_defi import BaseDex
from modules.utils.token import Token   
from modules.utils.txn_data_handler import TxnDataHandler
from modules.utils.Logger import logger
from modules.utils.utils import sleeping_sync
from modules.utils.token_stor import eth, usdc, usdt
from modules.config import get_slippage, ABI


class Ambient(BaseDex):
    contract_address = "0xaaaaAAAACB71BF2C8CaE522EA5fa455571A74106"
    ABI = [{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"bytes32","name":"pool","type":"bytes32"},{"indexed":True,"internalType":"int24","name":"tick","type":"int24"},{"indexed":False,"internalType":"bool","name":"isBid","type":"bool"},{"indexed":False,"internalType":"uint32","name":"pivotTime","type":"uint32"},{"indexed":False,"internalType":"uint64","name":"feeMileage","type":"uint64"},{"indexed":False,"internalType":"uint160","name":"commitEntropy","type":"uint160"}],"name":"CrocKnockoutCross","type":"event"},{"inputs":[],"name":"acceptCrocDex","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"uint16","name":"callpath","type":"uint16"},{"internalType":"bytes","name":"cmd","type":"bytes"},{"internalType":"bool","name":"sudo","type":"bool"}],"name":"protocolCmd","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"slot","type":"uint256"}],"name":"readSlot","outputs":[{"internalType":"uint256","name":"data","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"base","type":"address"},{"internalType":"address","name":"quote","type":"address"},{"internalType":"uint256","name":"poolIdx","type":"uint256"},{"internalType":"bool","name":"isBuy","type":"bool"},{"internalType":"bool","name":"inBaseQty","type":"bool"},{"internalType":"uint128","name":"qty","type":"uint128"},{"internalType":"uint16","name":"tip","type":"uint16"},{"internalType":"uint128","name":"limitPrice","type":"uint128"},{"internalType":"uint128","name":"minOut","type":"uint128"},{"internalType":"uint8","name":"reserveFlags","type":"uint8"}],"name":"swap","outputs":[{"internalType":"int128","name":"baseQuote","type":"int128"},{"internalType":"int128","name":"quoteFlow","type":"int128"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint16","name":"callpath","type":"uint16"},{"internalType":"bytes","name":"cmd","type":"bytes"}],"name":"userCmd","outputs":[{"internalType":"bytes","name":"","type":"bytes"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint16","name":"callpath","type":"uint16"},{"internalType":"bytes","name":"cmd","type":"bytes"},{"internalType":"bytes","name":"conds","type":"bytes"},{"internalType":"bytes","name":"relayerTip","type":"bytes"},{"internalType":"bytes","name":"signature","type":"bytes"}],"name":"userCmdRelayer","outputs":[{"internalType":"bytes","name":"output","type":"bytes"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint16","name":"callpath","type":"uint16"},{"internalType":"bytes","name":"cmd","type":"bytes"},{"internalType":"address","name":"client","type":"address"}],"name":"userCmdRouter","outputs":[{"internalType":"bytes","name":"","type":"bytes"}],"stateMutability":"payable","type":"function"}]
    SWAP_ABI = ("address", "address", "uint256", "bool", "bool", "uint128", "uint16", "uint128", "uint128", "uint8")
    name = "Ambient"
    supported_tokens = ["ETH", "USDT", "USDC"]

    lpts = []

    lpt_from_tokens = {}

    tokens_from_lpt = {}

    def transform_token_position(self, token_in: Token, token_out: Token):
        priority = ["ETH", "USDC", "USDT"]
        in_prioritized = False

        for token_name in priority:
            if token_name in [token_in.symbol, token_out.symbol]:
                if token_name == token_in.symbol:
                    in_prioritized = True
                    break
                else:
                    break
        
        if in_prioritized:
            return {
                "token_in": token_in.contract_address if token_in.symbol != "ETH" else "0x0000000000000000000000000000000000000000",
                "token_out": token_out.contract_address if token_out.symbol != "ETH" else "0x0000000000000000000000000000000000000000",
                "isBuy": True,
                "isBaseQty": True,
                "limitPrice": 0xffff5433e2b3d8211706e6102aa9471,
            }
        else:
            return {
                "token_in": token_out.contract_address if token_out.symbol != "ETH" else "0x0000000000000000000000000000000000000000",
                "token_out": token_in.contract_address if token_in.symbol != "ETH" else "0x0000000000000000000000000000000000000000",
                "isBuy": False,
                "isBaseQty": False,
                "limitPrice": 65538,
            }


    def create_txn_for_swap(self, amount_in: float, token1: Token, amount_out: float, token2: Token, sender: BaseAccount, full: bool = False, native_first: bool = False):
        w3 = sender.get_w3('scroll')
        contract = w3.eth.contract(self.contract_address, abi=self.ABI)
        stable = token1.stable and token2.stable
        native_first = token1.symbol == "ETH"
        txn_data_handler = TxnDataHandler(sender, "scroll", w3=w3)

        approve_txn = token1.get_approve_txn(sender, self.contract_address, int(amount_in*10**token1.decimals), w3=w3)
        deadline = int(time.time()+3600)

        if native_first:
            value = int(amount_in*10**token1.decimals)
        else:
            value = 0

        transformed_data = self.transform_token_position(token1, token2)
        args_for_encode = (
            transformed_data["token_in"],
            transformed_data["token_out"],
            420,
            transformed_data["isBuy"],
            transformed_data["isBaseQty"],
            int(amount_in*10**token1.decimals),
            0,
            transformed_data["limitPrice"],
            int(get_slippage()*amount_out*10**token2.decimals),
            0
        )

        swap_data = encode(self.SWAP_ABI, args_for_encode)
            
        txn = contract.functions.userCmd(
            1,
            swap_data
        ).build_transaction(txn_data_handler.get_txn_data(value))
        
        return txn


    def create_txn_for_liq(self, amount1: float, token1: Token, amount2: float, token2: Token, sender: BaseAccount):
        pass

    def create_txn_for_remove_liq(self, lptoken: Token, sender: BaseAccount):
        pass
