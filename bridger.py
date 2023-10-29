from BaseClasses import *
from token_stor import *
from DEXes.sushiswap import SushiSwap




class Bridger:
    chains = ["bsc", "arbitrum", "ethereum", "optimism", "avalanche", "polygon"]
    native_chains = ["ethereum", "arbitrum"]
    STARGATE_CONTRACTS = {
        'avalanche' : '0x45A01E4e04F14f7A4a6702c74187c5F6222033cd',
        'polygon'   : '0x45A01E4e04F14f7A4a6702c74187c5F6222033cd',
        'bsc'       : '0x4a364f8c717cAAD9A442737Eb7b8A55cc6cf18D8',
        'arbitrum'  : '0x53Bf833A5d6c4ddA888F69c22C88C9f356a41614',
        'optimism'  : '0xB0D502E938ed5f4df2E681fE6E419ff29631d62b',
        'ethereum'  : '0x8731d54E9D02c286767d56ac03e8037C07e01e98'
    }

    LAYERZERO_CHAINS_ID = {
        'avalanche' : 106,
        'polygon'   : 109,
        'ethereum'  : 101,
        'bsc'       : 102,
        'arbitrum'  : 110,
        'optimism'  : 111,
        'fantom'    : 112
    }

    STARGATE_ASSET_TYPES = {
        "USDT" : 2,
        "USDC" : 1
    }
    ORBITER_CHAIN_CODES = {
        "arbitrum": 9002,
        "ethereum": 9001,
        "scroll": 9019
    }

    ORBITER_WITHDRAW_FEE = {
        "arbitrum": 0.0013,
        "ethereum": 0.005
    }
    account: BaseAccount = None

    

    def __init__(self, account: BaseAccount) -> None:
        self.account = account

    def get_max_valued_token(self):
        token: EVMToken = None
        value: float = 0.0
        for chain in self.chains:
            for stable in chains_tokens[chain]:
                balance = self.account.get_balance(stable)[1]
                logger.info(f"[{self.account.get_address()}] ({chain}) {stable.symbol} balance: {balance}")
                if balance < SETTINGS["minUSDamount"]:
                    continue
                if balance > value:
                    value = balance
                    token = stable
        
        return token, value
    
    def quote_layer_zero_fee(self, dist_chain_name: str, sender_net: str, contract):
        while True:
            try:
                chain_id = self.LAYERZERO_CHAINS_ID[dist_chain_name]

                comission = contract.functions.quoteLayerZeroFee(
                    chain_id, 1, 
                    get_bytes(self.account.get_address().split("0x")[1]),
                    get_bytes(self.account.get_address().split("0x")[1]), 
                        (
                            0, 0, 
                            get_bytes(ZERO_ADDRESS.split("0x")[1])
                        )
                ).call()[0]
                human_readable = round(Web3.from_wei(comission, 'ether'), 7)

                if human_readable > SETTINGS["FEES"][sender_net]:
                    logger.info(f'[{self.account.get_address()}] Got fee to way:{sender_net}->{dist_chain_name}: {human_readable} Fee is to high')
                    sleeping_sync(self.account.get_address(), True)
                else:
                    logger.info(f'[{self.account.get_address()}] Got fee to way:{sender_net}->{dist_chain_name} : {human_readable} ')
                    return comission
                
            except Exception as error:
                logger.error(f'[{self.account.get_address()}] Cant get L0 fees: {error}')
                sleeping_sync(self.account.get_address(), True)

    def stargate(self, src_chain: str, dist_chain: str, src_token: EVMToken, value: float):
        @handle_error(account=self.account)
        def buff():
            txn_data_handler = EVMTransactionDataHandler(self.account, src_chain)
            
            dist_token = random.choice(chains_tokens[dist_chain])
            real_value = get_random_value(SETTINGS["USDAmountToBridge"])
            if real_value > value:
                real_value = value

            w3: Web3 = Web3(Web3.HTTPProvider(random.choice(RPC_LSIT[src_chain])))
            contract = w3.eth.contract(self.STARGATE_CONTRACTS[src_chain], abi=STARGATE_ABI)

            fee = self.quote_layer_zero_fee(dist_chain, src_chain, contract)

            min_recv_amount = value * 0.998

            approve_txn = src_token.get_approve_txn(self.account, self.STARGATE_CONTRACTS[src_chain], int(value*10**src_token.decimals))

            txn = contract.functions.swap(
                    self.LAYERZERO_CHAINS_ID[dist_chain],
                    self.STARGATE_ASSET_TYPES[src_token.symbol], self.STARGATE_ASSET_TYPES[dist_token.symbol], self.account.get_address(),
                    int(value*10**src_token.decimals), int(min_recv_amount*10**src_token.decimals),
                    (0, 0, "0x0000000000000000000000000000000000000001"),
                    self.account.get_address().lower(), b''
                ).build_transaction(txn_data_handler.get_txn_data(int(fee)))
            
            return [approve_txn, txn]
        return buff()
        

    def bridge_stables(self, dist_chain):
        @handle_error(account=self.account)
        def buff():
            while True:
                token, value = self.get_max_valued_token()
                if token:
                    break
                logger.info(f"[{self.account.get_address()}] can't find any stables. keep looking")
                rand_time = SETTINGS["ParsingSleep"]
                logger.info(f'[{self.account.get_address()}] sleeping {rand_time} s')
                time.sleep(rand_time)
            src_chain = token.net_name
            logger.info(f"[{self.account.get_address()}] found balance: ({src_chain}) {value} {token.symbol}")


            if src_chain in SETTINGS["nets_for_deposit"]:
                logger.info(f"[{self.account.get_address()}] funds already in {src_chain}")
                return src_chain, token
            
            bridge_txn = self.stargate(src_chain, dist_chain, token, value)
            if bridge_txn == 5555:
                return 5555
            logger.info(f"[{self.account.get_address()}] going to bridge {value} {token.symbol} from {src_chain} to {dist_chain}")
            self.account.send_txn(bridge_txn, src_chain)
            return 1
        return buff()
    
    def swap_stables_to_eth(self, token):
        @handle_error(account=self.account)
        def buff():
            sushi = SushiSwap()
            balance = self.account.get_balance(token)[1]
            real_value = get_random_value(SETTINGS["USDAmountToBridge"])
            if real_value > balance:
                real_value = balance
            sushi.swap_token_for_eth(token, real_value, self.account)
        return buff()

    @handle_error(account=account)
    def get_owlto_data(self, net_name):
        @handle_error(account=self.account)
        def buff():
            chain_ids = {
                "ethereum": 1,
                "arbitrum": 42161
            }
            chain_id = chain_ids[net_name]
            r = req(f"https://owlto.finance/api/lp-info?token=ETH&from_chainid={chain_id}&to_chainid=534352&user={self.account.get_address()}")
            min_val = int(r["msg"]["min"])/1e18
            max_val = int(r["msg"]["max"])/1e18
            fee = int(r["msg"]["dtc"])/1e18
            maker = r["msg"]["maker_address"]
            return min_val, max_val, fee, maker
        return buff()
        

    
    def owlto_bridge(self, net_name, amount):
        @handle_error(account=self.account)
        def buff():
            txn_data_handler = EVMTransactionDataHandler(self.account, net_name)
            min_amount, max_amount, fee, maker = self.get_owlto_data(net_name)

            if amount < min_amount+fee or amount > max_amount+fee:
                logger.error(f"[{self.account.get_address()}] amount to bridge ({amount}) not in owlto limits (min: {min_amount+fee}, max: {max_amount+fee})")
                return -1

            str_amount = str(int(amount*1e18))

            str_amount = str_amount[:-4] + "0006"        

            value = int(str_amount)

            txn = txn_data_handler.get_txn_data(value)
            txn["to"] = maker

            self.account.send_txn([txn], net_name)
        buff()
    
    def check_eth_balances(self, chain = None):
        token: EVMToken = None
        value: float = 0.0
        if chain:
            native_chains = [chain]
        else:
            native_chains = self.native_chains.copy()
        for chain in native_chains:
            ether = chain_natives[chain]
            balance = self.account.get_balance(ether)[1]
            logger.info(f"[{self.account.get_address()}] ({chain}) {ether.symbol} balance: {balance}")
            if balance < SETTINGS["MinEthValue"]:
                continue
            if balance > value:
                value = balance
                token = ether
        
        return token, value

    def orbiter_bridge(self, net_name, amount):
        @handle_error(account=self.account)
        def buff():
            txn_data_handler = EVMTransactionDataHandler(self.account, net_name)
            min_amount, max_amount, fee = 0.005, self.account.get_balance(chain_natives[net_name])[1], 0.0015
            maker = "0xE4eDb277e41dc89aB076a1F049f4a3EfA700bCE8"
            if amount < min_amount+fee or amount > max_amount+fee:
                logger.error(f"[{self.account.get_address()}] amount to bridge ({amount}) not in orbiter limits (min: {min_amount+fee}, max: {max_amount+fee})")
                return -1

            str_amount = str(int(amount*1e18))

            str_amount = str_amount[:-4] + str(self.ORBITER_CHAIN_CODES["scroll"])     

            value = int(str_amount)

            txn = txn_data_handler.get_txn_data(value)
            txn["to"] = maker

            self.account.send_txn([txn], net_name)
        return buff()


    def simple_bridge(self, chain = None):            
        bridge_type = random.choice(SETTINGS["bridge_type"])
        while True:
            token, value = self.check_eth_balances(chain=chain)
            if token:
                break
            logger.info(f"[{self.account.get_address()}] all balances below min({SETTINGS['MinEthValue']}). keep looking")
            rand_time = SETTINGS["ParsingSleep"]
            logger.info(f'[{self.account.get_address()}] sleeping {rand_time} s')
            time.sleep(rand_time)
        value -= get_random_value(SETTINGS["SaveOnWallet"])
        net = token.net_name

        real_value = get_random_value(SETTINGS["USDAmountToBridge"])
        usd_val = token.get_usd_value(value)
        if real_value > usd_val:
            real_value = usd_val

        token_value = real_value/token.get_price()

        logger.info(f"[{self.account.get_address()}] going to bridge {token_value} ETH")
        if bridge_type == "owlto":
            self.owlto_bridge(net, token_value)
        elif bridge_type == "orbiter":
            self.orbiter_bridge(net, token_value)
        else:
            logger.error(f"[{self.account.get_address()}] selected unsupported bridge({bridge_type})")

        


    def collector(self):
        dist_chain = random.choice(SETTINGS["nets_for_deposit"])
        dist_chain = "ethereum"
        token1 = chains_tokens[dist_chain][0]
        token2 = chains_tokens[dist_chain][1]
        
        st_bal1 = self.account.get_balance(token1)[1]
        st_bal2 = self.account.get_balance(token2)[1]
        res = self.bridge_stables(dist_chain)
        if res[0] in SETTINGS["nets_for_deposit"]:
            start = False
            dist_chain = res[0]
            token = res[1]
            token1 = chains_tokens[dist_chain][0]
            token2 = chains_tokens[dist_chain][1]
        elif res == 1:
            start = True
        else:
            return
        while start:
            bal1 = self.account.get_balance(token1)[1]
            logger.info(f"[{self.account.get_address()}] {token1.symbol} balance: {bal1}")
            bal2 = self.account.get_balance(token2)[1]
            logger.info(f"[{self.account.get_address()}] {token2.symbol} balance: {bal2}")
            if st_bal1 != bal1 or st_bal2 != bal2:
                if st_bal1 != bal1:
                    token = token1
                else:
                    token = token2
                break
            logger.info(f"[{self.account.get_address()}] balances still same. Waiting...")
            sleeping_sync(self.account.get_address())
        
        logger.success(f"[{self.account.get_address()}] found stables. going to swap for eth")

        if self.swap_stables_to_eth(token) == 5555:
            return

        logger.success(f"[{self.account.get_address()}] swapped successfully. going to bridge")

        self.simple_bridge(chain = token.net_name)

    def get_owlto_data_withdraw(self, net_name):
        @handle_error(account=self.account)
        def buff():
            chain_ids = {
                "ethereum": 1,
                "arbitrum": 42161
            }
            chain_id = chain_ids[net_name]
            r = req(f"https://owlto.finance/api/lp-info?token=ETH&from_chainid=534352&to_chainid={chain_id}&user={self.account.get_address()}")
            min_val = int(r["msg"]["min"])/1e18
            max_val = int(r["msg"]["max"])/1e18
            fee = int(r["msg"]["dtc"])/1e18
            maker = r["msg"]["maker_address"]

            return min_val, max_val, fee, maker
        return buff()
                


    def owlto_withdraw(self, net_name, amount):
        @handle_error(account=self.account)
        def buff():
            min_amount, max_amount, fee, maker = self.get_owlto_data_withdraw(net_name)
            owlto_ids = {
                "ethereum": "0001",
                "arbitrum": "0004"
            }

            txn_data_handler = EVMTransactionDataHandler(self.account, "scroll")

            if amount < min_amount+fee or amount > max_amount+fee:
                logger.error(f"[{self.account.get_address()}] amount to bridge ({amount}) not in owlto limits (min: {min_amount+fee}, max: {max_amount+fee})")
                return -1

            str_amount = str(int(amount*1e18))
            code = owlto_ids[net_name]
            str_amount = str_amount[:-4] + code       

            value = int(str_amount)

            txn = txn_data_handler.get_txn_data(value)
            txn["to"] = maker

            self.account.send_txn([txn], "scroll")
        buff()

    def orbiter_withdraw(self, net_name, amount):
        @handle_error(account=self.account)
        def buff():
            min_amount, max_amount, fee = 0.005, self.account.get_balance(chain_natives["scroll"])[1], self.ORBITER_WITHDRAW_FEE[net_name]
            maker = "0xE4eDb277e41dc89aB076a1F049f4a3EfA700bCE8"
           

            txn_data_handler = EVMTransactionDataHandler(self.account, "scroll")

            if amount < min_amount+fee or amount > max_amount+fee:
                logger.error(f"[{self.account.get_address()}] amount to bridge ({amount}) not in owlto limits (min: {min_amount+fee}, max: {max_amount+fee})")
                return -1

            str_amount = str(int(amount*1e18))
            code = str(self.ORBITER_CHAIN_CODES[net_name])
            str_amount = str_amount[:-4] + code       

            value = int(str_amount)

            txn = txn_data_handler.get_txn_data(value)
            txn["to"] = maker

            self.account.send_txn([txn], "scroll")
        buff()


    def withdraw(self):
        net_name = SETTINGS["DistNet"]
        bridge_type = random.choice(SETTINGS["bridge_type"])

        token = eth
        value = self.account.get_balance(eth)[1]
        value -= get_random_value(SETTINGS["WithdrawSaving"])
        net = token.net_name
        real_value = get_random_value(SETTINGS["EtherToWithdraw"])
        if real_value > value:
            real_value = value
        token_value = real_value

        logger.info(f"[{self.account.get_address()}] going to bridge {token_value} ETH to {net_name}")

        if bridge_type == "owlto":
            self.owlto_withdraw(net_name, token_value)
        elif bridge_type == "orbiter":
            self.orbiter_withdraw(net_name, token_value)
        else:
            logger.error(f"[{self.account.get_address()}] selected unsupported bridge({bridge_type})")

        


    def main_handler(self, way: str):
        """possible ways:
            simple -- check max valued eth in chains and bridge
            stargate -- check all stables, bridge to one of chains, swap on sushi bridge to scroll
            withdraw -- withdraw from scroll
            """
        if way == "simple":
            self.simple_bridge()
        elif way == "stargate":
            self.collector()
        elif way == "withdraw":
            self.withdraw()

        



