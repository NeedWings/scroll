from abc import ABC, abstractmethod
from cfg import *

def req(url: str, **kwargs):
    while True:
        try:
            resp = requests.get(url, **kwargs)
            if resp.status_code == 200:
                return resp.json()
            else:
                logger.error("Bad status code, will try again")
                pass
        except Exception as error:
            logger.error(f"Requests error: {error}")
        time.sleep(get_random_value(SETTINGS["ErrorSleepeng"]))

def handle_error(account):
    def actual_dec(func):
        def wrapper(*args, **kwargs):
            for i in range(5):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"[{account.get_address()}] got error: {e}, trying again")
                    sleeping_sync(account.get_address(), True)
            logger.error(f"[{account.get_address()}] retries 5. skip")
            return 5555
            
        return wrapper
    return actual_dec

class EVMTransactionDataHandler():
    
    def __init__(self, sender, net_name) -> None:
        self.address = sender.get_address()
        self.net_name = net_name
        self.w3 = Web3(Web3.HTTPProvider(random.choice(RPC_LSIT[net_name])))
    
    def get_gas_price(self):
        
        max_gas = Web3.to_wei(SETTINGS.get("GWEI").get(self.net_name), 'gwei')

        while True:
            try:
                gas_price = self.w3.eth.gas_price
                if gas_price > max_gas:
                    h_gas, h_max = Web3.from_wei(gas_price, 'gwei'), Web3.from_wei(max_gas, 'gwei')
                    logger.error(f'[{self.address}] Sender net: {self.net_name}. Current gasPrice: {h_gas} | Max gas price: {h_max}')
                    sleeping_sync(f'[{self.address}] Waiting best gwei. Update after ')
                else:
                    return round(gas_price)
                
            except Exception as error:
                logger.error(f'[{self.address}] Error: {error}')
                sleeping_sync(f'[{self.address}] Error fault. Update after ')


    def get_txn_data(self, value=0):
        gas_price = self.get_gas_price()


        data = {
            'chainId': self.w3.eth.chain_id, 
            'nonce': self.w3.eth.get_transaction_count(self.address),  
            'from': self.address, 
            "value": value
        }


        if self.net_name in ["avalanche", "polygon", "arbitrum", "ethereum", "base"]:
            data["type"] = "0x2"


        if self.net_name not in ['arbitrum', "avalanche", "polygon", "ethereum", "base"]:
            data["gasPrice"] = gas_price
            
        else:
            data["maxFeePerGas"] = gas_price
            if self.net_name == "polygon":
                data["maxPriorityFeePerGas"] = Web3.to_wei(30, "gwei")
            elif self.net_name == "avalanche" or self.net_name == "base":
                data["maxPriorityFeePerGas"] = gas_price
            elif self.net_name == "ethereum":
                data["maxPriorityFeePerGas"] = Web3.to_wei(0.05, "gwei")
            elif self.net_name == "arbitrum":
                data["maxPriorityFeePerGas"] = Web3.to_wei(0.01, "gwei")
        return data

class BaseAccount(ABC):

    @abstractmethod
    def send_txn(self, txns, net):
        """sends transaction"""
        pass
    
    @abstractmethod
    def get_address(self):
        "returns address"
        pass

    @abstractmethod
    def get_balance(self, token):
        pass

class EVMToken():
    def __init__(self, symbol, contract_address, decimals, net, stable = False) -> None:
        self.net_name = net
        self.w3 = Web3(Web3.HTTPProvider(random.choice(RPC_LSIT[net])))
        self.decimals = decimals
        self.symbol = symbol
        self.contract_address = contract_address
        self.contract = self.w3.eth.contract(contract_address, abi=ERC20_ABI)
        self.stable = stable

    def get_balance(self, address, of_wrapped = False):
        while True:
            try:
                balance = self.contract.functions.balanceOf(address).call()
                human_balance = balance/10**self.decimals
                return balance, human_balance
            except Exception as e:
                logger.error(f"[{address}] can't get balance of {self.symbol}: {e}")
                sleeping_sync(address, True)

    
    def get_approve_txn(self, sender: BaseAccount, spender, amount):
        @handle_error(account=sender)
        def buff():
            txn_data_handler = EVMTransactionDataHandler(sender, self.net_name)
            txn = self.contract.functions.approve(spender, amount).build_transaction(
                                txn_data_handler.get_txn_data()
                            )
            
            sender.send_txn([txn], self.net_name)
            t = get_random_value(SETTINGS["ApproveSleep"])
            logger.info(f"[{sender.get_address()}] sleeping {t} s")
            sleep(t)
            return None
        return buff()
    
    def get_price(self):
        if self.stable:
            return 1
        else:
            def __find__(ticker: str, rates: list):
                for k in rates:
                    name = k.get("symbol")
                    if name == ticker.upper() + 'USDT':
                        return float(k.get("price"))
            while True:
                response = req("https://api.binance.com/api/v3/ticker/price")
                if type(response) is list:
                    return __find__(self.symbol, response)
                else:
                    print(f'Cant get response from binance, tring again...')
                    time.sleep(5)

    def get_usd_value(self, amount):
        return self.get_price()*amount
        
            

