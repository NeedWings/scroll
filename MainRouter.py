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
    def __init__(self, private_key: str, delay: int, task_number: int, proxy=None) -> None:
        self.task_number = task_number
        self.account = Account(private_key, proxy=proxy)
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
        elif task_number == 13:
            self.zkstars()
        elif task_number == 14:
            self.scroll_origins()

    def zkstars(self):
        amount = get_random_value_int(SETTINGS["zkstars_amount"])
        contracts = """0x609c2f307940B8f52190b6D3D3A41C762136884E
0x16c0Baa8a2aA77fab8d0aeCe9B6947EE1b74B943
0xc5471e35533E887f59Df7A31F7C162Eb98F367F7
0xF861f5927C87bC7C4781817b08151d638dE41036
0x954E8AC11c369ef69636239803a36146BF85e61B
0xa576aC0A158EBDCC0445e3465adf50E93dD2CAd8
0x17863384C663c5f95e4e52D3601F2FF1919ac1aA
0x4C2656a6D1c0ecac86f5024e60d4F04DBB3d1623
0x4E86532CEDF07c7946e238bD32Ba141b4ed10c12
0x6b9db0FfCb840C3D9119B4fF00F0795602c96086
0x10D4749Bee6a1576AE5E11227BC7F5031aD351e4
0x373148e566E4c4C14f4eD8334aBa3a0Da645097a
0xDacbAc1C25d63B4B2B8BfDBF21C383e3CCFF2281
0x2394b22B3925342F3216360b7b8F43402E6A150b
0xf34f431E3fC0aD0D2beb914637b39f1ecf46c1Ee
0x6f1E292302DCe99e2A4681bE4370D349850Ac7C2
0xA21faC8b389f1f3717957a6BB7d5Ae658122fc82
0x1b499d45E0Cc5e5198b8A440f2D949F70E207A5D
0xEC9bEF17876D67de1F2EC69F9a0E94De647FcC93
0x5e6c493Da06221fed0259a49bEac09EF750C3De1""".split("\n")
        for i in range(amount):
            addr = random.choice(contracts)
            w3 = self.account.get_w3('scroll')
            contract =  w3.eth.contract(addr, abi = [{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"string","name":"baseURI_","type":"string"},{"internalType":"uint256","name":"ref_precent_","type":"uint256"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"},{"internalType":"address","name":"owner","type":"address"}],"name":"ERC721IncorrectOwner","type":"error"},{"inputs":[{"internalType":"address","name":"operator","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"ERC721InsufficientApproval","type":"error"},{"inputs":[{"internalType":"address","name":"approver","type":"address"}],"name":"ERC721InvalidApprover","type":"error"},{"inputs":[{"internalType":"address","name":"operator","type":"address"}],"name":"ERC721InvalidOperator","type":"error"},{"inputs":[{"internalType":"address","name":"owner","type":"address"}],"name":"ERC721InvalidOwner","type":"error"},{"inputs":[{"internalType":"address","name":"receiver","type":"address"}],"name":"ERC721InvalidReceiver","type":"error"},{"inputs":[{"internalType":"address","name":"sender","type":"address"}],"name":"ERC721InvalidSender","type":"error"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"ERC721NonexistentToken","type":"error"},{"inputs":[],"name":"ReentrancyGuardReentrantCall","type":"error"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"approved","type":"address"},{"indexed":true,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"operator","type":"address"},{"indexed":false,"internalType":"bool","name":"approved","type":"bool"}],"name":"ApprovalForAll","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":true,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Transfer","type":"event"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"approve","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"getApproved","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getPrice","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getRefPercent","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"operator","type":"address"}],"name":"isApprovedForAll","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"ownerOf","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address payable","name":"ref","type":"address"}],"name":"safeMint","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"safeTransferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"safeTransferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"operator","type":"address"},{"internalType":"bool","name":"approved","type":"bool"}],"name":"setApprovalForAll","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"newPrice","type":"uint256"}],"name":"setPrice","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"newPercent","type":"uint256"}],"name":"setRefPercent","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes4","name":"interfaceId","type":"bytes4"}],"name":"supportsInterface","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"tokenURI","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"transferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address payable","name":"to","type":"address"}],"name":"withdraw","outputs":[],"stateMutability":"nonpayable","type":"function"}])
            txn_data_handler = EVMTransactionDataHandler(self.account, "scroll")
            try:
                if SETTINGS["use_ref_for_zkstars"]:
                    ref = Web3.to_checksum_address(SETTINGS["ref_for_zkstars"])
                else:
                    ref = addr
                logger.info(f"[{self.account.address}] going to mint zkstars nft")
                txn = contract.functions.safeMint(ref).build_transaction(txn_data_handler.get_txn_data(int(0.0001*1e18)))
                self.account.send_txn([txn], "scroll")
                sleeping_sync(self.account.address)
            except Exception as e:
                logger.error(f"[{self.account.address}] got error: {e}")
                sleeping_sync(self.account.address, True)

    def scroll_origins(self):
        try:
            contract_address = "0x74670A3998d9d6622E32D0847fF5977c37E0eC91"
            w3 = self.account.get_w3("scroll")
            contract = w3.eth.contract(contract_address, abi=SCROLL_ORIGINS)
            txn_data_handler = EVMTransactionDataHandler(self.account, "scroll")


            mint_data = req(f"https://nft.scroll.io/p/{self.account.address}.json?timestamp={int(time.time()*1000)}")

            try:
                best_deployed = mint_data["metadata"]["bestDeployedContract"]
                first_deployed = mint_data["metadata"]["firstDeployedContract"]
                rarity_data = mint_data["metadata"]["rarityData"]
                proof = mint_data["proof"]
            except Exception as e:
                logger.info(f"[{self.account.address}] most likely not eligible: {e}")
                return
            
            txn = contract.functions.mint(
                self.account.address,
                (
                    self.account.address,
                    first_deployed,
                    best_deployed,
                    int(rarity_data, 16)
                ),
                list(map(bytes.fromhex, list(map(lambda x: x[2::], proof))))
            ).build_transaction(txn_data_handler.get_txn_data())

            self.account.send_txn([txn], "scroll")
        except Exception as e:
            logger.error(f"[{self.account.address}] got error: {e}")

    def full_withdraw(self):
        self.remove_liq()
        self.swap_to_one_token()
        self.bridger.main_handler("withdraw")


    def deploy_contracts(self):
        w3 = self.account.get_w3('scroll')
        txn_data_handler = EVMTransactionDataHandler(self.account, "scroll")
        source = random.choice(SETTINGS["contract_for_deploy"])
        logger.info(f"[{self.account.address}] going to deploy contract by {source} source code")
        bytecode, abi = CONTRACTS_FOR_DEPLOY[source][0], CONTRACTS_FOR_DEPLOY[source][1]
        contract = w3.eth.contract(bytecode=bytecode, abi=abi)

        txn = contract.constructor().build_transaction(txn_data_handler.get_txn_data())
        self.account.send_txn([txn], "scroll")
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

    
