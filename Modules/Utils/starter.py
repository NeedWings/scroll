import json
import traceback
from threading import Thread
from multiprocessing import Process, Event

from Modules.config import accounts, get_general_settings, SETTINGS_PATH
from Modules.Utils.Account import Account
from Modules.Utils.utils import get_random_value_int
from Modules.TasksHandlers.MainRouter import MainRouter
from Modules.TasksHandlers.OwnTasksRouter import OwnTasks



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






        