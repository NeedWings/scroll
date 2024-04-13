import json
from time import sleep
from random import shuffle, choice, randint
import multiprocessing
from multiprocessing import Event

from termcolor import colored
import inquirer
from inquirer.themes import load_theme_from_dict as loadth
from web3 import Web3

from modules.utils.starter import Starter
from modules.utils.launch import encode_secrets, decode_secrets, transform_keys
from modules.utils.account import Account, ethAccount
from modules.config import autosoft, subs_text, SETTINGS_PATH, SETTINGS, RPC_LIST


def get_action() -> str:
    theme = {
        "Question": {
            "brackets_color": "bright_yellow"
        },
        "List": {
            "selection_color": "bright_blue"
        }
    }

    question = [
        inquirer.List(
        "action",
        message=colored("Choose soft work task", 'light_yellow'),
        choices=[
            "Bridge",
            "Withdraw", 
            "Withdraw from Rhino to Scroll",
            "",
            "Add To Lend",
            "Borrow",
            "Remove From Lend",
            "Repay",
            "",
            "Add Liquidity",
            "Remove Liquidity",
            "",
            "Send To OKX Subs",
            "Withdraw From OKX",
            "",
            "Random Swaps",
            "Save Assets",
            "",
            "Dmail",
            "ZkStars mint",
            "Check In",
            "",
            "Own Tasks",
            "========================",
            "Encode secrets"
        ],
    )
    ]
    action = inquirer.prompt(question, theme=loadth(theme))['action']
    return action

def gas_locker(gas_lock, ender):
    while True:
        w3 = Web3(Web3.HTTPProvider(choice(RPC_LIST["ethereum"])))
        if ender.is_set():
            return  
        f = open(f"{SETTINGS_PATH}settings.json", "r")
        SETTINGS = json.loads(f.read())
        f.close()
        max_gas = Web3.to_wei(SETTINGS["MaxEthGwei"], 'gwei')
        try:
            gas_price = w3.eth.gas_price
            if gas_price > max_gas:
                h_gas, h_max = Web3.from_wei(gas_price, 'gwei'), Web3.from_wei(max_gas, 'gwei')
                gas_lock.set()
            else:
                gas_lock.clear()
            
        except Exception as error:
            pass
        sleep(randint(10, 20))


def main():
    starter = Starter()
    print(autosoft)
    print(subs_text)
    print("\n")
    f = open(f"{SETTINGS_PATH}to_run_addresses.txt", "r")
    addresses = f.read().lower().split("\n")
    f.close()
                
    action = get_action()
    if action == "Encode secrets":
        encode_secrets()
    else:
        gas_lock = Event()
        ender = Event()
        for i in range(len(addresses)):
            if len(addresses[i]) < 50:
                addresses[i] = "0x" + "0"*(42-len(addresses[i])) + addresses[i][2::]
            else:
                addresses[i] = "0x" + "0"*(66-len(addresses[i])) + addresses[i][2::]
        private_keys = decode_secrets()
        keys, counter = transform_keys(private_keys, addresses)
        print(f"Soft found {counter} keys to work")
        accounts = []
        shuffle(keys)
        if SETTINGS["useProxies"]:
            with open(f"{SETTINGS_PATH}proxies.txt", "r") as f:
                proxies_raw = f.read().split("\n")
            proxies = {}
            for proxy in proxies_raw:
                if proxy == "":
                    continue
                print(f'{proxy.split("@")[2]} connected to {"http://" + proxy.split("@")[0] + "@" + proxy.split("@")[1]}')
                proxies[proxy.split("@")[2].lower()] = "http://" + proxy.split("@")[0] + "@" + proxy.split("@")[1]
            for key in keys:
                accounts.append(Account(key, proxy=proxies[str(ethAccount.from_key(key).address).lower()]))
            
        else:
            for key in keys:
                accounts.append(Account(key))
        try:
            th = starter.start(action, gas_lock, accounts, ender)
            gas_locker(gas_lock, ender)
        except KeyboardInterrupt:
            th.kill()
            
if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
    input("Soft successfully end work. Press Enter to exit")


