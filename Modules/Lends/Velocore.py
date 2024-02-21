from Modules.BaseClasses.BaseDeFi import BaseLend
from Modules.BaseClasses.BaseAccount import BaseAccount
from Modules.Utils.Token import Token
from Modules.Utils.token_stor import eth
from Modules.Utils.TxnDataHandler import TxnDataHandler
from Modules.Utils.utils import sleeping_sync
from Modules.Utils.Logger import logger
from Modules.config import get_slippage


class Velocore(BaseLend):
    supported_tokens = ["ETH"]
    supported_tokens_for_borrow = []
    contract_address = "0x1d0188c4B276A09366D05d6Be06aF61a73bC7535"
    read_contract_address = "0xaA18cDb16a4DD88a59f4c2f45b5c91d009549e06"
    name = "Velocore"
    lend_tokens = [
        Token('VUSD+', "0xcc22F6AA610D1b2a0e89EF228079cB3e1831b1D1", 6, "linea")
    ]
    abi = [{"inputs":[{"internalType":"contract IVC","name":"vc_","type":"address"},{"internalType":"Token","name":"ballot_","type":"bytes32"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"contract IGauge","name":"gauge","type":"address"},{"indexed":True,"internalType":"contract IBribe","name":"bribe","type":"address"}],"name":"BribeAttached","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"contract IGauge","name":"gauge","type":"address"},{"indexed":True,"internalType":"contract IBribe","name":"bribe","type":"address"}],"name":"BribeKilled","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"contract IConverter","name":"pool","type":"address"},{"indexed":True,"internalType":"address","name":"user","type":"address"},{"indexed":False,"internalType":"Token[]","name":"tokenRef","type":"bytes32[]"},{"indexed":False,"internalType":"int128[]","name":"delta","type":"int128[]"}],"name":"Convert","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"bytes4","name":"sig","type":"bytes4"},{"indexed":True,"internalType":"address","name":"implementaion","type":"address"},{"indexed":False,"internalType":"bool","name":"viewer","type":"bool"}],"name":"FunctionChanged","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"contract IGauge","name":"pool","type":"address"},{"indexed":True,"internalType":"address","name":"user","type":"address"},{"indexed":False,"internalType":"Token[]","name":"tokenRef","type":"bytes32[]"},{"indexed":False,"internalType":"int128[]","name":"delta","type":"int128[]"}],"name":"Gauge","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"contract IGauge","name":"gauge","type":"address"},{"indexed":False,"internalType":"bool","name":"killed","type":"bool"}],"name":"GaugeKilled","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"contract ISwap","name":"pool","type":"address"},{"indexed":True,"internalType":"address","name":"user","type":"address"},{"indexed":False,"internalType":"Token[]","name":"tokenRef","type":"bytes32[]"},{"indexed":False,"internalType":"int128[]","name":"delta","type":"int128[]"}],"name":"Swap","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"to","type":"address"},{"indexed":True,"internalType":"address","name":"from","type":"address"},{"indexed":False,"internalType":"Token[]","name":"tokenRef","type":"bytes32[]"},{"indexed":False,"internalType":"int128[]","name":"delta","type":"int128[]"}],"name":"UserBalance","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"contract IGauge","name":"pool","type":"address"},{"indexed":True,"internalType":"address","name":"user","type":"address"},{"indexed":False,"internalType":"int256","name":"voteDelta","type":"int256"}],"name":"Vote","type":"event"},{"inputs":[{"internalType":"contract IGauge","name":"gauge","type":"address"},{"internalType":"contract IBribe","name":"bribe","type":"address"}],"name":"attachBribe","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"emissionToken","outputs":[{"internalType":"Token","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"Token[]","name":"tokenRef","type":"bytes32[]"},{"internalType":"int128[]","name":"deposit","type":"int128[]"},{"components":[{"internalType":"bytes32","name":"poolId","type":"bytes32"},{"internalType":"bytes32[]","name":"tokenInformations","type":"bytes32[]"},{"internalType":"bytes","name":"data","type":"bytes"}],"internalType":"struct VelocoreOperation[]","name":"ops","type":"tuple[]"}],"name":"execute","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"bribeIndex","type":"uint256"},{"internalType":"Token[]","name":"tokenRef","type":"bytes32[]"},{"internalType":"int128[]","name":"cumDelta","type":"int128[]"},{"internalType":"contract IGauge","name":"gauge","type":"address"},{"internalType":"uint256","name":"elapsed","type":"uint256"},{"internalType":"address","name":"user","type":"address"}],"name":"extort","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"initializeFacet","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"contract IGauge","name":"gauge","type":"address"},{"internalType":"contract IBribe","name":"bribe","type":"address"}],"name":"killBribe","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"contract IGauge","name":"gauge","type":"address"},{"internalType":"bool","name":"kill","type":"bool"}],"name":"killGauge","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"Token","name":"tok","type":"bytes32"},{"internalType":"uint128","name":"gaugeAmount","type":"uint128"},{"internalType":"uint128","name":"poolAmount","type":"uint128"}],"name":"notifyInitialSupply","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"user","type":"address"},{"internalType":"Token[]","name":"tokenRef","type":"bytes32[]"},{"internalType":"int128[]","name":"deposit","type":"int128[]"},{"components":[{"internalType":"bytes32","name":"poolId","type":"bytes32"},{"internalType":"bytes32[]","name":"tokenInformations","type":"bytes32[]"},{"internalType":"bytes","name":"data","type":"bytes"}],"internalType":"struct VelocoreOperation[]","name":"ops","type":"tuple[]"}],"name":"query","outputs":[{"internalType":"int128[]","name":"","type":"int128[]"}],"stateMutability":"nonpayable","type":"function"}]
    read_abi = [{"inputs":[{"internalType":"Token","name":"usdc_","type":"bytes32"},{"internalType":"contract VC","name":"vc_","type":"address"},{"internalType":"contract ConstantProductPoolFactory","name":"factory_","type":"address"},{"internalType":"contract WombatRegistry","name":"wombatRegistry_","type":"address"},{"internalType":"contract VelocoreLens","name":"lens_","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"contract IGauge","name":"gauge","type":"address"},{"indexed":True,"internalType":"contract IBribe","name":"bribe","type":"address"}],"name":"BribeAttached","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"contract IGauge","name":"gauge","type":"address"},{"indexed":True,"internalType":"contract IBribe","name":"bribe","type":"address"}],"name":"BribeKilled","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"contract IConverter","name":"pool","type":"address"},{"indexed":True,"internalType":"address","name":"user","type":"address"},{"indexed":False,"internalType":"Token[]","name":"tokenRef","type":"bytes32[]"},{"indexed":False,"internalType":"int128[]","name":"delta","type":"int128[]"}],"name":"Convert","type":"event"},{"anonymous":False,"inputs":[{"components":[{"internalType":"address","name":"facetAddress","type":"address"},{"internalType":"enum VaultStorage.FacetCutAction","name":"action","type":"uint8"},{"internalType":"bytes4[]","name":"functionSelectors","type":"bytes4[]"}],"indexed":False,"internalType":"struct VaultStorage.FacetCut[]","name":"_diamondCut","type":"tuple[]"},{"indexed":False,"internalType":"address","name":"_init","type":"address"},{"indexed":False,"internalType":"bytes","name":"_calldata","type":"bytes"}],"name":"DiamondCut","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"contract IGauge","name":"pool","type":"address"},{"indexed":True,"internalType":"address","name":"user","type":"address"},{"indexed":False,"internalType":"Token[]","name":"tokenRef","type":"bytes32[]"},{"indexed":False,"internalType":"int128[]","name":"delta","type":"int128[]"}],"name":"Gauge","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"contract IGauge","name":"gauge","type":"address"},{"indexed":False,"internalType":"bool","name":"killed","type":"bool"}],"name":"GaugeKilled","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"contract ISwap","name":"pool","type":"address"},{"indexed":True,"internalType":"address","name":"user","type":"address"},{"indexed":False,"internalType":"Token[]","name":"tokenRef","type":"bytes32[]"},{"indexed":False,"internalType":"int128[]","name":"delta","type":"int128[]"}],"name":"Swap","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"to","type":"address"},{"indexed":True,"internalType":"address","name":"from","type":"address"},{"indexed":False,"internalType":"Token[]","name":"tokenRef","type":"bytes32[]"},{"indexed":False,"internalType":"int128[]","name":"delta","type":"int128[]"}],"name":"UserBalance","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"contract IGauge","name":"pool","type":"address"},{"indexed":True,"internalType":"address","name":"user","type":"address"},{"indexed":False,"internalType":"int256","name":"voteDelta","type":"int256"}],"name":"Vote","type":"event"},{"inputs":[],"name":"canonicalPoolLength","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"user","type":"address"},{"internalType":"uint256","name":"begin","type":"uint256"},{"internalType":"uint256","name":"maxLength","type":"uint256"}],"name":"canonicalPools","outputs":[{"components":[{"internalType":"address","name":"gauge","type":"address"},{"components":[{"internalType":"address","name":"pool","type":"address"},{"internalType":"string","name":"poolType","type":"string"},{"internalType":"Token[]","name":"lpTokens","type":"bytes32[]"},{"internalType":"uint256[]","name":"mintedLPTokens","type":"uint256[]"},{"internalType":"Token[]","name":"listedTokens","type":"bytes32[]"},{"internalType":"uint256[]","name":"reserves","type":"uint256[]"},{"internalType":"bytes","name":"poolParams","type":"bytes"}],"internalType":"struct PoolData","name":"poolData","type":"tuple"},{"internalType":"bool","name":"killed","type":"bool"},{"internalType":"uint256","name":"totalVotes","type":"uint256"},{"internalType":"uint256","name":"userVotes","type":"uint256"},{"internalType":"uint256","name":"userClaimable","type":"uint256"},{"internalType":"uint256","name":"emissionRate","type":"uint256"},{"internalType":"uint256","name":"userEmissionRate","type":"uint256"},{"internalType":"uint256","name":"stakedValueInHubToken","type":"uint256"},{"internalType":"uint256","name":"userStakedValueInHubToken","type":"uint256"},{"internalType":"uint256","name":"averageInterestRatePerSecond","type":"uint256"},{"internalType":"uint256","name":"userInterestRatePerSecond","type":"uint256"},{"internalType":"Token[]","name":"stakeableTokens","type":"bytes32[]"},{"internalType":"uint256[]","name":"stakedAmounts","type":"uint256[]"},{"internalType":"uint256[]","name":"userStakedAmounts","type":"uint256[]"},{"internalType":"Token[]","name":"underlyingTokens","type":"bytes32[]"},{"internalType":"uint256[]","name":"stakedUnderlying","type":"uint256[]"},{"internalType":"uint256[]","name":"userUnderlying","type":"uint256[]"},{"components":[{"internalType":"Token[]","name":"tokens","type":"bytes32[]"},{"internalType":"uint256[]","name":"rates","type":"uint256[]"},{"internalType":"uint256[]","name":"userClaimable","type":"uint256[]"},{"internalType":"uint256[]","name":"userRates","type":"uint256[]"}],"internalType":"struct BribeData[]","name":"bribes","type":"tuple[]"}],"internalType":"struct GaugeData[]","name":"gaugeDataArray","type":"tuple[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"contract IPool","name":"poolAddr","type":"address"},{"internalType":"Token","name":"token","type":"bytes32"}],"name":"getPoolBalance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"gauge","type":"address"},{"internalType":"address","name":"user","type":"address"}],"name":"queryGauge","outputs":[{"components":[{"internalType":"address","name":"gauge","type":"address"},{"components":[{"internalType":"address","name":"pool","type":"address"},{"internalType":"string","name":"poolType","type":"string"},{"internalType":"Token[]","name":"lpTokens","type":"bytes32[]"},{"internalType":"uint256[]","name":"mintedLPTokens","type":"uint256[]"},{"internalType":"Token[]","name":"listedTokens","type":"bytes32[]"},{"internalType":"uint256[]","name":"reserves","type":"uint256[]"},{"internalType":"bytes","name":"poolParams","type":"bytes"}],"internalType":"struct PoolData","name":"poolData","type":"tuple"},{"internalType":"bool","name":"killed","type":"bool"},{"internalType":"uint256","name":"totalVotes","type":"uint256"},{"internalType":"uint256","name":"userVotes","type":"uint256"},{"internalType":"uint256","name":"userClaimable","type":"uint256"},{"internalType":"uint256","name":"emissionRate","type":"uint256"},{"internalType":"uint256","name":"userEmissionRate","type":"uint256"},{"internalType":"uint256","name":"stakedValueInHubToken","type":"uint256"},{"internalType":"uint256","name":"userStakedValueInHubToken","type":"uint256"},{"internalType":"uint256","name":"averageInterestRatePerSecond","type":"uint256"},{"internalType":"uint256","name":"userInterestRatePerSecond","type":"uint256"},{"internalType":"Token[]","name":"stakeableTokens","type":"bytes32[]"},{"internalType":"uint256[]","name":"stakedAmounts","type":"uint256[]"},{"internalType":"uint256[]","name":"userStakedAmounts","type":"uint256[]"},{"internalType":"Token[]","name":"underlyingTokens","type":"bytes32[]"},{"internalType":"uint256[]","name":"stakedUnderlying","type":"uint256[]"},{"internalType":"uint256[]","name":"userUnderlying","type":"uint256[]"},{"components":[{"internalType":"Token[]","name":"tokens","type":"bytes32[]"},{"internalType":"uint256[]","name":"rates","type":"uint256[]"},{"internalType":"uint256[]","name":"userClaimable","type":"uint256[]"},{"internalType":"uint256[]","name":"userRates","type":"uint256[]"}],"internalType":"struct BribeData[]","name":"bribes","type":"tuple[]"}],"internalType":"struct GaugeData","name":"poolData","type":"tuple"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"pool","type":"address"}],"name":"queryPool","outputs":[{"components":[{"internalType":"address","name":"pool","type":"address"},{"internalType":"string","name":"poolType","type":"string"},{"internalType":"Token[]","name":"lpTokens","type":"bytes32[]"},{"internalType":"uint256[]","name":"mintedLPTokens","type":"uint256[]"},{"internalType":"Token[]","name":"listedTokens","type":"bytes32[]"},{"internalType":"uint256[]","name":"reserves","type":"uint256[]"},{"internalType":"bytes","name":"poolParams","type":"bytes"}],"internalType":"struct PoolData","name":"ret","type":"tuple"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"contract ISwap","name":"swap","type":"address"},{"internalType":"Token","name":"base","type":"bytes32"},{"internalType":"Token","name":"quote","type":"bytes32"},{"internalType":"uint256","name":"baseAmount","type":"uint256"}],"name":"spotPrice","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"Token","name":"quote","type":"bytes32"},{"internalType":"Token[]","name":"tok","type":"bytes32[]"},{"internalType":"uint256[]","name":"amount","type":"uint256[]"}],"name":"spotPrice","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"Token","name":"base","type":"bytes32"},{"internalType":"Token","name":"quote","type":"bytes32"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"spotPrice","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"user","type":"address"},{"internalType":"Token[]","name":"ts","type":"bytes32[]"}],"name":"userBalances","outputs":[{"internalType":"uint256[]","name":"balances","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"user","type":"address"}],"name":"wombatGauges","outputs":[{"components":[{"internalType":"address","name":"gauge","type":"address"},{"components":[{"internalType":"address","name":"pool","type":"address"},{"internalType":"string","name":"poolType","type":"string"},{"internalType":"Token[]","name":"lpTokens","type":"bytes32[]"},{"internalType":"uint256[]","name":"mintedLPTokens","type":"uint256[]"},{"internalType":"Token[]","name":"listedTokens","type":"bytes32[]"},{"internalType":"uint256[]","name":"reserves","type":"uint256[]"},{"internalType":"bytes","name":"poolParams","type":"bytes"}],"internalType":"struct PoolData","name":"poolData","type":"tuple"},{"internalType":"bool","name":"killed","type":"bool"},{"internalType":"uint256","name":"totalVotes","type":"uint256"},{"internalType":"uint256","name":"userVotes","type":"uint256"},{"internalType":"uint256","name":"userClaimable","type":"uint256"},{"internalType":"uint256","name":"emissionRate","type":"uint256"},{"internalType":"uint256","name":"userEmissionRate","type":"uint256"},{"internalType":"uint256","name":"stakedValueInHubToken","type":"uint256"},{"internalType":"uint256","name":"userStakedValueInHubToken","type":"uint256"},{"internalType":"uint256","name":"averageInterestRatePerSecond","type":"uint256"},{"internalType":"uint256","name":"userInterestRatePerSecond","type":"uint256"},{"internalType":"Token[]","name":"stakeableTokens","type":"bytes32[]"},{"internalType":"uint256[]","name":"stakedAmounts","type":"uint256[]"},{"internalType":"uint256[]","name":"userStakedAmounts","type":"uint256[]"},{"internalType":"Token[]","name":"underlyingTokens","type":"bytes32[]"},{"internalType":"uint256[]","name":"stakedUnderlying","type":"uint256[]"},{"internalType":"uint256[]","name":"userUnderlying","type":"uint256[]"},{"components":[{"internalType":"Token[]","name":"tokens","type":"bytes32[]"},{"internalType":"uint256[]","name":"rates","type":"uint256[]"},{"internalType":"uint256[]","name":"userClaimable","type":"uint256[]"},{"internalType":"uint256[]","name":"userRates","type":"uint256[]"}],"internalType":"struct BribeData[]","name":"bribes","type":"tuple[]"}],"internalType":"struct GaugeData[]","name":"gaugeDataArray","type":"tuple[]"}],"stateMutability":"nonpayable","type":"function"}]


    def get_pool_balance(self, sender: BaseAccount):
        while True:
            try:
                w3 = sender.get_w3("linea")
                contract  = w3.eth.contract(address=self.read_contract_address, abi=self.read_abi)

                res = contract.functions.wombatGauges(w3.to_checksum_address(sender.address)).call()

                for gauge in res:
                    pool_data = gauge[1]
                    address = pool_data[0]
                    if address == "0x1D312eedd57E8d43bcb6369E4b8f02d3C18AAf13":
                        if gauge[0] == "0x9582B6Ad01b308eDAc14CB9BDF21e7Da698b5EDD":
                            return gauge[17][0]
            except Exception as e:
                logger.error(f"[{sender.address}] can't get pool data: {e}")


    def create_txn_for_adding_token(self, token: Token, amount: float, sender: BaseAccount):
        w3 = sender.get_w3("linea")
        contract = w3.eth.contract(self.contract_address, abi=self.abi)
        txn_data_handler = TxnDataHandler(sender, "linea", w3=w3)
        if token.symbol == "ETH":
            value =  int(amount*10**token.decimals)
        else:
            value = 0

        token.get_approve_txn(sender, self.contract_address, int(amount*10**token.decimals), w3=w3)
        hex_to_send = hex(int(amount*10**token.decimals))[2::]
        hex_to_send = "03" + (62-len(hex_to_send))*"0" + hex_to_send

        max_ = 340282366920938463463374607431768211455
        hex_to_send_reverce = hex(max_ - int(amount*10**token.decimals) + 1)[2::]
        hex_to_send_reverce = "03" + (62-len(hex_to_send_reverce))*"0" + hex_to_send_reverce
        eth_price = token.get_price()
        min_received = eth_price*amount*get_slippage()
        min_received = int(min_received*1e6)
        min_received = hex(max_ - min_received)[2::]
        min_received = "0201" + (60-len(min_received))*"0" + min_received

        token_ref = [
            bytes.fromhex("0000000000000000000000003f006b0493ff32b33be2809367f5f6722cb84a7b"),
            bytes.fromhex("000000000000000000000000cc22f6aa610d1b2a0e89ef228079cb3e1831b1d1"),
            bytes.fromhex("0200000000000000000000011d312eedd57e8d43bcb6369e4b8f02d3c18aaf13"),
            bytes.fromhex("eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
        ]
        ops = [
            [
                bytes.fromhex("040000000000000000000000" + sender.address[2::]),
                [bytes.fromhex(hex_to_send)],
                bytes.fromhex("00")
            ],
            [
                bytes.fromhex("040000000000000000000000" + sender.address[2::]),
                [bytes.fromhex(hex_to_send_reverce)],
                bytes.fromhex("00")
            ],
            [
                bytes.fromhex('0000000000000000000000007573f3284c91858450eb57c1f46c7354d901228d'),
                [
                    bytes.fromhex("000100000000000000000000000000007fffffffffffffffffffffffffffffff"),
                    bytes.fromhex("030200000000000000000000000000007fffffffffffffffffffffffffffffff")
                ],
                bytes.fromhex("00")
            ],
            [
                bytes.fromhex('0000000000000000000000001d312eedd57e8d43bcb6369e4b8f02d3c18aaf13'),
                [
                    bytes.fromhex("000200000000000000000000000000007fffffffffffffffffffffffffffffff"),
                    bytes.fromhex("020100000000000000000000000000007fffffffffffffffffffffffffffffff")
                ],
                bytes.fromhex("00")
            ],
            [
                bytes.fromhex('0500000000000000000000000000000000000000000000000000000000000000'),
                [bytes.fromhex(min_received)],
                bytes.fromhex("00")
            ],
            [
                bytes.fromhex('0100000000000000000000009582b6ad01b308edac14cb9bdf21e7da698b5edd'),
                [
                    bytes.fromhex('0101000000000000000000000000000000000000000000000000000000000000'),
                    bytes.fromhex('020200000000000000000000000000007fffffffffffffffffffffffffffffff')
                ],
                bytes.fromhex("00")
            ]

        ]
        txn = contract.functions.execute(
            token_ref,
            [0, 0, 0, 0],
            ops
        ).build_transaction(txn_data_handler.get_txn_data(value))

        return txn
    
    def create_txn_for_removing_token(self, token: Token, sender: BaseAccount):
        w3 = sender.get_w3("linea")
        contract = w3.eth.contract(self.contract_address, abi=self.abi)
        txn_data_handler = TxnDataHandler(sender, "linea", w3=w3)

        amount = self.get_pool_balance(sender)
        if amount == 0:
            logger.info(f"[{sender.address}] USD+ value is 0. Skip")
            return -1
        eth_price = eth.get_price()
        eth_min = int(((amount/1e6)/eth_price)*get_slippage()*1e18)
        max_ = 340282366920938463463374607431768211455
        token_ref = [
            bytes.fromhex("0000000000000000000000003f006b0493ff32b33be2809367f5f6722cb84a7b"),
            bytes.fromhex("000000000000000000000000cc22f6aa610d1b2a0e89ef228079cb3e1831b1d1"),
            bytes.fromhex("0200000000000000000000011d312eedd57e8d43bcb6369e4b8f02d3c18aaf13"),
            bytes.fromhex("eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
        ]
        ops = [
            [
                bytes.fromhex('0100000000000000000000009582b6ad01b308edac14cb9bdf21e7da698b5edd'),
                [
                    bytes.fromhex('0101000000000000000000000000000000000000000000000000000000000000'),
                    bytes.fromhex('02000000000000000000000000000000' + hex(max_ - amount + 1)[2::])
                ],
                bytes.fromhex("00")
            ],
            [
                bytes.fromhex('0000000000000000000000001d312eedd57e8d43bcb6369e4b8f02d3c18aaf13'),
                [
                    bytes.fromhex("000100000000000000000000000000007fffffffffffffffffffffffffffffff"),
                    bytes.fromhex("020200000000000000000000000000007fffffffffffffffffffffffffffffff")
                    
                ],
                bytes.fromhex("00")
            ],
            [
                bytes.fromhex('0000000000000000000000007573f3284c91858450eb57c1f46c7354d901228d'),
                [
                    bytes.fromhex("000200000000000000000000000000007fffffffffffffffffffffffffffffff"),
                    bytes.fromhex("030100000000000000000000000000007fffffffffffffffffffffffffffffff")
                    
                ],
                bytes.fromhex("00")
            ],
            [
                bytes.fromhex('0500000000000000000000000000000000000000000000000000000000000000'),
                [
                    bytes.fromhex('03010000000000000000000000000000' + hex(int((max_ - eth_min + 1)))[2::])
                ],
                bytes.fromhex("00")
            ]
        ]


        txn = contract.functions.execute(
            token_ref,
            [0, 0, 0, 0],
            ops
        ).build_transaction(txn_data_handler.get_txn_data())

        return txn
    
    