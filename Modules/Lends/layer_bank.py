from Modules.BaseClasses.BaseDeFi import BaseLend
from Modules.BaseClasses.BaseAccount import BaseAccount
from Modules.Utils.Token import Token
from Modules.Utils.TxnDataHandler import TxnDataHandler
from Modules.Utils.utils import sleeping_sync
from Modules.Utils.Logger import logger
true = True
false = False

class LayerBank(BaseLend):
    name = "LayerBank"
    contract_address = "0xEC53c830f4444a8A56455c6836b5D2aA794289Aa"
    price_calculator_address = "0x760bd7Fc100F217678D1b521404D2E93Db7Bec5F"
    supported_tokens = ["ETH", "USDC"]
    supported_tokens_for_borrow = ["ETH", "USDC"]
    lend_tokens = [
        Token("lETH", "0x274C3795dadfEbf562932992bF241ae087e0a98C", 18, "scroll"),
        Token("lUSDC", "0x0D8F8e271DD3f2fC58e5716d3Ff7041dBe3F0688", 18, "scroll"),
    ]

    supply_coeffs = {
        "ETH": 0.7,
        "USDC": 0.8
    }

    coeffs_from_contract = {
        "0x274C3795dadfEbf562932992bF241ae087e0a98C": 0.7,
        "0x0D8F8e271DD3f2fC58e5716d3Ff7041dBe3F0688": 0.8
    }

    lend_token_from_token = {
        "ETH": lend_tokens[0],
        "USDC": lend_tokens[1]
    }


    ltoken_abi = [{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"borrowBalanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]
    calculator_abi = [{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"inputs":[{"internalType":"address","name":"lToken","type":"address"}],"name":"getUnderlyingPrice","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address[]","name":"lTokens","type":"address[]"}],"name":"getUnderlyingPrices","outputs":[{"internalType":"uint256[]","name":"","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"keeper","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"asset","type":"address"}],"name":"priceOf","outputs":[{"internalType":"uint256","name":"priceInUSD","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"priceOfETH","outputs":[{"internalType":"uint256","name":"valueInUSD","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address[]","name":"assets","type":"address[]"}],"name":"pricesOf","outputs":[{"internalType":"uint256[]","name":"","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"references","outputs":[{"internalType":"uint256","name":"lastData","type":"uint256"},{"internalType":"uint256","name":"lastUpdated","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_keeper","type":"address"}],"name":"setKeeper","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address[]","name":"assets","type":"address[]"},{"internalType":"uint256[]","name":"prices","type":"uint256[]"},{"internalType":"uint256","name":"timestamp","type":"uint256"}],"name":"setPrices","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"asset","type":"address"},{"internalType":"address","name":"feed","type":"address"}],"name":"setTokenFeed","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"}]
    abi = [{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"lToken","type":"address"},{"indexed":false,"internalType":"uint256","name":"newBorrowCap","type":"uint256"}],"name":"BorrowCapUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"newCloseFactor","type":"uint256"}],"name":"CloseFactorUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"lToken","type":"address"},{"indexed":false,"internalType":"uint256","name":"newCollateralFactor","type":"uint256"}],"name":"CollateralFactorUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"target","type":"address"},{"indexed":true,"internalType":"address","name":"initiator","type":"address"},{"indexed":true,"internalType":"address","name":"asset","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"premium","type":"uint256"}],"name":"FlashLoan","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"newKeeper","type":"address"}],"name":"KeeperUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"newLABDistributor","type":"address"}],"name":"LABDistributorUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"newLeverager","type":"address"}],"name":"LeveragerUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"newLiquidationIncentive","type":"uint256"}],"name":"LiquidationIncentiveUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"lToken","type":"address"},{"indexed":false,"internalType":"address","name":"account","type":"address"}],"name":"MarketEntered","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"lToken","type":"address"},{"indexed":false,"internalType":"address","name":"account","type":"address"}],"name":"MarketExited","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"lToken","type":"address"}],"name":"MarketListed","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"user","type":"address"},{"indexed":false,"internalType":"address","name":"lToken","type":"address"},{"indexed":false,"internalType":"uint256","name":"uAmount","type":"uint256"}],"name":"MarketRedeem","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"user","type":"address"},{"indexed":false,"internalType":"address","name":"lToken","type":"address"},{"indexed":false,"internalType":"uint256","name":"uAmount","type":"uint256"}],"name":"MarketSupply","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"account","type":"address"}],"name":"Paused","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"newRebateDistributor","type":"address"}],"name":"RebateDistributorUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"lToken","type":"address"},{"indexed":false,"internalType":"uint256","name":"newSupplyCap","type":"uint256"}],"name":"SupplyCapUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"account","type":"address"}],"name":"Unpaused","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"newValidator","type":"address"}],"name":"ValidatorUpdated","type":"event"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"accountLiquidityOf","outputs":[{"internalType":"uint256","name":"collateralInUSD","type":"uint256"},{"internalType":"uint256","name":"supplyInUSD","type":"uint256"},{"internalType":"uint256","name":"borrowInUSD","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"allMarkets","outputs":[{"internalType":"address[]","name":"","type":"address[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"lToken","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"borrow","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"borrower","type":"address"},{"internalType":"address","name":"lToken","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"borrowBehalf","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"address","name":"lToken","type":"address"}],"name":"checkMembership","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"claimLab","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"market","type":"address"}],"name":"claimLab","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address[]","name":"accounts","type":"address[]"}],"name":"claimLabBehalf","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"closeFactor","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"lockDuration","type":"uint256"}],"name":"compoundLab","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address[]","name":"lTokens","type":"address[]"}],"name":"enterMarkets","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"lToken","type":"address"}],"name":"exitMarket","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_priceCalculator","type":"address"}],"name":"initialize","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"initialized","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"keeper","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"labDistributor","outputs":[{"internalType":"contract ILABDistributor","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"leverager","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"lTokenBorrowed","type":"address"},{"internalType":"address","name":"lTokenCollateral","type":"address"},{"internalType":"address","name":"borrower","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"liquidateBorrow","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"liquidationIncentive","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address payable","name":"lToken","type":"address"},{"internalType":"uint256","name":"supplyCap","type":"uint256"},{"internalType":"uint256","name":"borrowCap","type":"uint256"},{"internalType":"uint256","name":"collateralFactor","type":"uint256"}],"name":"listMarket","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"lToken","type":"address"}],"name":"marketInfoOf","outputs":[{"components":[{"internalType":"bool","name":"isListed","type":"bool"},{"internalType":"uint256","name":"supplyCap","type":"uint256"},{"internalType":"uint256","name":"borrowCap","type":"uint256"},{"internalType":"uint256","name":"collateralFactor","type":"uint256"}],"internalType":"struct Constant.MarketInfo","name":"","type":"tuple"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"marketInfos","outputs":[{"internalType":"bool","name":"isListed","type":"bool"},{"internalType":"uint256","name":"supplyCap","type":"uint256"},{"internalType":"uint256","name":"borrowCap","type":"uint256"},{"internalType":"uint256","name":"collateralFactor","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"marketListOf","outputs":[{"internalType":"address[]","name":"","type":"address[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"uint256","name":"","type":"uint256"}],"name":"marketListOfUsers","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"markets","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"pause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"paused","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"priceCalculator","outputs":[{"internalType":"contract IPriceCalculator","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"rebateDistributor","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"lToken","type":"address"},{"internalType":"uint256","name":"lAmount","type":"uint256"}],"name":"redeemToken","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"lToken","type":"address"},{"internalType":"uint256","name":"uAmount","type":"uint256"}],"name":"redeemUnderlying","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address payable","name":"lToken","type":"address"}],"name":"removeMarket","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"lToken","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"repayBorrow","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"newCloseFactor","type":"uint256"}],"name":"setCloseFactor","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"lToken","type":"address"},{"internalType":"uint256","name":"newCollateralFactor","type":"uint256"}],"name":"setCollateralFactor","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_keeper","type":"address"}],"name":"setKeeper","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_labDistributor","type":"address"}],"name":"setLABDistributor","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_leverager","type":"address"}],"name":"setLeverager","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"newLiquidationIncentive","type":"uint256"}],"name":"setLiquidationIncentive","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address[]","name":"lTokens","type":"address[]"},{"internalType":"uint256[]","name":"newBorrowCaps","type":"uint256[]"}],"name":"setMarketBorrowCaps","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address[]","name":"lTokens","type":"address[]"},{"internalType":"uint256[]","name":"newSupplyCaps","type":"uint256[]"}],"name":"setMarketSupplyCaps","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_priceCalculator","type":"address"}],"name":"setPriceCalculator","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_rebateDistributor","type":"address"}],"name":"setRebateDistributor","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_validator","type":"address"}],"name":"setValidator","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"lToken","type":"address"},{"internalType":"uint256","name":"uAmount","type":"uint256"}],"name":"supply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"supplier","type":"address"},{"internalType":"address","name":"lToken","type":"address"},{"internalType":"uint256","name":"uAmount","type":"uint256"}],"name":"supplyBehalf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"address","name":"src","type":"address"},{"internalType":"address","name":"dst","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transferTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"unpause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"}],"name":"usersOfMarket","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"validator","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"}]


    def enable_collateral(self, token: Token, sender: BaseAccount):
        w3 = sender.get_w3("scroll")
        contract = w3.eth.contract(self.contract_address, abi=self.abi)
        txn_data_handler = TxnDataHandler(sender, "scroll", w3=w3)

        markets = self.function_wrapper(
            contract.functions.marketListOf,
            sender.get_address(),
            "can't get market info",
            sender.get_address()
        )

        l_token = self.lend_token_from_token[token.symbol]

        if l_token.contract_address not in markets:
            txn = contract.functions.enterMarkets(
                [l_token.contract_address]
            ).build_transaction(txn_data_handler.get_txn_data(0))

            sender.send_txn(txn, "scroll")
            sleeping_sync(sender.get_address())

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

                return contract.functions.getUnderlyingPrice(l_token.contract_address).call()/10**l_token.decimals
            except Exception as e:
                logger.error(f"[{sender.get_address()}] can't get {l_token.symbol} price: {e} trying again")
                sleeping_sync(sender.get_address())
    
    def get_total_supplied(self, sender: BaseAccount):
        w3 = sender.get_w3("scroll")
        contract = w3.eth.contract(self.contract_address, abi=self.abi)

        markets = self.function_wrapper(
            contract.functions.marketListOf,
            sender.get_address(),
            "can't get market info",
            sender.get_address()
        )

        total = 0
        for contract_address in markets:
            l_token = Token("l-Token", contract_address, 18, "scroll")
            balance, human_balance = sender.get_balance(l_token)
            price = self.get_price(l_token, sender)
            total += price*balance*self.coeffs_from_contract[contract_address]
        return int(total)-1

    def get_total_borrowed(self, sender: BaseAccount):
        w3 = sender.get_w3("scroll")
        contract = w3.eth.contract(self.contract_address, abi=self.abi)

        markets = self.function_wrapper(
            contract.functions.marketListOf,
            sender.get_address(),
            "can't get market info",
            sender.get_address()
        )
        total = 0
        for contract_address in markets:
            l_token_contract = w3.eth.contract(contract_address, abi=self.ltoken_abi)
            l_token = Token("l-Token", contract_address, 18, "scroll")
            borrowed = self.function_wrapper(
                l_token_contract.functions.borrowBalanceOf,
                sender.get_address(),
                "can't get market borrowed",
                sender.get_address()
            )
            if contract_address == "0x2aD69A0Cf272B9941c7dDcaDa7B0273E9046C4B0":
                borrowed = borrowed * 1e12
            price = self.get_price(l_token, sender)
            total += price*borrowed
        return int(total)+1
    
    def how_many_can_borrow(self, sender: BaseAccount):
        total_supplied = self.get_total_supplied(sender)
        total_borrowed = self.get_total_borrowed(sender)
        return int((total_supplied-total_borrowed)*0.99)
    
    def how_many_can_remove(self, token: Token, sender: BaseAccount):
        total_supplied = self.get_total_supplied(sender)
        total_borrowed = self.get_total_borrowed(sender)
        return int((total_supplied-total_borrowed)*0.999/self.supply_coeffs[token.symbol])

    def create_txn_for_adding_token(self, token: Token, amount: float, sender: BaseAccount):
        w3 = sender.get_w3("scroll")
        contract = w3.eth.contract(self.contract_address, abi=self.abi)
        txn_data_handler = TxnDataHandler(sender, "scroll", w3=w3)
        if token.symbol == "ETH":
            value =  int(amount*10**token.decimals)
        else:
            value = 0

        self.enable_collateral(token, sender)

        token.get_approve_txn(sender, self.lend_token_from_token[token.symbol].contract_address, int(amount*10**token.decimals), w3=w3)

        txn = contract.functions.supply(
            self.lend_token_from_token[token.symbol].contract_address,
            int(amount*10**token.decimals)
        ).build_transaction(txn_data_handler.get_txn_data(value))

        return txn
    
    def create_txn_for_removing_token(self, token: Token, sender: BaseAccount):
        w3 = sender.get_w3("scroll")
        contract = w3.eth.contract(self.contract_address, abi=self.abi)
        txn_data_handler = TxnDataHandler(sender, "scroll", w3=w3)

        can_remove = self.how_many_can_remove(token, sender)/self.get_price(token, sender)
        amount = token.balance_of(sender.address, w3=w3)[0] - 1
        if amount > can_remove:
            amount = int(can_remove - 1)

        if amount <= 1:
            logger.error(f"[{sender.get_address()}] can't remove any tokens")
            return -1

        txn = contract.functions.redeemToken(
            token.contract_address,
            amount
        ).build_transaction(txn_data_handler.get_txn_data())
        return txn
    
    def create_txn_to_borrow_token(self, amount: float, token: Token, sender: BaseAccount):
        w3 = sender.get_w3("scroll")
        contract = w3.eth.contract(self.contract_address, abi=self.abi)
        txn_data_handler = TxnDataHandler(sender, "scroll", w3=w3)
        l_token = self.lend_token_from_token[token.symbol]
        borrow_limit = self.how_many_can_borrow(sender)/self.get_price(l_token, sender)
        if borrow_limit <= 1:
            logger.error(f"[{sender.get_address()}] can't borrow any tokens.")
            return -1
        
        if amount*10**token.decimals > borrow_limit:
            amount = int(borrow_limit - 1)
            logger.info(f"[{sender.get_address()}] amount out of borrow limits. Will borrow only {amount/10**token.decimals} {token.symbol}")
        else:
            amount = int(amount*10**token.decimals)

        txn = contract.functions.borrow(
            l_token.contract_address,
            amount
        ).build_transaction(txn_data_handler.get_txn_data())

        return txn
        

    def create_txn_to_repay_token(self, token: Token, sender: BaseAccount):
        w3 = sender.get_w3("scroll")
        contract = w3.eth.contract(self.contract_address, abi=self.abi)
        txn_data_handler = TxnDataHandler(sender, "scroll", w3=w3)
        l_token = self.lend_token_from_token[token.symbol]
        l_token_contract = w3.eth.contract(l_token.contract_address, abi=self.ltoken_abi)

        borrowed = self.function_wrapper(
            l_token_contract.functions.borrowBalanceOf,
            sender.get_address(),
            "can't get market borrowed",
            sender.get_address()
        )

        if borrowed <= 1:
            logger.info(f"[{sender.get_address()}] borrowed amount of {token.symbol} is 0")
            return -1
        
        logger.info(f"[{sender.get_address()}] going to repay {token.symbol}")

        balance, human_balance = sender.get_balance(token)
        if balance > borrowed:
            to_repay = borrowed - 2
        else:
            to_repay = balance - 2
        token.get_approve_txn(sender, l_token.contract_address, to_repay, w3=w3)

        if token.symbol == "ETH":
            value = to_repay
        else:
            value = 0

        txn = contract.functions.repayBorrow(
            l_token.contract_address,
            to_repay
        ).build_transaction(txn_data_handler.get_txn_data(value=value))

        return txn

