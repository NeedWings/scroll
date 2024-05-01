import decimal
import random

from modules.base_classes.base_account import BaseAccount
from modules.utils.token_stor import nets_stables, nets_eth, nets_weth
from modules.utils.utils import decimal_to_int
from modules.utils.txn_data_handler import TxnDataHandler
from modules.utils.Logger import logger
from modules.config import ABI

class Orbiter:

    supported_nets = ['ethereum', 'optimism', 'arbitrum', 'zksync', 'scroll', 'base']
    chaincodes = {
        'ethereum'      : '9001',
        'optimism'      : '9007',
        'bsc'           : '9015',
        'arbitrum'      : '9002',
        'nova'          : '9016',
        'polygon'       : '9006',
        'polygon_zkevm' : '9017',
        'zksync'        : '9014',
        'starknet'      : '9004',
        "zksync_lite"   : "9003",
        "linea"         : '9023',
        "scroll"        : '9019',
        "base"          : '9021'
    }

    orbiter_chaincodes_eth = {
        'ethereum'      : 0.000000000000009001,
        'optimism'      : 0.000000000000009007,
        'bsc'           : 0.000000000000009015,
        'arbitrum'      : 0.000000000000009002,
        'nova'          : 0.000000000000009016,
        'polygon'       : 0.000000000000009006,
        'polygon_zkevm' : 0.000000000000009017,
        'zksync'        : 0.000000000000009014,
        'starknet'      : 0.000000000000009004,
        "zksync_lite"   : 0.000000000000009003,
        "linea"         : 0.000000000000009023,
        "base"          : 0.000000000000009021,
        "scroll"        : 0.000000000000009019
    }

    contracts = {
        "bsc"      : "0xE4eDb277e41dc89aB076a1F049f4a3EfA700bCE8",
        "arbitrum" : "0xE4eDb277e41dc89aB076a1F049f4a3EfA700bCE8",
        "polygon"  : "0xE4eDb277e41dc89aB076a1F049f4a3EfA700bCE8",
        "zksync"   : "0xE4eDb277e41dc89aB076a1F049f4a3EfA700bCE8",
        "linea"    : "0x80C67432656d59144cEFf962E8fAF8926599bCF8",
        "optimism" : "0xE4eDb277e41dc89aB076a1F049f4a3EfA700bCE8",
        "scroll"   : "0xE4eDb277e41dc89aB076a1F049f4a3EfA700bCE8",
        "base"     : "0x80C67432656d59144cEFf962E8fAF8926599bCF8",
    }

    def __init__(self, account: BaseAccount) -> None:
        self.account = account


    def get_value_with_chaincode(self, value, net):
        base_num_dec = decimal.Decimal(str(value))
        orbiter_amount_dec = decimal.Decimal(str(self.orbiter_chaincodes_eth[net]))
        difference = base_num_dec - orbiter_amount_dec
        random_offset = decimal.Decimal(str(random.uniform(-0.000000000000001, 0.000000000000001)))
        result_dec = difference + random_offset
        orbiter_str = self.chaincodes[net][-4:]
        result_str = '{:.18f}'.format(result_dec.quantize(decimal.Decimal('0.000000000000000001')))
        result_str = result_str[:-4] + orbiter_str
        return decimal.Decimal(result_str)


    def bridge_native_to_linea(self, amount, net_name):
        try:
            w3 = self.account.get_w3(net_name)
            txn_data_handler = TxnDataHandler(self.account, net_name, w3=w3)

            amount = self.get_value_with_chaincode(amount-0.001, "scroll")
            value = decimal_to_int(amount, 18)
            if value <= 0:
                logger.error(f"[{self.account.address}] orbiter value is 0")
                return -1
            txn = txn_data_handler.get_txn_data(value=value)

            txn["to"] = self.contracts[net_name]

            return txn
        except:
            return -1
    
    def bridge_weth_to_linea(self, amount, net_name):
        w3 = self.account.get_w3(net_name)
        txn_data_handler = TxnDataHandler(self.account, net_name, w3=w3)

        amount = self.get_value_with_chaincode(amount, "scroll")
        value = decimal_to_int(amount, 18)
        
        if value <= 0:
            logger.error(f"[{self.account.address}] orbiter value is 0")
            return -1
        weth = nets_weth[net_name]

        contract = w3.eth.contract(weth.contract_address, abi=ABI)
        
        txn = contract.functions.transfer(self.contracts[net_name], value).build_transaction(txn_data_handler.get_txn_data())

        return txn

    def bridge_from_linea(self, amount, net_name):
        w3 = self.account.get_w3("scroll")
        txn_data_handler = TxnDataHandler(self.account, "scroll", w3=w3)

        amount = self.get_value_with_chaincode(amount, net_name)
        value = decimal_to_int(amount, 18)

        if amount <= 0.002:
            logger.error(f"[{self.account.address}] (orbiter bridger) Value is lower than 0.002")
            return
        
        txn = txn_data_handler.get_txn_data(value=value)
        txn["to"] = self.contracts["scroll"]

        return txn
        