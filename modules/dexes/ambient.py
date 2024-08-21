import time
from math import log, sqrt

from web3.contract.contract import Contract
from eth_abi import encode

from modules.base_classes.base_account import BaseAccount
from modules.base_classes.base_defi import BaseDex
from modules.utils.token import Token   
from modules.utils.q_number import QNumber
from modules.utils.txn_data_handler import TxnDataHandler
from modules.utils.Logger import logger
from modules.utils.utils import sleeping_sync, get_random_value, req
from modules.utils.token import AmbientV3Position
from modules.utils.token_stor import eth, usdc, usdt, token_from_contract
from modules.config import get_slippage, ABI, SETTINGS


class Ambient(BaseDex):
    contract_address = "0xaaaaAAAACB71BF2C8CaE522EA5fa455571A74106"
    quote_address = "0x62223e90605845Cf5CC6DAE6E0de4CDA130d6DDf"
    ABI = [{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"bytes32","name":"pool","type":"bytes32"},{"indexed":True,"internalType":"int24","name":"tick","type":"int24"},{"indexed":False,"internalType":"bool","name":"isBid","type":"bool"},{"indexed":False,"internalType":"uint32","name":"pivotTime","type":"uint32"},{"indexed":False,"internalType":"uint64","name":"feeMileage","type":"uint64"},{"indexed":False,"internalType":"uint160","name":"commitEntropy","type":"uint160"}],"name":"CrocKnockoutCross","type":"event"},{"inputs":[],"name":"acceptCrocDex","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"uint16","name":"callpath","type":"uint16"},{"internalType":"bytes","name":"cmd","type":"bytes"},{"internalType":"bool","name":"sudo","type":"bool"}],"name":"protocolCmd","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"slot","type":"uint256"}],"name":"readSlot","outputs":[{"internalType":"uint256","name":"data","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"base","type":"address"},{"internalType":"address","name":"quote","type":"address"},{"internalType":"uint256","name":"poolIdx","type":"uint256"},{"internalType":"bool","name":"isBuy","type":"bool"},{"internalType":"bool","name":"inBaseQty","type":"bool"},{"internalType":"uint128","name":"qty","type":"uint128"},{"internalType":"uint16","name":"tip","type":"uint16"},{"internalType":"uint128","name":"limitPrice","type":"uint128"},{"internalType":"uint128","name":"minOut","type":"uint128"},{"internalType":"uint8","name":"reserveFlags","type":"uint8"}],"name":"swap","outputs":[{"internalType":"int128","name":"baseQuote","type":"int128"},{"internalType":"int128","name":"quoteFlow","type":"int128"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint16","name":"callpath","type":"uint16"},{"internalType":"bytes","name":"cmd","type":"bytes"}],"name":"userCmd","outputs":[{"internalType":"bytes","name":"","type":"bytes"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint16","name":"callpath","type":"uint16"},{"internalType":"bytes","name":"cmd","type":"bytes"},{"internalType":"bytes","name":"conds","type":"bytes"},{"internalType":"bytes","name":"relayerTip","type":"bytes"},{"internalType":"bytes","name":"signature","type":"bytes"}],"name":"userCmdRelayer","outputs":[{"internalType":"bytes","name":"output","type":"bytes"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint16","name":"callpath","type":"uint16"},{"internalType":"bytes","name":"cmd","type":"bytes"},{"internalType":"address","name":"client","type":"address"}],"name":"userCmdRouter","outputs":[{"internalType":"bytes","name":"","type":"bytes"}],"stateMutability":"payable","type":"function"}]
    SWAP_ABI = ("address", "address", "uint256", "bool", "bool", "uint128", "uint16", "uint128", "uint128", "uint8")
    ADD_LP_ABI = ("uint8", "address", "address", "uint256", "int24", "int24", "uint128", "uint128", "uint128", "uint8", "address")
    name = "Ambient"
    supported_tokens = ["ETH", "USDT", "USDC", "WRSETH", "WSTETH"]
    supported_liq_tokens  = ["ETH", "USDT", "USDC", "WRSETH", "WSTETH"]
    #base_prices = {
    #    "ETH-USDC": 1.2337912104734611e-05,
    #    "ETH-USDT": 1.224518807519506e-05,
    #    "USDC-USDT": 1
    #}



    def lpts(self, user: BaseAccount) -> list:
        resp = req(f"https://ambindexer.net/scroll-gcgo/user_positions?user={user.address}&chainId=0x82750&ensResolution=true&annotate=true&omitKnockout=true&addValue=true", proxies = user.proxies)
        positions = resp["data"]
        lpts = []

        for position in positions:
            token1 = position["base"]
            token2 = position["quote"]
            bid_tick = position["bidTick"]
            ask_tick = position["askTick"]
            is_ambient = position["positionType"] == "ambient"
            opened = position["concLiq"] > 0 or position["ambientLiq"] > 0
            liq_amount = position["concLiq"]
            lpts.append(AmbientV3Position(f"{token_from_contract[token1].symbol}-{token_from_contract[token2].symbol}",token1, token2, bid_tick, ask_tick, liq_amount, is_ambient, opened))
        
        return lpts

    lpt_from_tokens = {}

    tokens_from_lpt = {}

    def transform_tokens_for_removing(self, token_in: Token, token_out: Token):
        priority = ["ETH", "USDC", "WRSETH", "USDT", "WSTETH"]
        in_prioritized = False

        for token_name in priority:
            if token_name in [token_in.symbol, token_out.symbol]:
                if token_name == token_in.symbol:
                    name = f"{token_in.symbol}-{token_out.symbol}"
                    in_prioritized = True
                    break
                else:
                    name = f"{token_out.symbol}-{token_in.symbol}"
                    break

        slippage = get_slippage()

        token1_price = token_in.get_price()
        token2_price = token_out.get_price()
        current_spot_price = (token1_price*10**token_out.decimals)/(token2_price*10**token_in.decimals)
        if in_prioritized:
            current_spot_price = 1/current_spot_price
        current_tick = int(log(current_spot_price, 1.0001))
        current_tick = int(current_tick/4) * 4

        sqrt_price = sqrt(1.0001**current_tick)
        limitLower = QNumber.from_float(sqrt_price*0.9, 64, 64).value
        limitUpper = QNumber.from_float(sqrt_price*1.1, 64, 64).value


        if in_prioritized:
            return {
                "token_in": token_in.contract_address if token_in.symbol != "ETH" else "0x0000000000000000000000000000000000000000",
                "token_out": token_out.contract_address if token_out.symbol != "ETH" else "0x0000000000000000000000000000000000000000",
                "limitLower": limitLower,
                "limitUpper": limitUpper
            }
        else:
            return {
                "token_in": token_out.contract_address if token_out.symbol != "ETH" else "0x0000000000000000000000000000000000000000",
                "token_out": token_in.contract_address if token_in.symbol != "ETH" else "0x0000000000000000000000000000000000000000",
                "limitLower": limitLower,
                "limitUpper": limitUpper
            }


    def transform_tokens_for_adding(self, token_in: Token, token_out: Token, current_tick: int):
        priority = ["ETH", "USDC", "WRSETH", "USDT", "WSTETH"]
        in_prioritized = False

        for token_name in priority:
            if token_name in [token_in.symbol, token_out.symbol]:
                if token_name == token_in.symbol:
                    name = f"{token_in.symbol}-{token_out.symbol}"
                    in_prioritized = True
                    break
                else:
                    name = f"{token_out.symbol}-{token_in.symbol}"
                    break

        range = get_random_value(SETTINGS["V3 Liq Range"])
        if SETTINGS["Low range for stables"]:
            if token_in.stable and token_out.stable:
                range = get_random_value([0.0004, 0.0006])
        full = range == 1
        code = 31 if full else 11
        slippage = get_slippage()

        token1_price = token_in.get_price()
        token2_price = token_out.get_price()
        current_tick = int(current_tick/4) * 4
        print(current_tick)
        sqrt_price = sqrt(1.0001**current_tick)

        limitLower = QNumber.from_float(sqrt_price*0.6, 64, 64).value
        limitUpper = QNumber.from_float(sqrt_price*1.4, 64, 64).value

        if full:
            bidTick = 0
            askTick = 0
        else:

            bidTick = current_tick-int(10000*range)
            askTick = current_tick+int(10000*range)

            bidTick = int(bidTick/4) * 4
            askTick = int(askTick/4) * 4
            


        if in_prioritized:
            return {
                "code": code,
                "token_in": token_in.contract_address if token_in.symbol != "ETH" else "0x0000000000000000000000000000000000000000",
                "token_out": token_out.contract_address if token_out.symbol != "ETH" else "0x0000000000000000000000000000000000000000",
                "bidTick": bidTick,
                "askTick": askTick,
                "limitLower": limitLower,
                "limitUpper": limitUpper,
                "prioritized": in_prioritized
            }
        else:
            return {
                "code": code,
                "token_in": token_out.contract_address if token_out.symbol != "ETH" else "0x0000000000000000000000000000000000000000",
                "token_out": token_in.contract_address if token_in.symbol != "ETH" else "0x0000000000000000000000000000000000000000",
                "bidTick": bidTick,
                "askTick": askTick,
                "limitLower": limitLower,
                "limitUpper": limitUpper,
                "prioritized": in_prioritized
            }

    def transform_token_position(self, token_in: Token, token_out: Token):
        priority = ["ETH", "USDC", "WRSETH", "USDT", "WSTETH"]
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

    def get_current_tick(self, token1: Token, token2: Token, sender: BaseAccount):
        priority = ["ETH", "USDC", "WRSETH", "USDT", "WSTETH"]
        in_prioritized = False
        w3 = sender.get_w3("scroll")

        contract: Contract = w3.eth.contract(self.quote_address, abi=[{"inputs":[{"internalType":"address","name":"base","type":"address"},{"internalType":"address","name":"quote","type":"address"},{"internalType":"uint256","name":"poolIdx","type":"uint256"}],"name":"queryCurveTick","outputs":[{"internalType":"int24","name":"","type":"int24"}],"stateMutability":"view","type":"function"}])

        for token_name in priority:
            if token_name in [token1.symbol, token2.symbol]:
                if token_name == token1.symbol:
                    name = f"{token1.symbol}-{token2.symbol}"
                    in_prioritized = True
                    break
                else:
                    name = f"{token2.symbol}-{token1.symbol}"
                    break
        if in_prioritized:
            data = contract.functions.queryCurveTick(
                token1.contract_address if token1.symbol != "ETH" else "0x0000000000000000000000000000000000000000",
                token2.contract_address if token2.symbol != "ETH" else "0x0000000000000000000000000000000000000000",
                420
            ).call()
        else:
            data = contract.functions.queryCurveTick(
                token2.contract_address if token2.symbol != "ETH" else "0x0000000000000000000000000000000000000000",
                token1.contract_address if token1.symbol != "ETH" else "0x0000000000000000000000000000000000000000",
                420
            ).call()
        return data
        

    def create_txn_for_swap(self, amount_in: float, token1: Token, amount_out: float, token2: Token, sender: BaseAccount, full: bool = False, native_first: bool = False):
        w3 = sender.get_w3('scroll')
        contract = w3.eth.contract(self.contract_address, abi=self.ABI)
        native_first = token1.symbol == "ETH"
        txn_data_handler = TxnDataHandler(sender, "scroll", w3=w3)

        approve_txn = token1.get_approve_txn(sender, self.contract_address, int(amount_in*10**token1.decimals), w3=w3)

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
        tick = self.get_current_tick(token1, token2, sender)
        w3 = sender.get_w3('scroll')
        contract = w3.eth.contract(self.contract_address, abi=self.ABI)
        txn_data_handler = TxnDataHandler(sender, "scroll", w3=w3)

        approve_txn = token1.get_approve_txn(sender, self.contract_address, int(2*amount1*10**token1.decimals), w3=w3)
        approve2_txn = token2.get_approve_txn(sender, self.contract_address, int(2*amount2*10**token2.decimals), w3=w3)

        if "ETH" in [token1.symbol, token2.symbol]:
            if token1.symbol == "ETH":
                value = int(amount1*10**token1.decimals)
            else:
                value = int(amount2*10**token2.decimals)
        else:
            value = 0

        transformed_data = self.transform_tokens_for_adding(token1, token2, tick)
        if transformed_data["prioritized"]:
            amount = amount1*get_slippage()*10**token1.decimals
        else:
            amount = amount2*get_slippage()*10**token2.decimals
        args_for_encode = (
            transformed_data["code"],
            transformed_data["token_in"],
            transformed_data["token_out"],
            420,
            transformed_data["bidTick"],
            transformed_data["askTick"],
            int(amount),
            transformed_data["limitLower"],
            transformed_data["limitUpper"],
            0,
            "0x0000000000000000000000000000000000000000"
        )

        swap_data = encode(self.ADD_LP_ABI, args_for_encode)

        txn = contract.functions.userCmd(
            128,
            swap_data
        ).build_transaction(txn_data_handler.get_txn_data(value))

        return txn

    def create_txn_for_remove_liq(self, lptoken: AmbientV3Position, sender: BaseAccount):
        w3 = sender.get_w3('scroll')
        contract = w3.eth.contract(self.contract_address, abi=self.ABI)
        txn_data_handler = TxnDataHandler(sender, "scroll", w3=w3)

        token1 = token_from_contract[lptoken.token1]
        token2 = token_from_contract[lptoken.token2]

        transformed_data = self.transform_tokens_for_removing(token1, token2)
        args_for_encode = (
            4 if lptoken.is_ambient else 2,
            transformed_data["token_in"],
            transformed_data["token_out"],
            420,
            lptoken.bid_tick,
            lptoken.ask_tick,
            0xffffffffffffffffffffffffffffffff if lptoken.is_ambient else lptoken.liq_amount,
            transformed_data["limitLower"],
            transformed_data["limitUpper"],
            0,
            "0x0000000000000000000000000000000000000000"
        )

        swap_data = encode(self.ADD_LP_ABI, args_for_encode)
        txn = contract.functions.userCmd(
            128,
            swap_data
        ).build_transaction(txn_data_handler.get_txn_data())

        return txn