class EVMNativeToken(EVMToken):
    def __init__(self, net) -> None:
        self.net_name = net
        self.w3 = Web3(Web3.HTTPProvider(random.choice(RPC_LSIT[net])))
        self.decimals = 18
        self.symbol = NATIVE_TOKENS_SYMBOLS[net]
        self.contract_address = NATIVE_WRAPPED_CONTRACTS[net]
        self.abi = [{"anonymous": False,"inputs":[{"indexed": True,"internalType":"address","name":"src","type":"address"},{"indexed": True,"internalType":"address","name":"guy","type":"address"},{"indexed": False,"internalType":"uint256","name":"wad","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous": False,"inputs":[{"indexed": True,"internalType":"address","name":"dst","type":"address"},{"indexed": False,"internalType":"uint256","name":"wad","type":"uint256"}],"name":"Deposit","type":"event"},{"anonymous": False,"inputs":[{"indexed": True,"internalType":"address","name":"src","type":"address"},{"indexed": True,"internalType":"address","name":"dst","type":"address"},{"indexed": False,"internalType":"uint256","name":"wad","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous": False,"inputs":[{"indexed": True,"internalType":"address","name":"src","type":"address"},{"indexed": False,"internalType":"uint256","name":"wad","type":"uint256"}],"name":"Withdrawal","type":"event"},{"payable": True,"stateMutability":"payable","type":"fallback"},{"constant": True,"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable": False,"stateMutability":"view","type":"function"},{"constant": False,"inputs":[{"internalType":"address","name":"guy","type":"address"},{"internalType":"uint256","name":"wad","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable": False,"stateMutability":"nonpayable","type":"function"},{"constant": True,"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable": False,"stateMutability":"view","type":"function"},{"constant": True,"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"payable": False,"stateMutability":"view","type":"function"},{"constant": False,"inputs":[],"name":"deposit","outputs":[],"payable": True,"stateMutability":"payable","type":"function"},{"constant": True,"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"payable": False,"stateMutability":"view","type":"function"},{"constant": True,"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"payable": False,"stateMutability":"view","type":"function"},{"constant": True,"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable": False,"stateMutability":"view","type":"function"},{"constant": False,"inputs":[{"internalType":"address","name":"dst","type":"address"},{"internalType":"uint256","name":"wad","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable": False,"stateMutability":"nonpayable","type":"function"},{"constant": False,"inputs":[{"internalType":"address","name":"src","type":"address"},{"internalType":"address","name":"dst","type":"address"},{"internalType":"uint256","name":"wad","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable": False,"stateMutability":"nonpayable","type":"function"},{"constant": False,"inputs":[{"internalType":"uint256","name":"wad","type":"uint256"}],"name":"withdraw","outputs":[],"payable": False,"stateMutability":"nonpayable","type":"function"}]
        self.contract = self.w3.eth.contract(self.contract_address, abi=self.abi)
        self.stable = False



    def get_balance(self, address, of_wrapped = False):

        while True:
            try:
                if not of_wrapped:
                    balance = self.w3.eth.get_balance(address)
                    human_balance = balance/10**self.decimals
                    return balance, human_balance
                else:
                    balance = self.contract.functions.balanceOf(address).call()
                    human_balance = balance/10**self.decimals
                    return balance, human_balance
            except Exception as e:
                logger.error(f"[{address}] can't get balance of {self.symbol}: {e}")
                sleeping_sync(address, True)

    


    def create_unwrap_txn(self, sender):
        txn_data_handler = EVMTransactionDataHandler(sender, self.net_name)
        while True:
            try:
                amount = self.contract.functions.balanceOf(sender.get_address()).call()
                break
            except Exception as e:
                logger.error(f"[{sender.get_address()}] can't get balance of W{self.symbol}: {e}")
                sleeping_sync(sender.get_address(), True)
        if amount <= 1:
            return None
        txn = self.contract.functions.withdraw(
            amount
        ).build_transaction(txn_data_handler.get_txn_data())
        return txn
    
    def create_wrap_txn(self, wei: bool, amount, sender):
        txn_data_handler = EVMTransactionDataHandler(sender, self.net_name)
        if not wei:
            amount = int(amount*10**self.decimals)
        txn = self.contract.functions.deposit().build_transaction(txn_data_handler.get_txn_data(amount))

        return txn

    def get_approve_txn(self, address, spender, amount):
        return None
    
    def get_approve_txn_wrapped(self, wei, sender: BaseAccount, spender, amount):
        @handle_error(account=sender)
        def buff(amount):
            if not wei:
                amount = int(amount*10**self.decimals)
            txn_data_handler = EVMTransactionDataHandler(sender, self.net_name)
            txn = self.contract.functions.approve(spender, amount).build_transaction(
                                txn_data_handler.get_txn_data()
                            )
            
            
            sender.send_txn([txn], self.net_name)
            t = get_random_value(SETTINGS["ApproveSleep"])
            logger.info(f"[{sender.get_address()}] sleeping {t} s")
            sleep(t)
            return None
        return buff(amount)




class Account(BaseAccount):
    def __init__(self, private_key: str):
        self.private_key = private_key
        self.address = ethAccount.from_key(private_key).address
        self.formatted_hex_address = self.address

    def get_address(self):
        return self.address
    
    def get_balance(self, token):
        return token.get_balance(self.address)
    
    def send_txn(self, txns, net):
        for txn in txns:

            if txn == None:
                continue
            w3 = Web3(Web3.HTTPProvider(random.choice(RPC_LSIT[net])))

            gasEstimate = w3.eth.estimate_gas(txn)

            txn['gas'] = round(gasEstimate*1.5) 
            signed_txn = w3.eth.account.sign_transaction(txn, private_key=self.private_key)
            tx_token = w3.to_hex(w3.eth.send_raw_transaction(signed_txn.rawTransaction))

            logger.success(f"[{self.address}] sending txn: {tx_token}")
            success = self.wait_until_txn_finished(tx_token, net)
            return success, signed_txn, tx_token

    
    def wait_until_txn_finished(self, hash, net, max_time = 500):
        w3 = Web3(Web3.HTTPProvider(random.choice(RPC_LSIT[net])))
        start_time = time.time()
        while True:
            try:
                if time.time() - start_time > max_time:
                    logger.error(f'[{self.address}] {hash} transaction is failed (timeout)')
                    return False
                receipts = w3.eth.get_transaction_receipt(hash)
                status = receipts.get("status")

                if status == 1:
                    logger.success(f"[{self.address}] {hash} is completed")
                    return True
                elif status is None:
                    #print(f'[{hash}] still processed')
                    sleep(0.3)
                elif status != 1:
                    logger.error(f'[{self.address}] [{hash}] transaction is failed')
                    return False
            except:
                #print(f"[{hash}] still in progress")
                sleep(1)         



class BaseDex(ABC):
    name = None
    supported_tokens = []
    lpts = []
    contract_address_lp = None
    def __init__(self) -> None:
        new_supported_tokens = []
        for token in self.supported_tokens:
            if token in SETTINGS["Supported_tokens"]:
                new_supported_tokens.append(token)
        self.supported_tokens = new_supported_tokens

    @abstractmethod
    def create_txn_for_swap(self, amount_in: float, token1: EVMToken, amount_out: float, token2: EVMToken, sender: BaseAccount, full: bool = False, native_first: bool = False):
        pass

    @abstractmethod
    def create_txn_for_liq(self, amount1: float, token1: EVMToken, amount2: float, token2: EVMToken, sender: BaseAccount):
        pass

    @abstractmethod
    def create_txn_for_remove_liq(self, lptoken: EVMToken, sender: BaseAccount):
        pass

    def get_pair_for_token(self, token: str):
        for i in range(20):
            pair = random.choice(self.supported_tokens)
            if token != pair:
                return pair
        logger.error("Can't find pair for token")
        return -5
    
class BaseLend(ABC):
    contract_address = None
    name = None
    supported_tokens = []
    lend_tokens = []
    @abstractmethod
    async def create_txn_for_adding_token(self, token: EVMToken, amount: float, sender: BaseAccount):
        pass

    @abstractmethod
    async def create_txn_for_removing_token(self, amount: int, token: EVMToken, sender: BaseAccount):
        pass

    @abstractmethod
    async def create_txn_for_borrow(self, amount: float, token: EVMToken, sender: BaseAccount):
        pass
    
    @abstractmethod
    async def create_txn_for_return(self, token: EVMToken, sender: BaseAccount):
        pass
