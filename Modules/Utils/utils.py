import random
import requests
from Modules.Utils.Logger import logger, console_log
import time
from Modules.config import SETTINGS_PATH, get_general_settings
import string
from threading import Event
from web3 import Web3
import json

def get_random_value_int(param):
    return random.randint(int(param[0]), int(param[1]))

def get_random_value(param):
    return random.uniform(float(param[0]), float(param[1]))

def param_to_list_selected(param):
    res = []
    for i in param:
        if param[i]:
            res.append(i)
    return res

def sleeping_sync(address, error = False):
    settings = get_general_settings()
    task_sleep = [int(settings["TimeSleeps"]["task-sleep-min"]), int(settings["TimeSleeps"]["task-sleep-max"])]
    error_sleeping = [int(settings["TimeSleeps"]["task-sleep-min"]), int(settings["TimeSleeps"]["task-sleep-max"])]
    if error:
        rand_time = get_random_value_int(error_sleeping)
    else:
        rand_time = get_random_value_int(task_sleep)
    logger.info(f'[{address}] sleeping {rand_time} s')
    time.sleep(rand_time)

def get_pair_for_address_from_file(filename: str, address: str):
    address = address.lower()
    with open(f"{SETTINGS_PATH}{filename}", "r") as f:
        buff = f.read().lower().split("\n")
    pairs_raw = []
    for i in buff:
        if ";" in i:
            pairs_raw.append(i)

    for pair in pairs_raw:
        if pair.split(";")[0] == address:
            return Web3.to_checksum_address(pair.split(";")[1])
    return None


def req_post(url: str, **kwargs):
    settings = get_general_settings()
    while True:
        try:
            resp = requests.post(url, **kwargs)
            if resp.status_code == 200:
                return resp.json()
            else:
                console_log.error("Bad status code, will try again")
                pass
        except Exception as error:
            console_log.error(f"Requests error: {error}")
        
        time.sleep(get_random_value([settings["TimeSleeps"]["error-sleep-min"], settings["TimeSleeps"]["error-sleep-max"]]))


def req(url: str, **kwargs):
    settings = get_general_settings()
    while True:
        try:
            resp = requests.get(url, **kwargs)
            if resp.status_code == 200:
                return resp.json()
            else:
                console_log.error("Bad status code, will try again")
                pass
        except Exception as error:
            console_log.error(f"Requests error: {error}")
        time.sleep(get_random_value([settings["TimeSleeps"]["error-sleep-min"], settings["TimeSleeps"]["error-sleep-max"]]))

def get_random_string(length: int) -> str:
    letters = string.ascii_lowercase + "1234567890"
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


def decimal_to_int(qty, decimal):
    return int(qty * int("".join(["1"] + ["0"]*decimal)))

def base36encode(number, alphabet='0123456789abcdefghijklmnopqrstuvwxyz'):
    """Converts an integer to a base36 string."""
    if not isinstance(number, int):
        raise TypeError('number must be an integer')
 
    base36 = ''
    sign = ''
 
    if number < 0:
        sign = '-'
        number = -number
 
    if 0 <= number < len(alphabet):
        return sign + alphabet[number]
 
    while number != 0:
        number, i = divmod(number, len(alphabet))
        base36 = alphabet[i] + base36
 
    return sign + base36