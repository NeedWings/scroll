from DEXes.merkly import *
from DEXes.scrollswap import *
from DEXes.spacefi import *
from DEXes.syncswap import *
from DEXes.skydrome import *
from own_tasks import *
from token_stor import *
from DEXes.dmail import *
from bridger import Bridger
from rhino import *
dmail_hand = Dmail()
merkly_hand = Merkly()
swap_dexes = [
    ScrollSwap(),
    Skydrome(),
    SpaceFi(),
    SyncSwap()
]


liq_dexes = [
    ScrollSwap(),
    Skydrome(),
    SpaceFi()
]

lends = [

]

supported_dexes_for_swaps = []
supported_dexes_for_liq = []
supported_lends = []
suppotred_tokens = []

for name in SETTINGS["SwapDEXs"]:
    for dex in swap_dexes:
        if dex.name == name:
            supported_dexes_for_swaps.append(dex)


for name in SETTINGS["LiqDEXs"]:
    for dex in liq_dexes:
        if dex.name == name:
            supported_dexes_for_liq.append(dex)


#for name in SETTINGS["Lends"]:
#    for dex in lends:
#        if dex.name == name:
#            supported_lends.append(dex)
        
for name in SETTINGS["Supported_tokens"]:
    for token in tokens:
        if token.symbol == name:
            suppotred_tokens.append(token)


