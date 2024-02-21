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



class ScrollSwap(BaseDex):
    contract_address = "0xEfEb222F8046aAa032C56290416C3192111C0085"
    ABI = [{"inputs":[],"name":"WETH","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"amountADesired","type":"uint256"},{"internalType":"uint256","name":"amountBDesired","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"addLiquidity","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"},{"internalType":"uint256","name":"liquidity","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amountTokenDesired","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"addLiquidityETH","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"},{"internalType":"uint256","name":"liquidity","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"factory","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"reserveIn","type":"uint256"},{"internalType":"uint256","name":"reserveOut","type":"uint256"}],"name":"getAmountIn","outputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"reserveIn","type":"uint256"},{"internalType":"uint256","name":"reserveOut","type":"uint256"}],"name":"getAmountOut","outputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsIn","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsOut","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"reserveA","type":"uint256"},{"internalType":"uint256","name":"reserveB","type":"uint256"}],"name":"quote","outputs":[{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidity","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidityETH","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidityETHSupportingFeeOnTransferTokens","outputs":[{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityETHWithPermit","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityETHWithPermitSupportingFeeOnTransferTokens","outputs":[{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityWithPermit","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapETHForExactTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokensSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForETHSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokensSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMax","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMax","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"}]
    name = "ScrollSwap"
    supported_tokens = ["ETH", "USDT"]

    lpts = [
        Token("ETH:USDT", "0xE3c46d28C23007B0BfF7Bb58471C81312C0A8690", 18, "scroll"),
   ]

    lpt_from_tokens = {
        "ETH:USDT":lpts[0],
        "USDT:ETH":lpts[0],
    }

    tokens_from_lpt = {
        "0xE3c46d28C23007B0BfF7Bb58471C81312C0A8690": [eth, usdt],

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
                    token1.contract_address,
                    token2.contract_address
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
                    token1.contract_address,
                    token2.contract_address
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

        approve1_txn = token1.get_approve_txn(sender, self.contract_address, int(amount1*10**token1.decimals), w3=w3)
        approve2_txn = token2.get_approve_txn(sender, self.contract_address, int(amount2*10**token2.decimals), w3=w3)

        if token1.symbol == "ETH" or token2.symbol == "ETH":
            if token1.symbol == "ETH":
                token = token2
                amount_token = amount2
                amount_eth = amount1
            else:
                token = token1
                amount_token = amount1
                amount_eth = amount2
            
            txn = contract.functions.addLiquidityETH(
                token.contract_address,
                int(amount_token*10**token.decimals), 
                int(get_slippage()*amount_token*10**token.decimals),
                int(get_slippage()*amount_eth*1e18),
                sender.get_address(),
                deadline
            ).build_transaction(txn_data_handler.get_txn_data(int(amount_eth*1e18)))
        else:
            txn = contract.functions.addLiquidity(
                token1.contract_address,
                token2.contract_address,
                int(amount1*10**token1.decimals),
                int(amount2*10**token2.decimals),
                int(get_slippage()*amount1*10**token1.decimals),
                int(get_slippage()*amount2*10**token2.decimals),
                sender.get_address(),
                deadline
            ).build_transaction(txn_data_handler.get_txn_data())
        
        return txn

    def _get_nonce_of_liq_token(self, address: str, lpt: Token, w3):
        contract = w3.eth.contract(lpt.contract_address, abi=ABI)
        while True:
            try:
                nonce = contract.functions.nonces(address).call()
                return nonce
            except Exception as e:
                logger.error(f"[{address}] got error while trying to get nonce of lpt: {e}")
                sleeping_sync(address, True)
                
    def create_txn_for_remove_liq(self, lptoken: Token, sender: BaseAccount):
        w3 = sender.get_w3('scroll')
        contract = w3.eth.contract(self.contract_address, abi=self.ABI)
        txn_data_handler = TxnDataHandler(sender, "scroll", w3=w3)
        token1: Token = self.tokens_from_lpt[lptoken.contract_address][0]
        token2: Token = self.tokens_from_lpt[lptoken.contract_address][1]

        stable = token1.stable and token2.stable
        token1_val = token1.balance_of(lptoken.contract_address, w3=w3, of_wrapped=True)[0]
        token2_val = token2.balance_of(lptoken.contract_address, w3=w3, of_wrapped=True)[0]
        deadline = int(time.time()+3600)
        lpt_contract = w3.eth.contract(lptoken.contract_address, abi=ABI)
        total_liq_amount = lpt_contract.functions.totalSupply().call()
        liq_amount = lptoken.balance_of(sender.get_address(), w3=w3)[0]
        multiplier = liq_amount/total_liq_amount

        user_part1 = int(token1_val*multiplier*get_slippage())
        user_part2 = int(token2_val*multiplier*get_slippage())


        msg = {
            'types': {
                'EIP712Domain': [
                { 'name': 'name', 'type': 'string' },
                { 'name': 'version', 'type': 'string' },
                { 'name': 'chainId', 'type': 'uint256' },
                { 'name': 'verifyingContract', 'type': 'address' },
                ],
                'Permit': [
                { 'name': 'owner', 'type': 'address' },
                { 'name': 'spender', 'type': 'address' },
                { 'name': 'value', 'type': 'uint256' },
                { 'name': 'nonce', 'type': 'uint256' },
                { 'name': 'deadline', 'type': 'uint256' },
                ]
            },
            'domain': {
                'name': 'Scrollswap LPs',
                'version': '1',
                'chainId': 534352,
                'verifyingContract': lptoken.contract_address,
            },
            'primaryType': 'Permit',
            'message': {
                'owner': sender.get_address(),
                'spender': self.contract_address,
                'value': int(lptoken.balance_of(sender.get_address(), w3=w3)[0]),
                'nonce': self._get_nonce_of_liq_token(sender.get_address(), lptoken, w3),
                'deadline': deadline
                

            },
            
        }
        
        encoded_msg = encode_structured_data(msg)
        
        signed_msg = w3.eth.account.sign_message(encoded_msg, sender.private_key)
       

        r = signed_msg.r.to_bytes(32, "big")
        s = signed_msg.s.to_bytes(32, "big")
        v = signed_msg.v


        if token1.symbol == "ETH" or token2.symbol == "ETH":
            if token1.symbol == "ETH":
                token = token2
                user_part_eth = user_part1
                user_part_token = user_part2
            else:
                token = token1
                user_part_eth = user_part2
                user_part_token = user_part1
            
            txn = contract.functions.removeLiquidityETHWithPermit(
                token.contract_address,
                liq_amount,
                user_part_token,
                user_part_eth,
                sender.get_address(),
                deadline,
                False,
                v,
                r,
                s
            ).build_transaction(txn_data_handler.get_txn_data())
        else:
            txn = contract.functions.removeLiquidityWithPermit(
                token1.contract_address,
                token2.contract_address,
                liq_amount,
                user_part1,
                user_part2,
                sender.get_address(),
                deadline,
                False,
                v,
                r,
                s
            ).build_transaction(txn_data_handler.get_txn_data())

        return txn





