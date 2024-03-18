from time import sleep
from random import choice
from threading import Event

from modules.tasks_handlers.lending_handler import LendingHandler
from modules.tasks_handlers.liquiditty_handler import LiquidityHandler
from modules.tasks_handlers.other_handler import OtherHandler
from modules.tasks_handlers.swaps_handler import SwapsHandler
from modules.tasks_handlers.own_tasks_router import OwnTasks
from modules.other.okx_helper import OKXHelper
from modules.bridges.bridge_router import BridgeRouter
from modules.utils.account import Account
from modules.config import SETTINGS


class MainRouter:
    
    def __init__(self, account: Account, task_number) -> None:
        self.account = account
        self.account.setup_w3(self.account.proxy)
        self.task_number = task_number

    def start(self):
        if self.task_number == 1:
            selected = choice(SETTINGS["Bridge Type"])
            bridge_router = BridgeRouter(self.account)
            bridge_router.bridge(bridge_router.bridge_consts[selected])
        elif self.task_number == 2:
            selected = choice(SETTINGS["Bridge Type"])
            if "Rhino" in selected:
                selected.remove("Rhino")
            bridge_router = BridgeRouter(self.account)
            bridge_router.bridge(bridge_router.withdraw_consts[selected])
        elif self.task_number == 5 :
            bridge_router = BridgeRouter(self.account)
            bridge_router.withdraw_from_rhino()
        elif self.task_number == 3:
            swap_handler = SwapsHandler(self.account)
            swap_handler.save_assets(choice(SETTINGS["To Save Funds"]))
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
            api_key = SETTINGS["OKX key"]
            secret = SETTINGS["OKX Secret"]
            password = SETTINGS["OKX Password"]
            okx_helper = OKXHelper(api_key, secret, password, self.account)
            okx_helper.withdraw_handl()
        elif self.task_number == 202:
            api_key = SETTINGS["OKX key"]
            secret = SETTINGS["OKX Secret"]
            password = SETTINGS["OKX Password"]
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