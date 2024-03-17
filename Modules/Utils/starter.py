import json
import traceback
from threading import Thread
from multiprocessing import Event
import multiprocessing
import multiprocessing.popen_spawn_win32 as forking
import os
import sys

from modules.config import accounts, get_general_settings, SETTINGS_PATH
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
        "ZkStars mint": 27
    }

    running_threads: Process = None

    def run_tasks(self, own_tasks, mode, selected_accounts):
        gas_lock = Event()
        settings = get_general_settings()
        thread_runner_sleep = [int(settings["TimeSleeps"]["threads-runner-sleep-min"]), int(settings["TimeSleeps"]["threads-runner-sleep-max"])]
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
        

    def start(self, json_data, gas_lock):

        

        is_own_tasks = json_data["Other"]["module"]["Own Tasks"]
        if is_own_tasks:
            try:
                own_tasks = json.loads(json_data["Other"]["own-tasks"])
            except:
                return "Json error, check own-tasks"
            mode = "standart" if json_data["Other"]["own-tasks-mode"]["standart"] else "invert"
            self.run_own_tasks(own_tasks, mode, gas_lock)
        else:
            tasks = self.get_task_numbers(json_data) 
            self.run_own_tasks(tasks, "standart", gas_lock)
        return None

    def get_task_numbers(self, json_data):
        res = []
        for page in json_data:
            for module in json_data[page]['module']:
                if json_data[page]['module'][module]:
                    res.append(self.task_numbers[module])
        return res
    
    def get_selected_acounts(self):
        res = []
        for address in accounts:
            account: Account = accounts[address]
            if account.is_active():
                res.append(account)
        return res
    
    def run_own_tasks(self, own_tasks, mode, gas_lock):
        selected_accounts = self.get_selected_acounts()
        with open(f"{SETTINGS_PATH}logs.json") as f:
            init_log = json.load(f)
        init_log["amount"] = len(selected_accounts)
        with open(f"{SETTINGS_PATH}logs.json", "w") as f:
            json.dump(init_log, f, indent=1)

            
        p = Process(target=self.run_tasks, args=(own_tasks, mode, selected_accounts))
        p.start()
        self.running_threads = p






        