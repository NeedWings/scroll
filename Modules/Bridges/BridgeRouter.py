from Modules.Utils.TokenChecker import token_checker
from Modules.Bridges.Orbiter import Orbiter
from Modules.Dexes.OneInch import OneInch
from Modules.Bridges.owlto import Owlto
from Modules.Bridges.rhino import Rhino
from Modules.Bridges.routernitro import RouterNitro
from Modules.BaseClasses.BaseAccount import BaseAccount
from Modules.Utils.Token import Token
from Modules.Utils.token_stor import eth_ethereum, eth, eth_arbitrum, nets_eth
from Modules.config import get_general_settings, get_launch_settings
from Modules.Utils.utils import get_random_value, get_random_value_int, sleeping_sync, get_pair_for_address_from_file, param_to_list_selected
from Modules.Utils.Logger import logger
from Modules.TasksHandlers.SwapsHandler import SwapsHandler
from Modules.Other.OKXHelper import OKXHelper
from random import uniform, choice
from time import sleep

OWLTO_BRIDGE = 1
ORBITER_BRIDGE = 2
OWLTO_WITHDRAW = 3
ORBITER_WITHDRAW = 4
RHINO_BRIDGE = 5
ROUTER_NITRO_BRIDGE = 6

class BridgeRouter:

    bridge_consts = {
        "Rhino": RHINO_BRIDGE,
        "Owlto": OWLTO_BRIDGE,
        "Orbiter": ORBITER_BRIDGE,
        "RouterNitro": ROUTER_NITRO_BRIDGE
    }

    withdraw_consts = {
        "Owlto": OWLTO_WITHDRAW,
        "Orbiter": ORBITER_WITHDRAW
    }

    def __init__(self, account: BaseAccount) -> None:
        self.LAUNCH_SETTINGS = get_launch_settings()
        self.GENERAL_SETTINGS = get_general_settings()
        self.account = account
        self.owlto_handler = Owlto(account)
        self.orbiter_handler = Orbiter(account)
        self.one_inch_handler = OneInch()
        self.rhino_handler = Rhino(account)
        self.router_nitro = RouterNitro(account)


    def owlto_bridge(self):
        start_balance = self.account.get_balance(eth)[1]
        while True:
            try:
                value, net, token = token_checker.get_max_valued_native(self.account, ["arbitrum", "optimism", "zksync", "ethereum", "base", "linea"])

                human_balance = value/1e18

                if self.LAUNCH_SETTINGS["Bridges"]["bridge-all-balance"]:
                    balance = human_balance - get_random_value([self.LAUNCH_SETTINGS["Bridges"]["save-when-bridge-min"], self.LAUNCH_SETTINGS["Bridges"]["save-when-bridge-max"]])
                else:
                    balance = get_random_value([self.LAUNCH_SETTINGS["Bridges"]["eth-to-bridge-min"], self.LAUNCH_SETTINGS["Bridges"]["eth-to-bridge-max"]]) - get_random_value([self.LAUNCH_SETTINGS["Bridges"]["save-when-bridge-min"], self.LAUNCH_SETTINGS["Bridges"]["save-when-bridge-max"]])

                if balance > 0.002:
                    logger.info(f'[{self.account.address}] Will bridge from: {net}, balance: {human_balance} ETH')
                    
                    txn = self.owlto_handler.get_bridge_txn(net, balance)
                    if txn == -1:
                        return
                    self.account.send_txn(txn, net)
                    break
                else:
                    logger.error(f'[{self.account.address}] Cant find any ETH balances')
                    sleeping_sync(self.account.address, True)
            except Exception as e:
                logger.error(f"[{self.account.address}] got error: {e}")
                sleeping_sync(self.account.address, True)
        new_balance = start_balance
        while new_balance == start_balance:
            sleeping_sync(self.account.address)
            new_balance = self.account.get_balance(eth)[1]

            logger.info(f"[{self.account.address}] waiting for balance. current: {new_balance} ETH")
            

        logger.success(f"[{self.account.address}] found balance! Current: {new_balance} ETH")

    def router_nitro_bridge(self):
        start_balance = self.account.get_balance(eth)[1]
        while True:
            try:
                value, net, token = token_checker.get_max_valued_native(self.account, ["arbitrum", "optimism", "zksync", "ethereum", "linea"])

                human_balance = value/1e18

                if self.LAUNCH_SETTINGS["Bridges"]["bridge-all-balance"]:
                    balance = human_balance - get_random_value([self.LAUNCH_SETTINGS["Bridges"]["save-when-bridge-min"], self.LAUNCH_SETTINGS["Bridges"]["save-when-bridge-max"]])
                else:
                    balance = get_random_value([self.LAUNCH_SETTINGS["Bridges"]["eth-to-bridge-min"], self.LAUNCH_SETTINGS["Bridges"]["eth-to-bridge-max"]]) - get_random_value([self.LAUNCH_SETTINGS["Bridges"]["save-when-bridge-min"], self.LAUNCH_SETTINGS["Bridges"]["save-when-bridge-max"]])

                if balance > 0.002:
                    logger.info(f'[{self.account.address}] Will bridge from: {net}, balance: {human_balance} ETH')
                    
                    txn = self.router_nitro.get_bridge_txn(net, balance)
                    if txn == -1:
                        return
                    self.account.send_txn(txn, net)
                    break
                else:
                    logger.error(f'[{self.account.address}] Cant find any ETH balances')
                    sleeping_sync(self.account.address, True)
            except Exception as e:
                logger.error(f"[{self.account.address}] got error: {e}")
                sleeping_sync(self.account.address, True)
        new_balance = start_balance
        while new_balance == start_balance:
            sleeping_sync(self.account.address)
            new_balance = self.account.get_balance(eth)[1]

            logger.info(f"[{self.account.address}] waiting for balance. current: {new_balance} ETH")
            

        logger.success(f"[{self.account.address}] found balance! Current: {new_balance} ETH")

    def orbiter_bridge(self):
        start_balance = self.account.get_balance(eth)[1]
        while True:
            try:
                value, net, token = token_checker.get_max_valued_native(self.account, ["arbitrum", "optimism", "zksync", "linea", "base"])

                human_balance = value/1e18

                if self.LAUNCH_SETTINGS["Bridges"]["bridge-all-balance"]:
                    balance = human_balance - get_random_value([self.LAUNCH_SETTINGS["Bridges"]["save-when-bridge-min"], self.LAUNCH_SETTINGS["Bridges"]["save-when-bridge-max"]])
                else:
                    balance = get_random_value([self.LAUNCH_SETTINGS["Bridges"]["eth-to-bridge-min"], self.LAUNCH_SETTINGS["Bridges"]["eth-to-bridge-max"]]) - get_random_value([self.LAUNCH_SETTINGS["Bridges"]["save-when-bridge-min"], self.LAUNCH_SETTINGS["Bridges"]["save-when-bridge-max"]])

                if balance > 0.002:
                    logger.info(f'[{self.account.address}] Will bridge from: {net}, balance: {human_balance} ETH')
                    
                    txn = self.orbiter_handler.bridge_native_to_linea(balance, net)
                    if txn == -1:
                        return
                    self.account.send_txn(txn, net)
                    break
                else:
                    logger.info(f'[{self.account.address}] Cant find any ETH balances, will check WETH balances...')

                    value, net, token = token_checker.get_max_valued_wrapped(self.account, ["polygon", "bsc"])
                    
                    human_balance = value/1e18
                    
                    logger.info(f'[{self.account.address}] Top chain with WETH assets: {net}, with balance: {human_balance}')

                    if  human_balance > 0.002:

                        if self.LAUNCH_SETTINGS["Bridges"]["bridge-all-balance"]:
                            balance = human_balance - get_random_value([self.LAUNCH_SETTINGS["Bridges"]["save-when-bridge-min"], self.LAUNCH_SETTINGS["Bridges"]["save-when-bridge-max"]])
                        else:
                            balance = get_random_value([self.LAUNCH_SETTINGS["Bridges"]["eth-to-bridge-min"], self.LAUNCH_SETTINGS["Bridges"]["eth-to-bridge-max"]]) - get_random_value([self.LAUNCH_SETTINGS["Bridges"]["save-when-bridge-min"], self.LAUNCH_SETTINGS["Bridges"]["save-when-bridge-max"]])
                        txn = self.orbiter_handler.bridge_weth_to_linea(balance, net)
                        if txn == -1:
                            return
                        self.account.send_txn(txn, net)
                        break

                    else:
                        logger.info(f'[{self.account.address}] Weth amount is lower than eth to bridge or minimal orbiter limits, will check stable assets')

                        value, net, token = token_checker.get_max_valued_stable(self.account, ["polygon", "bsc", "arbitrum"])

                        if value == 0:
                            logger.info(f'[{self.account.address}] Cant find any stable assets...')
                            return
                        
                        eth_price = eth_ethereum.get_price()

                        to_recv_amount = (value / 10**token.decimals) / eth_price

                        logger.info(f'[{self.account.address}] Can recieve {round(to_recv_amount, 5)} $eth from selling stable assets')
                        if to_recv_amount > 0.002:
                            logger.info(f'[{self.account.address}] Will try to swap token to ETH or WETH')

                            txn = self.one_inch_handler.swap_stable(token, value, self.account)
                            self.account.send_txn(txn, net)
                            sleeping_sync(self.account.address)
                            self.orbiter_bridge()
                        else:
                            logger.info(f'[{self.account.address}] to_recv_amount is lower than settings or minimal orbiter value')
                            return
            except Exception as e:
                logger.error(f"[{self.account.address}] got error: {e}")
                sleeping_sync(self.account.address, True)
        new_balance = start_balance
        while new_balance == start_balance:
            sleeping_sync(self.account.address)
            new_balance = self.account.get_balance(eth)[1]

            logger.info(f"[{self.account.address}] waiting for balance. current: {new_balance} ETH")
            

        logger.success(f"[{self.account.address}] found balance! Current: {new_balance} ETH")

            
    
    def owlto_withdraw(self):
        net = "arbitrum"
        start_balance = self.account.get_balance(nets_eth[net])[1]
        while True:
            try:
                w3 = self.account.get_w3("scroll")
                bridge_amount = get_random_value([self.LAUNCH_SETTINGS["Bridges"]["eth-to-withdraw-min"], self.LAUNCH_SETTINGS["Bridges"]["eth-to-withdraw-max"]])
                balance, human_balance = eth.balance_of(self.account.address, w3=w3)
                if self.LAUNCH_SETTINGS["Bridges"]["withdraw-all-balance"]:
                    swaps_handler = SwapsHandler(self.account)
                    swaps_handler.save_assets("ETH")
                    balance, human_balance = eth.balance_of(self.account.address, w3=w3)
                    if human_balance > 0.0065:
                        bridge_amount = human_balance - uniform(0.00055, 0.0007)
                    else:
                        logger.error(f'[{self.account.address}] Balance is lower than 0.0065')
                        return
                else:
                    if human_balance > bridge_amount:
                        pass    
                    else:
                        swaps_handler = SwapsHandler(self.account)
                        swaps_handler.save_assets("ETH")
                        balance, human_balance = eth.balance_of(self.account.address, w3=w3)
                        if human_balance < bridge_amount:
                            logger.error(f'[{self.account.address}] Eth balance is low')
                            return

                logger.info(f"[{self.account.address}] going to withdraw with Owlto {bridge_amount} ETH")


                txn = self.owlto_handler.get_withdraw_txn(net, bridge_amount)

                self.account.send_txn(txn, "scroll")

                break
               

            except Exception as e:
                logger.error(f"[{self.account.address}] got error: {e}")
                sleeping_sync(self.account.address, True)
                
        
        new_balance = start_balance
        while new_balance == start_balance:
            sleeping_sync(self.account.address)
            new_balance = self.account.get_balance(nets_eth[net])[1]

            logger.info(f"[{self.account.address}] waiting for balance. current: {new_balance} ETH")
            

        logger.success(f"[{self.account.address}] found balance! Current: {new_balance} ETH")

    
    def withdraw_orbiter(self):
        net = "arbitrum"
        start_balance = self.account.get_balance(nets_eth[net])[1]
        while True:
            try:
                w3 = self.account.get_w3("scroll")
                bridge_amount = get_random_value([self.LAUNCH_SETTINGS["Bridges"]["eth-to-withdraw-min"], self.LAUNCH_SETTINGS["Bridges"]["eth-to-withdraw-max"]])
                balance, human_balance = eth.balance_of(self.account.address, w3=w3)
                if self.LAUNCH_SETTINGS["Bridges"]["withdraw-all-balance"]:
                    swaps_handler = SwapsHandler(self.account)
                    swaps_handler.save_assets("ETH")
                    balance, human_balance = eth.balance_of(self.account.address, w3=w3)
                    if human_balance > 0.0065:
                        bridge_amount = human_balance - uniform(0.00055, 0.0007)
                    else:
                        logger.error(f'[{self.account.address}] Balance is lower than 0.0065')
                        return
                else:
                    if human_balance > bridge_amount:
                        pass    
                    else:
                        swaps_handler = SwapsHandler(self.account)
                        swaps_handler.save_assets("ETH")
                        balance, human_balance = eth.balance_of(self.account.address, w3=w3)
                        if human_balance < bridge_amount:
                            logger.error(f'[{self.account.address}] Eth balance is lower than: OrbiterAmountBridge and busd balance is 0')
                            return

                logger.info(f"[{self.account.address}] going to withdraw with Orbiter {bridge_amount} ETH")


                txn = self.orbiter_handler.bridge_from_linea(bridge_amount, net)

                self.account.send_txn(txn, "scroll")

                break
               

            except Exception as e:
                logger.error(f"[{self.account.address}] got error: {e}")
                sleeping_sync(self.account.address, True)
                
        
        new_balance = start_balance
        while new_balance == start_balance:
            sleeping_sync(self.account.address)
            new_balance = self.account.get_balance(nets_eth[net])[1]

            logger.info(f"[{self.account.address}] waiting for balance. current: {new_balance} ETH")
            

        logger.success(f"[{self.account.address}] found balance! Current: {new_balance} ETH")

    def rhino_bridge(self):
        start_balance = self.account.get_balance(eth)[1]
        while True:
            try:
                value, net, token = token_checker.get_max_valued_native(self.account, ["arbitrum", "zksync"])

                human_balance = value/1e18

                if self.LAUNCH_SETTINGS["Bridges"]["bridge-all-balance"]:
                    balance = human_balance - get_random_value([self.LAUNCH_SETTINGS["Bridges"]["save-when-bridge-min"], self.LAUNCH_SETTINGS["Bridges"]["save-when-bridge-max"]])
                else:
                    balance = get_random_value([self.LAUNCH_SETTINGS["Bridges"]["eth-to-bridge-min"], self.LAUNCH_SETTINGS["Bridges"]["eth-to-bridge-max"]]) - get_random_value([self.LAUNCH_SETTINGS["Bridges"]["save-when-bridge-min"], self.LAUNCH_SETTINGS["Bridges"]["save-when-bridge-max"]])

                if balance > 0.005:
                    logger.info(f'[{self.account.address}] Will bridge from: {net}, balance: {human_balance} ETH')
                    
                    self.rhino_handler.bridge_to_scroll(balance, net)
                    break
                else:
                    logger.error(f'[{self.account.address}] Cant find any ETH balances')
                    sleeping_sync(self.account.address, True)
            except Exception as e:
                logger.error(f"[{self.account.address}] got error: {e}")
                sleeping_sync(self.account.address, True)
        new_balance = start_balance
        while new_balance == start_balance:
            sleeping_sync(self.account.address)
            new_balance = self.account.get_balance(eth)[1]

            logger.info(f"[{self.account.address}] waiting for balance. current: {new_balance} ETH")
            

        logger.success(f"[{self.account.address}] found balance! Current: {new_balance} ETH")

    def withdraw_from_rhino(self):
        self.rhino_handler.withdraw_from_rhino()

    def bridge(self, bridge_type):
        if bridge_type == OWLTO_BRIDGE:
            self.owlto_bridge()
        elif bridge_type == ORBITER_BRIDGE:
            self.orbiter_bridge()
        elif bridge_type == OWLTO_BRIDGE:
            self.owlto_withdraw()
        elif bridge_type == ORBITER_WITHDRAW:
            self.withdraw_orbiter()
        elif bridge_type == RHINO_BRIDGE:
            self.rhino_bridge()
        elif bridge_type == ROUTER_NITRO_BRIDGE:
            self.router_nitro_bridge()





