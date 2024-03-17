from Modules.TasksHandlers.LendingHandler import LendingHandler
from Modules.TasksHandlers.LiquidityHandler import LiquidityHandler
from Modules.TasksHandlers.OtherHandler import OtherHandler
from Modules.TasksHandlers.SwapsHandler import SwapsHandler
from Modules.TasksHandlers.OwnTasksRouter import OwnTasks
from Modules.Other.OKXHelper import OKXHelper
from Modules.Bridges.BridgeRouter import BridgeRouter, OWLTO_BRIDGE, OWLTO_WITHDRAW, ORBITER_BRIDGE, ORBITER_WITHDRAW, RHINO_BRIDGE
from Modules.Utils.Account import Account
from Modules.Utils.utils import param_to_list_selected
from Modules.config import get_general_settings, get_launch_settings
from time import sleep
from random import choice
from threading import Event


class MainRouter:
    
    def __init__(self, account: Account, task_number) -> None:
        self.account = account
        self.account.setup_w3(self.account.proxy)
        self.task_number = task_number
        self.LAUNCH_SETTINGS = get_launch_settings()
        self.GENERAL_SETTINGS = get_general_settings()

    def start(self):
        if self.task_number == 1:
            selected =  param_to_list_selected(get_launch_settings()["Bridges"]["BridgeType"])
            bridge_router = BridgeRouter(self.account)
            bridge_router.bridge(bridge_router.bridge_consts[choice(selected)])
        elif self.task_number == 2:
            selected =  param_to_list_selected(get_launch_settings()["Bridges"]["BridgeType"])
            if "Rhino" in selected:
                selected.remove("Rhino")
            bridge_router = BridgeRouter(self.account)
            bridge_router.bridge(bridge_router.withdraw_consts[choice(selected)])
        elif self.task_number == 5 :
            bridge_router = BridgeRouter(self.account)
            bridge_router.withdraw_from_rhino()
        elif self.task_number == 3:
            swap_handler = SwapsHandler(self.account)
            swap_handler.save_assets(choice(param_to_list_selected(self.LAUNCH_SETTINGS["Swaps"]["SaveAssets"])))
        elif self.task_number == 4:
            liquidity_handler = LiquidityHandler(self.account)
            liquidity_handler.add_liquidity()
        elif self.task_number == 6:
            other_handler = OtherHandler(self.account)
            other_handler.horizon_check_in()
        elif self.task_number == 12:
            other_handler = OtherHandler(self.account)
            other_handler.dmail()
        elif self.task_number == 27:
            other_handler = OtherHandler(self.account)
            other_handler.zkstars()
        elif self.task_number == 201:
            api_key = self.GENERAL_SETTINGS["Exchanges"]["OKX"]["key"]
            secret = self.GENERAL_SETTINGS["Exchanges"]["OKX"]["Secret"]
            password = self.GENERAL_SETTINGS["Exchanges"]["OKX"]["Password"]
            okx_helper = OKXHelper(api_key, secret, password, self.account)
            okx_helper.withdraw_handl()
        elif self.task_number == 202:
            api_key = self.GENERAL_SETTINGS["Exchanges"]["OKX"]["key"]
            secret = self.GENERAL_SETTINGS["Exchanges"]["OKX"]["Secret"]
            password = self.GENERAL_SETTINGS["Exchanges"]["OKX"]["Password"]
            okx_helper = OKXHelper(api_key, secret, password, self.account)
            okx_helper.deposit_handl()
        elif self.task_number == 21:
            swap_handler = SwapsHandler(self.account)
            swap_handler.random_swaps()
        elif self.task_number == 22:
            lend_handler = LendingHandler(self.account)
            lend_handler.add_to_lend()
        elif self.task_number == 23:
            lend_handler = LendingHandler(self.account)
            lend_handler.remove_from_lend()
        elif self.task_number == 24:
            liquidity_handler = LiquidityHandler(self.account)
            liquidity_handler.remove_liquidity()
        elif self.task_number == 25:
            lend_handler = LendingHandler(self.account)
            lend_handler.borrow()
        elif self.task_number == 26:
            lend_handler = LendingHandler(self.account)
            lend_handler.repay()
        elif self.task_number == 0:
            own_tasks_router = OwnTasks(self.account)
            own_tasks_router.main(self)