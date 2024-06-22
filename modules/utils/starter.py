import json
import traceback
from threading import Thread
from multiprocessing import Event
import multiprocessing
import multiprocessing.popen_spawn_win32 as forking
import os
import sys

from modules.config import SETTINGS_PATH, SETTINGS
from modules.utils.account import Account
from modules.utils.utils import get_random_value_int
from modules.tasks_handlers.main_router import MainRouter
from modules.tasks_handlers.own_tasks_router import OwnTasks


class _Popen(forking.Popen):
    def __init__(self, *args, **kw):
        if hasattr(sys, 'frozen'):
            # We have to set original _MEIPASS2 value from sys._MEIPASS
            # to get --onefile mode working.
            os.putenv('_MEIPASS2', sys._MEIPASS)
        try:
            super(_Popen, self).__init__(*args, **kw)
        finally:
            if hasattr(sys, 'frozen'):
                # On some platforms (e.g. AIX) 'os.unsetenv()' is not
                # available. In those cases we cannot delete the variable
                # but only set it to the empty string. The bootloader
                # can handle this case.
                if hasattr(os, 'unsetenv'):
                    os.unsetenv('_MEIPASS2')
                else:
                    os.putenv('_MEIPASS2', '')

class Process(multiprocessing.Process):
    if sys.platform.startswith('win'):
        _Popen = _Popen




class Starter:
    
    task_numbers = {
        "Bridge": 1,
        "Withdraw": 2, 
        "Add To Lend": 22,
        "Borrow": 25,
        "Remove From Lend": 23,
        "Repay": 26,
        "Add Liquidity": 4,
        "Remove Liquidity": 24,
        "Send To OKX Subs": 202,
        "Withdraw From OKX": 201,
        "Dmail": 12,
        "Random Swaps": 21,
        "Save Assets": 3,
        "ZkStars mint": 27,
        "Check In Owlto": 28,
        "Check In RubyScore": 29,
        "Withdraw from Rhino to Scroll": 5,
        "Bridge from arb/opti to eth": 30,
        "Off Bridge": 31,
        "Check points": 8821
    }

    running_threads: Process = None

    def run_tasks(self, own_tasks, mode, selected_accounts, gas_lock, ender):
        thread_runner_sleep = SETTINGS["Thread Runner Sleep"]
        tasks = []
        delay = 0
        for i in range(len(selected_accounts)):
            main_router = MainRouter(selected_accounts[i], 0)
            own_tasks_router = OwnTasks(selected_accounts[i])
            tasks.append(Thread(target=own_tasks_router.main, args=[main_router, own_tasks.copy(), mode, delay, gas_lock]))
            delay += get_random_value_int(thread_runner_sleep)

        for i in tasks:
            i.start()

        for i in tasks:
            i.join()

        ender.set()
        

    def start(self, module, gas_lock, accounts, ender):
        is_own_tasks = module == "Own Tasks"
        if is_own_tasks:
            own_tasks = SETTINGS["own tasks"]
            mode = SETTINGS["own tasks mode"]
            return self.run_own_tasks(own_tasks, mode, gas_lock, ender, accounts)
        else:
            tasks = [self.task_numbers[module]]
            return self.run_own_tasks(tasks, "standart", gas_lock, ender, accounts)
    
    def run_own_tasks(self, own_tasks, mode, gas_lock, ender, accounts):


            
        p = Process(target=self.run_tasks, args=(own_tasks, mode, accounts, gas_lock, ender))
        p.start()
        self.running_threads = p
        return p






        