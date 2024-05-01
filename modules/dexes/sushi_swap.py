import time

from modules.base_classes.base_account import BaseAccount
from modules.base_classes.base_defi import BaseDex
from modules.utils.token import Token   
from modules.utils.txn_data_handler import TxnDataHandler
from modules.utils.Logger import logger
from modules.utils.utils import sleeping_sync, req
from modules.utils.token_stor import eth, usdc, usdt
from modules.config import get_slippage, ABI


class SushiSwap(BaseDex):
    contract_address = "0x734583f62Bb6ACe3c9bA9bd5A53143CA2Ce8C55A"
    ABI = [{"inputs":[{"internalType":"address","name":"_bentoBox","type":"address"},{"internalType":"address[]","name":"priviledgedUserList","type":"address[]"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"}],"name":"MinimalOutputBalanceViolation","type":"error"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":True,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"from","type":"address"},{"indexed":False,"internalType":"address","name":"to","type":"address"},{"indexed":True,"internalType":"address","name":"tokenIn","type":"address"},{"indexed":True,"internalType":"address","name":"tokenOut","type":"address"},{"indexed":False,"internalType":"uint256","name":"amountIn","type":"uint256"},{"indexed":False,"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"indexed":False,"internalType":"uint256","name":"amountOut","type":"uint256"}],"name":"Route","type":"event"},{"inputs":[{"internalType":"int256","name":"amount0Delta","type":"int256"},{"internalType":"int256","name":"amount1Delta","type":"int256"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"algebraSwapCallback","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"bentoBox","outputs":[{"internalType":"contract IBentoBoxMinimal","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"int256","name":"amount0Delta","type":"int256"},{"internalType":"int256","name":"amount1Delta","type":"int256"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"pancakeV3SwapCallback","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"pause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"priviledgedUsers","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"tokenIn","type":"address"},{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"address","name":"tokenOut","type":"address"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"bytes","name":"route","type":"bytes"}],"name":"processRoute","outputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"resume","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"user","type":"address"},{"internalType":"bool","name":"priviledge","type":"bool"}],"name":"setPriviledge","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address payable","name":"transferValueTo","type":"address"},{"internalType":"uint256","name":"amountValueTransfer","type":"uint256"},{"internalType":"address","name":"tokenIn","type":"address"},{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"address","name":"tokenOut","type":"address"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"bytes","name":"route","type":"bytes"}],"name":"transferValueAndprocessRoute","outputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"int256","name":"amount0Delta","type":"int256"},{"internalType":"int256","name":"amount1Delta","type":"int256"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"uniswapV3SwapCallback","outputs":[],"stateMutability":"nonpayable","type":"function"},{"stateMutability":"payable","type":"receive"}]
    name = "SushiSwap"
    supported_tokens = ["ETH", "USDT", "USDC"]

    lpts = [
        Token("ETH:USDT", "0x82B8b66CeC3668558AFb66Bcdd83b35E010b39a7", 18, "scroll"),
        Token("ETH:USDC", "0x1d675222304d1c09370A3922F46B63d6024ea768", 18, "scroll"),
        Token("USDT:USDC", "0xa631B2A2C3469aa1bF5dc49977207F378D16d7d8", 18, "scroll"),
   ]

    lpt_from_tokens = {
        "ETH:USDT":lpts[0],
        "USDT:ETH":lpts[0],
        "USDC:ETH":lpts[1],
        "ETH:USDC":lpts[1],
        "USDC:USDT":lpts[2],
        "USDT:USDC":lpts[2],
    }

    tokens_from_lpt = {
        "0x82B8b66CeC3668558AFb66Bcdd83b35E010b39a7": [eth, usdt],
        "0x1d675222304d1c09370A3922F46B63d6024ea768": [usdc, eth],
        "0xa631B2A2C3469aa1bF5dc49977207F378D16d7d8": [usdc, usdt]
    }

    def get_swap_data(self, token1: Token, token2: Token, amount: int, sender: BaseAccount):
        w3 = sender.get_w3('scroll')
        gas_price = w3.eth.gas_price
        token_in = token1.contract_address if token1.symbol != "ETH" else "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
        token_out = token2.contract_address if token2.symbol != "ETH" else "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
        max_price_impact = 1-get_slippage()
        to = sender.address

        resp = req(f"https://api.sushi.com/swap/v4/534352?tokenIn={token_in}&tokenOut={token_out}&amount={amount}&maxPriceImpact={max_price_impact}&gasPrice={gas_price}&to={to}&preferSushi=true")

        result_price_impact = resp["priceImpact"]
        if result_price_impact>max_price_impact:
            raise Exception("Slippage too high")
        
        return resp["routeProcessorArgs"]
        

    def create_txn_for_swap(self, amount_in: float, token1: Token, amount_out: float, token2: Token, sender: BaseAccount, full: bool = False, native_first: bool = False):
        w3 = sender.get_w3('scroll')
        contract = w3.eth.contract(self.contract_address, abi=self.ABI)
        if token1.symbol == "ETH":
            native_first = True
        txn_data_handler = TxnDataHandler(sender, "scroll", w3=w3)

        approve_txn = token1.get_approve_txn(sender, self.contract_address, int(amount_in*10**token1.decimals), w3=w3)
        swap_args = self.get_swap_data(token1, token2, int(amount_in*10**token1.decimals), sender)
        if swap_args.get("value") is None:
            swap_args["value"] = 0
        
        txn = contract.functions.processRoute(
            swap_args["tokenIn"],
            int(swap_args["amountIn"]),
            swap_args["tokenOut"],
            int(swap_args["amountOutMin"]),
            sender.address,
            bytes.fromhex(swap_args["routeCode"][2::])
        ).build_transaction(txn_data_handler.get_txn_data(int(swap_args["value"])))

        return txn

    def create_txn_for_liq(self, amount1: float, token1: Token, amount2: float, token2: Token, sender: BaseAccount):
       pass
    
    def create_txn_for_remove_liq(self, lptoken: Token, sender: BaseAccount):
        pass





