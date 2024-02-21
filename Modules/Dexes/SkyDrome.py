import time

from eth_account.messages import encode_structured_data

from Modules.BaseClasses.BaseAccount import BaseAccount
from Modules.BaseClasses.BaseDeFi import BaseDex
from Modules.Utils.Token import Token   
from Modules.config import get_slippage, ABI
from Modules.Utils.TxnDataHandler import TxnDataHandler
from Modules.Utils.Logger import logger
from Modules.Utils.utils import sleeping_sync
from Modules.Utils.token_stor import eth, usdc, usdt


class Skydrome(BaseDex):
    contract_address = "0xAA111C62cDEEf205f70E6722D1E22274274ec12F"
    ABI = [{"type":"constructor","stateMutability":"nonpayable","inputs":[{"type":"address","name":"_factory","internalType":"address"},{"type":"address","name":"_weth","internalType":"address"}]},{"type":"function","stateMutability":"nonpayable","outputs":[{"type":"uint256[]","name":"","internalType":"uint256[]"}],"name":"UNSAFE_swapExactTokensForTokens","inputs":[{"type":"uint256[]","name":"amounts","internalType":"uint256[]"},{"type":"tuple[]","name":"routes","internalType":"struct Router.route[]","components":[{"type":"address","name":"from","internalType":"address"},{"type":"address","name":"to","internalType":"address"},{"type":"bool","name":"stable","internalType":"bool"}]},{"type":"address","name":"to","internalType":"address"},{"type":"uint256","name":"deadline","internalType":"uint256"}]},{"type":"function","stateMutability":"nonpayable","outputs":[{"type":"uint256","name":"amountA","internalType":"uint256"},{"type":"uint256","name":"amountB","internalType":"uint256"},{"type":"uint256","name":"liquidity","internalType":"uint256"}],"name":"addLiquidity","inputs":[{"type":"address","name":"tokenA","internalType":"address"},{"type":"address","name":"tokenB","internalType":"address"},{"type":"bool","name":"stable","internalType":"bool"},{"type":"uint256","name":"amountADesired","internalType":"uint256"},{"type":"uint256","name":"amountBDesired","internalType":"uint256"},{"type":"uint256","name":"amountAMin","internalType":"uint256"},{"type":"uint256","name":"amountBMin","internalType":"uint256"},{"type":"address","name":"to","internalType":"address"},{"type":"uint256","name":"deadline","internalType":"uint256"}]},{"type":"function","stateMutability":"payable","outputs":[{"type":"uint256","name":"amountToken","internalType":"uint256"},{"type":"uint256","name":"amountETH","internalType":"uint256"},{"type":"uint256","name":"liquidity","internalType":"uint256"}],"name":"addLiquidityETH","inputs":[{"type":"address","name":"token","internalType":"address"},{"type":"bool","name":"stable","internalType":"bool"},{"type":"uint256","name":"amountTokenDesired","internalType":"uint256"},{"type":"uint256","name":"amountTokenMin","internalType":"uint256"},{"type":"uint256","name":"amountETHMin","internalType":"uint256"},{"type":"address","name":"to","internalType":"address"},{"type":"uint256","name":"deadline","internalType":"uint256"}]},{"type":"function","stateMutability":"view","outputs":[{"type":"address","name":"","internalType":"address"}],"name":"factory","inputs":[]},{"type":"function","stateMutability":"view","outputs":[{"type":"uint256","name":"amount","internalType":"uint256"},{"type":"bool","name":"stable","internalType":"bool"}],"name":"getAmountOut","inputs":[{"type":"uint256","name":"amountIn","internalType":"uint256"},{"type":"address","name":"tokenIn","internalType":"address"},{"type":"address","name":"tokenOut","internalType":"address"}]},{"type":"function","stateMutability":"view","outputs":[{"type":"uint256","name":"amount","internalType":"uint256"}],"name":"getAmountOut","inputs":[{"type":"uint256","name":"amountIn","internalType":"uint256"},{"type":"address","name":"tokenIn","internalType":"address"},{"type":"address","name":"tokenOut","internalType":"address"},{"type":"bool","name":"stable","internalType":"bool"}]},{"type":"function","stateMutability":"view","outputs":[{"type":"uint256[]","name":"amounts","internalType":"uint256[]"}],"name":"getAmountsOut","inputs":[{"type":"uint256","name":"amountIn","internalType":"uint256"},{"type":"tuple[]","name":"routes","internalType":"struct Router.route[]","components":[{"type":"address","name":"from","internalType":"address"},{"type":"address","name":"to","internalType":"address"},{"type":"bool","name":"stable","internalType":"bool"}]}]},{"type":"function","stateMutability":"view","outputs":[{"type":"uint256","name":"reserveA","internalType":"uint256"},{"type":"uint256","name":"reserveB","internalType":"uint256"}],"name":"getReserves","inputs":[{"type":"address","name":"tokenA","internalType":"address"},{"type":"address","name":"tokenB","internalType":"address"},{"type":"bool","name":"stable","internalType":"bool"}]},{"type":"function","stateMutability":"view","outputs":[{"type":"bool","name":"","internalType":"bool"}],"name":"isPair","inputs":[{"type":"address","name":"pair","internalType":"address"}]},{"type":"function","stateMutability":"view","outputs":[{"type":"address","name":"pair","internalType":"address"}],"name":"pairFor","inputs":[{"type":"address","name":"tokenA","internalType":"address"},{"type":"address","name":"tokenB","internalType":"address"},{"type":"bool","name":"stable","internalType":"bool"}]},{"type":"function","stateMutability":"view","outputs":[{"type":"uint256","name":"amountA","internalType":"uint256"},{"type":"uint256","name":"amountB","internalType":"uint256"},{"type":"uint256","name":"liquidity","internalType":"uint256"}],"name":"quoteAddLiquidity","inputs":[{"type":"address","name":"tokenA","internalType":"address"},{"type":"address","name":"tokenB","internalType":"address"},{"type":"bool","name":"stable","internalType":"bool"},{"type":"uint256","name":"amountADesired","internalType":"uint256"},{"type":"uint256","name":"amountBDesired","internalType":"uint256"}]},{"type":"function","stateMutability":"view","outputs":[{"type":"uint256","name":"amountA","internalType":"uint256"},{"type":"uint256","name":"amountB","internalType":"uint256"}],"name":"quoteRemoveLiquidity","inputs":[{"type":"address","name":"tokenA","internalType":"address"},{"type":"address","name":"tokenB","internalType":"address"},{"type":"bool","name":"stable","internalType":"bool"},{"type":"uint256","name":"liquidity","internalType":"uint256"}]},{"type":"function","stateMutability":"nonpayable","outputs":[{"type":"uint256","name":"amountA","internalType":"uint256"},{"type":"uint256","name":"amountB","internalType":"uint256"}],"name":"removeLiquidity","inputs":[{"type":"address","name":"tokenA","internalType":"address"},{"type":"address","name":"tokenB","internalType":"address"},{"type":"bool","name":"stable","internalType":"bool"},{"type":"uint256","name":"liquidity","internalType":"uint256"},{"type":"uint256","name":"amountAMin","internalType":"uint256"},{"type":"uint256","name":"amountBMin","internalType":"uint256"},{"type":"address","name":"to","internalType":"address"},{"type":"uint256","name":"deadline","internalType":"uint256"}]},{"type":"function","stateMutability":"nonpayable","outputs":[{"type":"uint256","name":"amountToken","internalType":"uint256"},{"type":"uint256","name":"amountETH","internalType":"uint256"}],"name":"removeLiquidityETH","inputs":[{"type":"address","name":"token","internalType":"address"},{"type":"bool","name":"stable","internalType":"bool"},{"type":"uint256","name":"liquidity","internalType":"uint256"},{"type":"uint256","name":"amountTokenMin","internalType":"uint256"},{"type":"uint256","name":"amountETHMin","internalType":"uint256"},{"type":"address","name":"to","internalType":"address"},{"type":"uint256","name":"deadline","internalType":"uint256"}]},{"type":"function","stateMutability":"nonpayable","outputs":[{"type":"uint256","name":"amountToken","internalType":"uint256"},{"type":"uint256","name":"amountETH","internalType":"uint256"}],"name":"removeLiquidityETHWithPermit","inputs":[{"type":"address","name":"token","internalType":"address"},{"type":"bool","name":"stable","internalType":"bool"},{"type":"uint256","name":"liquidity","internalType":"uint256"},{"type":"uint256","name":"amountTokenMin","internalType":"uint256"},{"type":"uint256","name":"amountETHMin","internalType":"uint256"},{"type":"address","name":"to","internalType":"address"},{"type":"uint256","name":"deadline","internalType":"uint256"},{"type":"bool","name":"approveMax","internalType":"bool"},{"type":"uint8","name":"v","internalType":"uint8"},{"type":"bytes32","name":"r","internalType":"bytes32"},{"type":"bytes32","name":"s","internalType":"bytes32"}]},{"type":"function","stateMutability":"nonpayable","outputs":[{"type":"uint256","name":"amountA","internalType":"uint256"},{"type":"uint256","name":"amountB","internalType":"uint256"}],"name":"removeLiquidityWithPermit","inputs":[{"type":"address","name":"tokenA","internalType":"address"},{"type":"address","name":"tokenB","internalType":"address"},{"type":"bool","name":"stable","internalType":"bool"},{"type":"uint256","name":"liquidity","internalType":"uint256"},{"type":"uint256","name":"amountAMin","internalType":"uint256"},{"type":"uint256","name":"amountBMin","internalType":"uint256"},{"type":"address","name":"to","internalType":"address"},{"type":"uint256","name":"deadline","internalType":"uint256"},{"type":"bool","name":"approveMax","internalType":"bool"},{"type":"uint8","name":"v","internalType":"uint8"},{"type":"bytes32","name":"r","internalType":"bytes32"},{"type":"bytes32","name":"s","internalType":"bytes32"}]},{"type":"function","stateMutability":"pure","outputs":[{"type":"address","name":"token0","internalType":"address"},{"type":"address","name":"token1","internalType":"address"}],"name":"sortTokens","inputs":[{"type":"address","name":"tokenA","internalType":"address"},{"type":"address","name":"tokenB","internalType":"address"}]},{"type":"function","stateMutability":"payable","outputs":[{"type":"uint256[]","name":"amounts","internalType":"uint256[]"}],"name":"swapExactETHForTokens","inputs":[{"type":"uint256","name":"amountOutMin","internalType":"uint256"},{"type":"tuple[]","name":"routes","internalType":"struct Router.route[]","components":[{"type":"address","name":"from","internalType":"address"},{"type":"address","name":"to","internalType":"address"},{"type":"bool","name":"stable","internalType":"bool"}]},{"type":"address","name":"to","internalType":"address"},{"type":"uint256","name":"deadline","internalType":"uint256"}]},{"type":"function","stateMutability":"nonpayable","outputs":[{"type":"uint256[]","name":"amounts","internalType":"uint256[]"}],"name":"swapExactTokensForETH","inputs":[{"type":"uint256","name":"amountIn","internalType":"uint256"},{"type":"uint256","name":"amountOutMin","internalType":"uint256"},{"type":"tuple[]","name":"routes","internalType":"struct Router.route[]","components":[{"type":"address","name":"from","internalType":"address"},{"type":"address","name":"to","internalType":"address"},{"type":"bool","name":"stable","internalType":"bool"}]},{"type":"address","name":"to","internalType":"address"},{"type":"uint256","name":"deadline","internalType":"uint256"}]},{"type":"function","stateMutability":"nonpayable","outputs":[{"type":"uint256[]","name":"amounts","internalType":"uint256[]"}],"name":"swapExactTokensForTokens","inputs":[{"type":"uint256","name":"amountIn","internalType":"uint256"},{"type":"uint256","name":"amountOutMin","internalType":"uint256"},{"type":"tuple[]","name":"routes","internalType":"struct Router.route[]","components":[{"type":"address","name":"from","internalType":"address"},{"type":"address","name":"to","internalType":"address"},{"type":"bool","name":"stable","internalType":"bool"}]},{"type":"address","name":"to","internalType":"address"},{"type":"uint256","name":"deadline","internalType":"uint256"}]},{"type":"function","stateMutability":"nonpayable","outputs":[{"type":"uint256[]","name":"amounts","internalType":"uint256[]"}],"name":"swapExactTokensForTokensSimple","inputs":[{"type":"uint256","name":"amountIn","internalType":"uint256"},{"type":"uint256","name":"amountOutMin","internalType":"uint256"},{"type":"address","name":"tokenFrom","internalType":"address"},{"type":"address","name":"tokenTo","internalType":"address"},{"type":"bool","name":"stable","internalType":"bool"},{"type":"address","name":"to","internalType":"address"},{"type":"uint256","name":"deadline","internalType":"uint256"}]},{"type":"function","stateMutability":"view","outputs":[{"type":"address","name":"","internalType":"contract IWETH"}],"name":"weth","inputs":[]},{"type":"receive","stateMutability":"payable"}]
    name = "Skydrome"
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

    def create_txn_for_swap(self, amount_in: float, token1: Token, amount_out: float, token2: Token, sender: BaseAccount, full: bool = False, native_first: bool = False):
        w3 = sender.get_w3('scroll')
        contract = w3.eth.contract(self.contract_address, abi=self.ABI)
        stable = token1.stable and token2.stable
        if token1.symbol == "ETH":
            native_first = True
        txn_data_handler = TxnDataHandler(sender, "scroll", w3=w3)

        approve_txn = token1.get_approve_txn(sender, self.contract_address, int(amount_in*10**token1.decimals), w3=w3)
        deadline = int(time.time()+3600)

        if native_first:
            value = int(amount_in*10**token1.decimals)
            function = contract.functions.swapExactETHForTokens
            txn = function(
                int(get_slippage()*amount_out*10**token2.decimals),
                [
                    (token1.contract_address,
                    token2.contract_address, 
                    stable)
                ],
                sender.get_address(),
                deadline
            ).build_transaction(txn_data_handler.get_txn_data(value))
        else:
            if token2.symbol == "ETH":
                function = contract.functions.swapExactTokensForETH
            else:
                function = contract.functions.swapExactTokensForTokens
            value = 0
            txn = function(
                int(amount_in*10**token1.decimals),
                int(get_slippage()*amount_out*10**token2.decimals),
                [
                    (token1.contract_address,
                    token2.contract_address,
                    stable)
                ],
                sender.get_address(),
                deadline
            ).build_transaction(txn_data_handler.get_txn_data(value))

        

        return txn


    def get_pool_rate(self, token1: Token, token2: Token, sender: BaseAccount):
        lpt = self.lpt_from_tokens[f"{token1.symbol}:{token2.symbol}"]
        token1_val = token1.balance_of(lpt.contract_address, w3=sender.get_w3('scroll'), of_wrapped=True)[1]
        token2_val = token2.balance_of(lpt.contract_address, w3=sender.get_w3('scroll'), of_wrapped=True)[1]

        token1_usd_val = token1.get_usd_value(token1_val)
        token2_usd_val = token2.get_usd_value(token2_val)

        return token1_usd_val/token2_usd_val


    def create_txn_for_liq(self, amount1: float, token1: Token, amount2: float, token2: Token, sender: BaseAccount):
        w3 = sender.get_w3('scroll')
        contract = w3.eth.contract(self.contract_address, abi=self.ABI)
        stable = token1.stable and token2.stable
        txn_data_handler = TxnDataHandler(sender, "scroll", w3=w3)
        deadline = int(time.time()+3600)

        rate = self.get_pool_rate(token1, token2, sender)

        if rate > 1:
            amount2 = amount2/rate
        else:
            amount1 = amount1*rate
        if token1.symbol == "ETH" or token2.symbol == "ETH":
            if token1.symbol == "ETH":
                am = amount1
            else:
                am = amount2
            wrap_txn = eth.create_wrap_txn(False, am, sender, w3=w3)
            logger.info(f"[{sender.get_address()}] wrapping {am} ETH")
            sender.send_txn(wrap_txn, "scroll")
            sleeping_sync(sender.get_address(), False)
            approve0_txn = eth.get_approve_txn_wrapped(False, sender, self.contract_address, am, w3=w3)
            sleeping_sync(sender.get_address())


        approve1_txn = token1.get_approve_txn(sender, self.contract_address, int(amount1*10**token1.decimals), w3=w3)
        approve2_txn = token2.get_approve_txn(sender, self.contract_address, int(amount2*10**token2.decimals), w3=w3)

        
        txn = contract.functions.addLiquidity(
            token1.contract_address,
            token2.contract_address,
            stable,
            int(amount1*10**token1.decimals),
            int(amount2*10**token2.decimals),
            int(get_slippage()*amount1*10**token1.decimals),
            int(get_slippage()*amount2*10**token2.decimals),
            sender.get_address(),
            deadline
        ).build_transaction(txn_data_handler.get_txn_data())
        
        return txn
    
    def create_txn_for_remove_liq(self, lptoken: Token, sender: BaseAccount):
        w3 = sender.get_w3('scroll')
        contract = w3.eth.contract(self.contract_address, abi=self.ABI)
        txn_data_handler = TxnDataHandler(sender, "scroll", w3=w3)
        token1: Token = self.tokens_from_lpt[lptoken.contract_address][0]
        token2: Token = self.tokens_from_lpt[lptoken.contract_address][1]

        stable = token1.stable and token2.stable
        token1_val = token1.balance_of(lptoken.contract_address, of_wrapped=True, w3=w3)[0]
        token2_val = token2.balance_of(lptoken.contract_address, of_wrapped=True, w3=w3)[0]
        deadline = int(time.time()+3600)

        lpt_contract = w3.eth.contract(lptoken.contract_address, abi=ABI)
        total_liq_amount = lpt_contract.functions.totalSupply().call()

        liq_amount = lptoken.balance_of(sender.get_address())[0]

        multiplier = liq_amount/total_liq_amount

        user_part1 = int(token1_val*multiplier*get_slippage())
        user_part2 = int(token2_val*multiplier*get_slippage())

        lptoken.get_approve_txn(sender, self.contract_address, liq_amount, w3=w3)


        
        txn = contract.functions.removeLiquidity(
            token1.contract_address,
            token2.contract_address,
            stable,
            liq_amount,
            user_part1,
            user_part2,
            sender.get_address(),
            deadline
        ).build_transaction(txn_data_handler.get_txn_data())
        if "ETH" in [token1.symbol, token2.symbol]:
            sender.send_txn(txn, "scroll")
            sleeping_sync(sender.get_address())
            txn = eth.create_unwrap_txn(sender, w3=w3)
        return txn





