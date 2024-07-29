from time import sleep

from modules.base_classes.base_defi import BaseLend
from modules.base_classes.base_account import BaseAccount
from modules.utils.token import Token
from modules.utils.token_stor import tokens_dict
from modules.utils.txn_data_handler import TxnDataHandler
from modules.utils.token_stor import eth, usdc
from modules.utils.utils import sleeping_sync, get_random_value_int
from modules.config import SETTINGS
from modules.utils.Logger import logger
true = True
false = False

class Aave(BaseLend):
    name = "Aave"
    pool_contract_address = "0x11fCfe756c05AD438e312a7fd934381537D3cFfe"
    price_calculator_address = "0x04421D8C506E2fA2371a08EfAaBf791F624054F3"
    gateway_contract_address = "0xFF75A4B698E3Ec95E608ac0f22A03B8368E05F5D"
    supported_tokens = ["ETH", "USDC"]
    supported_tokens_for_borrow = ["ETH", "USDC"]
    lend_tokens = [
        Token("aETH", "0xf301805bE1Df81102C957f6d4Ce29d2B8c056B2a", 18, "scroll"),
        Token("aUSDC", "0x1D738a3436A8C49CefFbaB7fbF04B660fb528CbD", 6, "scroll"),
    ]

    borrow_tokens = [
        Token("bETH", "0xfD7344CeB1Df9Cf238EcD667f4A6F99c6Ef44a56", 18, "scroll"),
        Token("bUSDC", "0x3d2E209af5BFa79297C88D6b57F89d792F6E28EE", 6, "scroll")
    ]

    borrow_token_from_lend_token = {
        "aETH": borrow_tokens[0],
        "aUSDC": borrow_tokens[1],
    }

    token_from_lend_token = {
        lend_tokens[0]: eth,
        lend_tokens[1]: usdc
    }

    supply_coeffs = {
        "aETH": 0.7425,
        "aUSDC": 0.7425
    }

    coeffs_from_contract = {
        "0xf301805bE1Df81102C957f6d4Ce29d2B8c056B2a": 0.7425,
        "0x1D738a3436A8C49CefFbaB7fbF04B660fb528CbD": 0.7425
    }

    lend_token_from_token = {
        "ETH": lend_tokens[0],
        "USDC": lend_tokens[1]
    }

    borrowed_token_abi = [{"inputs":[{"internalType":"address","name":"delegatee","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"approveDelegation","outputs":[],"stateMutability":"nonpayable","type":"function"}]
    gateway_abi = [{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"interestRateMode","type":"uint256"},{"internalType":"uint16","name":"referralCode","type":"uint16"}],"name":"borrowETH","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"onBehalfOf","type":"address"},{"internalType":"uint16","name":"referralCode","type":"uint16"}],"name":"depositETH","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"rateMode","type":"uint256"},{"internalType":"address","name":"onBehalfOf","type":"address"}],"name":"repayETH","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"address","name":"to","type":"address"}],"name":"withdrawETH","outputs":[],"stateMutability":"nonpayable","type":"function"}]
    calculator_abi = [{"inputs":[{"internalType":"address","name":"asset","type":"address"}],"name":"getAssetPrice","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]
    pool_abi = [{"inputs":[{"internalType":"address","name":"user","type":"address"}],"name":"getUserAccountData","outputs":[{"internalType":"uint256","name":"totalCollateralBase","type":"uint256"},{"internalType":"uint256","name":"totalDebtBase","type":"uint256"},{"internalType":"uint256","name":"availableBorrowsBase","type":"uint256"},{"internalType":"uint256","name":"currentLiquidationThreshold","type":"uint256"},{"internalType":"uint256","name":"ltv","type":"uint256"},{"internalType":"uint256","name":"healthFactor","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"asset","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"address","name":"onBehalfOf","type":"address"},{"internalType":"uint16","name":"referralCode","type":"uint16"}],"name":"supply","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"asset","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"address","name":"to","type":"address"}],"name":"withdraw","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"asset","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"interestRateMode","type":"uint256"},{"internalType":"uint16","name":"referralCode","type":"uint16"},{"internalType":"address","name":"onBehalfOf","type":"address"}],"name":"borrow","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"asset","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"interestRateMode","type":"uint256"},{"internalType":"address","name":"onBehalfOf","type":"address"}],"name":"repay","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"}]



    def function_wrapper(self, func, address, error_msg, *args):
        while True:
            try:
                return func(*args).call()
            except Exception as e:
                logger.error(f"[{address}] {error_msg}: {e}")
                sleeping_sync(address)

    def get_price(self, l_token: Token, sender: BaseAccount):
        while True:
            try:
                w3 = sender.get_w3("scroll")
                contract = w3.eth.contract(self.price_calculator_address, abi=self.calculator_abi)

                return contract.functions.getAssetPrice(tokens_dict[l_token.symbol[1::]].contract_address).call()/1e8
            except Exception as e:
                logger.error(f"[{sender.get_address()}] can't get {l_token.symbol} price: {e} trying again")
                sleeping_sync(sender.get_address())
    
    def get_total_supplied(self, sender: BaseAccount):
        w3 = sender.get_w3("scroll")
        contract = w3.eth.contract(self.pool_contract_address, abi=self.pool_abi)

        user_data = self.function_wrapper(
            contract.functions.getUserAccountData,
            sender.address,
            "Can't get user data",
            sender.address
        )

        total = user_data[0]
        return int(total)/1e8

    def get_total_borrowed(self, sender: BaseAccount):
        w3 = sender.get_w3("scroll")
        contract = w3.eth.contract(self.pool_contract_address, abi=self.pool_abi)

        user_data = self.function_wrapper(
            contract.functions.getUserAccountData,
            sender.address,
            "Can't get user data",
            sender.address
        )

        total = user_data[1]
        return int(total)/1e8
    
    def how_many_can_borrow(self, sender: BaseAccount):
        w3 = sender.get_w3("scroll")
        contract = w3.eth.contract(self.pool_contract_address, abi=self.pool_abi)

        user_data = self.function_wrapper(
            contract.functions.getUserAccountData,
            sender.address,
            "Can't get user data",
            sender.address
        )

        total = user_data[2]
        return int(total*0.99)/1e8
    
    def how_many_can_remove(self, token: Token, sender: BaseAccount):
        return self.how_many_can_borrow(sender)/0.7425

    def create_txn_for_adding_token(self, token: Token, amount: float, sender: BaseAccount):
        w3 = sender.get_w3("scroll")
        txn_data_handler = TxnDataHandler(sender, "scroll", w3=w3)
        

        token.get_approve_txn(sender, "0x11fCfe756c05AD438e312a7fd934381537D3cFfe", int(amount*10**token.decimals), w3=w3)

        if token.symbol == "ETH":
            contract = w3.eth.contract(self.gateway_contract_address, abi=self.gateway_abi)
            value =  int(amount*10**token.decimals)
            function = contract.functions.depositETH
            txn = function(
                "0x11fCfe756c05AD438e312a7fd934381537D3cFfe",
                sender.address,
                0
            ).build_transaction(txn_data_handler.get_txn_data(value))
        else:
            contract = w3.eth.contract(self.pool_contract_address, abi=self.pool_abi)
            function = contract.functions.supply
            txn = function(
                token.contract_address,
                int(amount*10**token.decimals),
                sender.address,
                0
            ).build_transaction(txn_data_handler.get_txn_data())

       

        return txn
    
    def create_txn_for_removing_token(self, token: Token, sender: BaseAccount):
        w3 = sender.get_w3("scroll")
       
        txn_data_handler = TxnDataHandler(sender, "scroll", w3=w3)

        can_remove = (self.how_many_can_remove(token, sender)/self.get_price(token, sender)) * 10**token.decimals
        amount = token.balance_of(sender.address, w3=w3)[0] - 1
        if amount > can_remove:
            amount = int(can_remove - 1)
        
        if amount <= 1:
            logger.error(f"[{sender.get_address()}] can't remove any tokens")
            return -1
        

        if token.symbol == "aETH":
            contract = w3.eth.contract(self.gateway_contract_address, abi=self.gateway_abi)
            token.get_approve_txn(sender, "0xFF75A4B698E3Ec95E608ac0f22A03B8368E05F5D", amount, w3=w3)
            txn = contract.functions.withdrawETH(
                "0x11fCfe756c05AD438e312a7fd934381537D3cFfe",
                amount,
                sender.address
            ).build_transaction(txn_data_handler.get_txn_data())
        else:
            contract = w3.eth.contract(self.pool_contract_address, abi=self.pool_abi)
            token.get_approve_txn(sender, self.pool_contract_address, amount, w3=w3)
            txn = contract.functions.withdraw(
                tokens_dict[token.symbol[1::]].contract_address,
                amount,
                sender.address
            ).build_transaction(txn_data_handler.get_txn_data()) 
        return txn
    
    def create_txn_to_borrow_token(self, amount: float, token: Token, sender: BaseAccount):
        logger.info(f"[{sender.address}] going to borrow {amount} {token.symbol}")
        w3 = sender.get_w3("scroll")
        txn_data_handler = TxnDataHandler(sender, "scroll", w3=w3)
        l_token = self.lend_token_from_token[token.symbol]
        borrow_limit = (self.how_many_can_borrow(sender)/self.get_price(l_token, sender))*10**token.decimals
        if borrow_limit <= 1:
            logger.error(f"[{sender.get_address()}] can't borrow any tokens.")
            return -1
        
        if amount*10**token.decimals > borrow_limit:
            amount = int(borrow_limit - 1)
            logger.info(f"[{sender.get_address()}] amount out of borrow limits. Will borrow only {amount/10**token.decimals} {token.symbol}")
        else:
            amount = int(amount*10**token.decimals)

        if token.symbol == "ETH":
            contract = w3.eth.contract(self.gateway_contract_address, abi=self.gateway_abi)
            borrowed_token = self.borrow_token_from_lend_token[l_token.symbol]
            token_contract = w3.eth.contract(borrowed_token.contract_address, abi=self.borrowed_token_abi)
            logger.info(f"[{sender.address}] going to approve {borrowed_token.symbol}")

            txn = token_contract.functions.approveDelegation(
                "0xFF75A4B698E3Ec95E608ac0f22A03B8368E05F5D",
                amount
            ).build_transaction(txn_data_handler.get_txn_data())
            sender.send_txn(txn, "scroll")
            t = get_random_value_int(SETTINGS["Approve Sleep"])
            logger.info(f"[{sender.get_address()}] sleeping {t} s")
            sleep(t)
            txn = contract.functions.borrowETH(
                "0x11fCfe756c05AD438e312a7fd934381537D3cFfe",
                amount,
                2,
                0
            ).build_transaction(txn_data_handler.get_txn_data())
        else:
            contract = w3.eth.contract(self.pool_contract_address, abi=self.pool_abi)
            txn = contract.functions.borrow(
                token.contract_address,
                amount,
                2,
                0,
                sender.address
            ).build_transaction(txn_data_handler.get_txn_data()) 

        return txn
        

    def create_txn_to_repay_token(self, token: Token, sender: BaseAccount):
        w3 = sender.get_w3("scroll")
        txn_data_handler = TxnDataHandler(sender, "scroll", w3=w3)
        l_token = self.lend_token_from_token[token.symbol]
        borrowed_token = self.borrow_token_from_lend_token[l_token.symbol]

        borrowed = sender.get_balance(borrowed_token)[0]

        if borrowed <= 100:
            logger.info(f"[{sender.get_address()}] borrowed amount of {token.symbol} is 0")
            return -1
        
        logger.info(f"[{sender.get_address()}] going to repay {token.symbol}")

        balance, human_balance = sender.get_balance(token)
        if balance > borrowed:
            to_repay = borrowed - 2
        else:
            to_repay = balance - 2
        
        if token.symbol == "ETH":
            contract = w3.eth.contract(self.gateway_contract_address, abi=self.gateway_abi)
            
            txn = contract.functions.repayETH(
                "0x11fCfe756c05AD438e312a7fd934381537D3cFfe",
                to_repay,
                2,
                sender.address
            ).build_transaction(txn_data_handler.get_txn_data(to_repay))
        else:
            contract = w3.eth.contract(self.pool_contract_address, abi=self.pool_abi)
            token.get_approve_txn(sender, self.pool_contract_address, to_repay, w3=w3)
            txn = contract.functions.repay(
                token.contract_address,
                to_repay,
                2,
                sender.address
            ).build_transaction(txn_data_handler.get_txn_data()) 

        return txn