class MainRouter():
    def __init__(self, private_key: str, delay: int, task_number: int) -> None:
        self.task_number = task_number
        self.account = Account(private_key)
        self.bridger = Bridger(self.account)
        self.delay = delay
        indexes.append(self.account.get_address())

    
    def start(self):
        sleep(self.delay)
        task_number = self.task_number
        
        if task_number == 0:
            own_tasks(self)
        elif task_number == 12:
            self.deploy_contracts()
        elif task_number == 1:
            self.bridger.main_handler("simple")
        elif task_number == 2:
            self.bridger.main_handler("stargate")
        elif task_number == 3:
            self.bridger.main_handler("withdraw")
        elif task_number == 4:
            self.swaps_handler()
        elif task_number == 5:
            self.swap_to_one_token(random.choice(SETTINGS["toSaveFunds"]))
        elif task_number == 6:
            self.liq_handler()
        elif task_number == 7:
            self.remove_liq()
        elif task_number == 8:
            self.merkly()
        elif task_number == 9:
            self.dmail()
        elif task_number == 10:
            self.full()

    def full_withdraw(self):
        self.remove_liq()
        self.swap_to_one_token()
        self.bridger.main_handler("withdraw")


    def deploy_contracts(self):
         try:
            w3 = Web3(Web3.HTTPProvider(random.choice(RPC_LSIT["scroll"])))
            txn_data_handler = EVMTransactionDataHandler(self.account, "scroll")
            source = random.choice(SETTINGS["contract_for_deploy"])
            logger.info(f"[{self.account.address}] going to deploy contract by {source} source code")
            bytecode, abi = CONTRACTS_FOR_DEPLOY[source][0], CONTRACTS_FOR_DEPLOY[source][1]
            contract = w3.eth.contract(bytecode=bytecode, abi=abi)

            txn = contract.constructor().build_transaction(txn_data_handler.get_txn_data())
            self.account.send_txn([txn], "scroll")
        except Exception as e:
            logger.error(f"[{self.account.get_address()}] got erroor: {e}")
        sleeping_sync(self.account.address)


    def dmail(self):
        amount = get_random_value_int(SETTINGS["dmail_messages_amount"])
        for qawe in range(amount):
            
            calldata = dmail_hand.send_msg(self.account)

            self.account.send_txn(calldata, "scroll")

            sleeping_sync(self.account.get_address())

    def get_max_valued_token(self, tokens: List[EVMToken]):
        max_valued = None
        max_value = 0
        for token in tokens:
            balance = self.account.get_balance(token)[0]
            if token.symbol == "ETH":
                balance = balance - get_random_value(SETTINGS["SaveEthOnBalance"])*1e18
                logger.info(f"[{self.account.get_address()}] {token.symbol} balance: {balance/10**token.decimals}")
            else:
                if balance/10**token.decimals < SETTINGS["MINIMAL_SWAP_AMOUNTS"][token.symbol]:
                    balance = 0
                    logger.info(f"[{self.account.get_address()}] {token.symbol} balance below MINIMAL_SWAP_AMOUNTS, will count as 0")
                else:
                    logger.info(f"[{self.account.get_address()}] {token.symbol} balance: {balance/10**token.decimals}")
            usd_value = token.get_usd_value(balance/10**token.decimals)
            if usd_value>max_value:
                max_valued = token
                max_value = usd_value
        return max_valued, max_value

    def supported_tokens_str_to_token(self, tokens):
        res = []
        for token in tokens:
            res.append(tokens_dict[token])

        return res
    
    def full(self):
        ways = [1, 2, 4]
        shuffle(ways)
        for way in ways:
            print(way)
            if way == 1:
                self.swaps_handler()
            elif way == 2:
                self.liq_handler()
                if random.choice(SETTINGS["RemoveOnFullMode"]):
                    self.remove_liq()
            elif way == 4:
                self.dmail()
            
        if random.choice(SETTINGS["SwapAtTheEnd"]):
            self.swap_to_one_token(random.choice(SETTINGS["toSaveFunds"]))

    def merkly(self):
        amount = get_random_value_int(SETTINGS["merkly_mint/bridge_amount"])
        for i in range(amount):
            mint_txn = merkly_hand.create_txn_for_mint(self.account)

    def swaps_handler(self):
        swap_amount = get_random_value_int(SETTINGS["swapAmounts"])
        if swap_amount < 1:
            return
        s = list(range(swap_amount))
        for i in s:
            try:
                dex: BaseDex = random.choice(supported_dexes_for_swaps)
                token1, usd_value = self.get_max_valued_token(self.supported_tokens_str_to_token(dex.supported_tokens))
                if token1 == None:
                    logger.error(f"[{self.account.get_address()}] all balances is 0")
                    continue
                token1: EVMToken = token1
                token2 = tokens_dict[dex.get_pair_for_token(token1.symbol)]
                
                amount_to_swap = usd_value * get_random_value(SETTINGS["WorkPercent"])
                
                token1_val = amount_to_swap/token1.get_price()
                token2_val = amount_to_swap/token2.get_price()
                logger.info(f"[{self.account.get_address()}] going to swap {token1_val} {token1.symbol} for {token2.symbol} in {dex.name}")

                swap_txn = dex.create_txn_for_swap(token1_val, token1, token2_val, token2, self.account)
                if swap_txn == 5555:
                    s.append(len(s))
                    sleeping_sync(self.account.get_address(), True)
                    continue

                self.account.send_txn(swap_txn, "scroll")
                sleeping_sync(self.account.get_address())

            except Exception as e:
                logger.error(f"[{self.account.get_address()}] got erroor: {e}")
                sleeping_sync(self.account.get_address(), True)
    
    def liq_handler(self):
        liq_amount = get_random_value_int(SETTINGS["AddLiqAmount"])
        if liq_amount < 1:
            return
        
        for i in range(liq_amount):
            try:
                dex: BaseDex = random.choice(supported_dexes_for_liq)
                token1, usd_value = self.get_max_valued_token(self.supported_tokens_str_to_token(dex.supported_tokens))
                if token1 == None:
                    logger.error(f"[{self.account.get_address()}] all balances is 0")
                    continue
                token1: EVMToken = token1
                token2 = dex.get_pair_for_token(token1.symbol)

                if token2 == -5:
                    continue
                token2: EVMToken = tokens_dict[token2]
                amount_to_add = usd_value * get_random_value(SETTINGS["LiqWorkPercent"])/2
                token2_usd_value = token2.get_usd_value(self.account.get_balance(token2)[1])
                amount1 = amount_to_add/token1.get_price()
                amount2 = amount_to_add/token2.get_price()
                logger.info(f"[{self.account.get_address()}] going to add liquidity in {dex.name} in {token1.symbol}/{token2.symbol} pair for {amount1} {token1.symbol} and {amount2} {token2.symbol}")
                
                if token2_usd_value < amount_to_add*(1+ SETTINGS["Slippage"]+0.01):
                    logger.info(f"[{self.account.get_address()}] not enough second token for adding, will make swap")
                    
                    amount_to_swap = amount_to_add*(1+ SETTINGS["Slippage"]+0.01) - token2_usd_value
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

    

    def swap_to_one_token(self, token = "ETH"):
        token = tokens_dict[token]
        tokens = suppotred_tokens.copy() 
        shuffle(tokens)
        for token_to_swap in tokens:
            try:
                token_to_swap: EVMToken
                if token == token_to_swap:
                    continue

                balance = self.account.get_balance(token_to_swap)[0]

                if token_to_swap.symbol == "ETH":
                    balance -= int(get_random_value(SETTINGS["SaveEthOnBalance"])*1e18)
                else:
                    if balance/10**token_to_swap.decimals < SETTINGS["MINIMAL_SWAP_AMOUNTS"][token_to_swap.symbol]:
                        balance = 0

                if balance <=0:
                    logger.info(f"[{self.account.get_address()}] {token_to_swap.symbol} balance 0 or less MINIMAL_SWAP_AMOUNTS. skip")
                    continue
                selected = False
                for i in range(10):
                    dex: BaseDex = random.choice(supported_dexes_for_swaps)
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

    def remove_liq(self):
        dexes = supported_dexes_for_liq.copy()
        shuffle(dexes)
        for dex in dexes:
            dex: BaseDex
            lptokens = dex.lpts.copy()
            shuffle(lptokens)
            for lpt in lptokens:
                lpt: EVMToken
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

    
