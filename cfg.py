from abi import *
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union, cast
from random import shuffle
import multiprocessing
from threading import Thread
try:
    import Crypto.Hash._keccak
    import cytoolz._signatures
    import Crypto.Cipher._raw_ecb
    import Crypto.Cipher._raw_cbc
    import Crypto.Cipher._raw_aes
    import Crypto.Cipher._raw_cfb
    import Crypto.Cipher._raw_ctr
    import Crypto.Cipher._raw_des
    import Crypto.Cipher._raw_aes
    import Crypto.Cipher._raw_ofb
    import Crypto.Cipher._raw_aesni
    import Crypto.Cipher._raw_des3
    import Crypto.Cipher._raw_ofb
    import Crypto.Cipher._raw_ocb
    import Crypto.Cipher._raw_eksblowfish
    import Crypto.Util._strxor
    import Crypto.Util._raw_api
    import Crypto.Util._cpu_features
    import Crypto.Util._cpuid_c
    import Crypto.Util._file_system
    import Crypto.Util._strxor
    import Crypto.Hash._BLAKE2b
    import Crypto.Hash._BLAKE2s
    import Crypto.Hash._ghash_clmul
    import Crypto.Hash._ghash_portable
    import Crypto.Hash._SHA1
    import Crypto.Hash._SHA224
    import Crypto.Hash._SHA256
    import Crypto.Hash._SHA384
    import Crypto.Hash._SHA512
    import Crypto.Hash._MD2
    import Crypto.Hash._MD4
    import Crypto.Hash._MD5
    import Crypto.Cipher._Salsa20
    import Crypto.Cipher._ARC4
    import Crypto.Cipher._EKSBlowfish
    import Crypto.Cipher._chacha20
    import Crypto.Protocol._scrypt
    import Crypto.PublicKey._ec_ws
    import Crypto.PublicKey._ed25519
    import Crypto.PublicKey._ed448
    import Crypto.PublicKey._ed448
    import Crypto.PublicKey._openssh
    import Crypto.PublicKey._x25519
    import Crypto
    import eth_hash.backends.pycryptodome
except:
    pass
from eth_hash.auto import keccak
import random
import time
import json
import asyncio
import base64
from typing import (
    Optional
)
from typing_extensions import Literal
import requests
from web3 import Web3
from eth_account import Account as ethAccount
import uuid
import decimal
from os import getcwd
import os
import base64
from cryptography.fernet import Fernet
import getpass
import hashlib
import sys
import socket
import wmi
from aiohttp import ClientSession
import sys, os
import inquirer
from termcolor import colored
from inquirer.themes import load_theme_from_dict as loadth
import datetime
from time import sleep
from web3.contract.contract import Contract
from eth_account.messages import encode_structured_data, encode_defunct
from eth_keys import keys
import eth_abi
from eth_keys.datatypes import PublicKey
def override_where():
    """ overrides certifi.core.where to return actual location of cacert.pem"""
    # change this to match the location of cacert.pem
    return os.path.abspath("data/cacert.pem")


# is the program compiled?
if True:
    import certifi.core

    os.environ["REQUESTS_CA_BUNDLE"] = override_where()
    certifi.core.where = override_where

    # delay importing until after where() has been replaced
    import requests.utils
    import requests.adapters
    # replace these variables in case these modules were
    # imported before we replaced certifi.core.where
    requests.utils.DEFAULT_CA_BUNDLE_PATH = override_where()
    requests.adapters.DEFAULT_CA_BUNDLE_PATH = override_where()

def str_to_felt(text: str) -> int:
    b_text = bytes(text, 'UTF-8')
    return int.from_bytes(b_text, "big")

def get_bytes(value: str) -> str:
    i = len(value)
    return '0x' + ''.join('0' for k in range(64-i)) + value

def get_orbiter_value(base_num: float):
    base_num_dec = decimal.Decimal(str(base_num))
    orbiter_amount_dec = decimal.Decimal(str(0.000000000000009004))
    difference = base_num_dec - orbiter_amount_dec
    random_offset = decimal.Decimal(str(random.uniform(-0.000000000000001, 0.000000000000001)))
    result_dec = difference + random_offset
    orbiter_str = "9004"
    result_str = '{:.18f}'.format(result_dec.quantize(decimal.Decimal('0.000000000000000001')))
    result_str = result_str[:-4] + orbiter_str
    return decimal.Decimal(result_str)

def json_remove_comments(invalid_json: str):
    comment_start = -1
    for char in range(len(invalid_json)):
        if invalid_json[char:char+4] == ", //":
                comment_start = char+1
        
        if invalid_json[char] == "\n" and comment_start != -1:
            invalid_json = invalid_json[0:comment_start] + invalid_json[char:len(invalid_json)]
            return json_remove_comments(invalid_json)
    return invalid_json


autosoft = """

 _______          _________ _______  _______  _______  _______ _________
(  ___  )|\     /|\__   __/(  ___  )(  ____ \(  ___  )(  ____ \\__   __/
| (   ) || )   ( |   ) (   | (   ) || (    \/| (   ) || (    \/   ) (   
| (___) || |   | |   | |   | |   | || (_____ | |   | || (__       | |   
|  ___  || |   | |   | |   | |   | |(_____  )| |   | ||  __)      | |   
| (   ) || |   | |   | |   | |   | |      ) || |   | || (         | |   
| )   ( || (___) |   | |   | (___) |/\____) || (___) || )         | |   
|/     \|(_______)   )_(   (_______)\_______)(_______)|/          )_(   

"""
subs_text = """
You have purchased an AutoSoft software license.
Thank you for your trust.
Link to the channel with announcements: t.me/swiper_tools
Ask all questions in our chat.

"""

KEY = "CEy426oSSaOTWDPgtuKxm1nS2uWN_4-L_eyt0dmAr40="
SETTINGS_PATH = getcwd() + '\\data\\'

CONTRACT_ADDRESS_PREFIX = str_to_felt('STARKNET_CONTRACT_ADDRESS')
UNIVERSAL_DEPLOYER_PREFIX = str_to_felt('UniversalDeployerContract')


WETH = {
    "arbitrum": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
}

ROUTES = {
    "arbitrum": {
        "USDC": "0x02ff970a61a04b1ca14834a43f5de4533ebddb5cc801ffff0115e444da5b343c5a0931f5d3e85d158d1efc3d4000fc506aaa1340b4dedffd88be278bee058952d6740182af49447d8a07e3bd95bd0d56f35241523fbab101ffff0200",
        "USDT": "0x02fd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb901ffff00cb0e5bfa72bbb4d16ab5aa0c60601c438f04b4ad00fc506aaa1340b4dedffd88be278bee058952d6740182af49447d8a07e3bd95bd0d56f35241523fbab101ffff0200"
    }
}

STARKGATE_CONTRACT = "0xae0Ee0A63A2cE6BaeEFFE56e7714FB4EFE48D419"
ORBITER_CONTRACTS_REC = "0xE4eDb277e41dc89aB076a1F049f4a3EfA700bCE8"
ORBITER_CONTRACT = "0xD9D74a29307cc6Fc8BF424ee4217f1A587FBc8Dc"
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

print(SETTINGS_PATH)
try:
    f = open(f"{SETTINGS_PATH}settings.json", "r")
    a = json_remove_comments(f.read())
    SETTINGS = json.loads(a)
    f.close()
except Exception as e:
    input("Error with settings.json")
    exit()

INF_VALUE = 115792089237316195423570985008687907853269984665640564039457584007913129639935


ETH_RPC = SETTINGS["RPC"]["ethereum"]
OPTI_RPC = SETTINGS["RPC"]["optimism"]
ARB_RPC = SETTINGS["RPC"]["arbitrum"]
BSC_RPC = SETTINGS["RPC"]["bsc"]
POLYGON_RPC = SETTINGS["RPC"]["polygon"]
AVAX_RPC = SETTINGS["RPC"]["avalanche"]
SCROLL_RPC = SETTINGS["RPC"]["scroll"]


RPC_LSIT = {
    "ethereum": ETH_RPC,
    "optimism": OPTI_RPC,
    "arbitrum": ARB_RPC,
    "bsc": BSC_RPC,
    "polygon": POLYGON_RPC,
    "avalanche": AVAX_RPC,
    "scroll": SCROLL_RPC
}





MASK_250 = 2**250 - 1


proxy_dict_cfg = {

}

NATIVE_TOKENS_SYMBOLS = {
     "zkevm": "ETH",
     "arbitrum": "ETH",
     "polygon": "MATIC",
     "bsc": "BNB",
     "optimism": "ETH",
     "avalanche": "AVAX",
     "ethereum": "ETH",
     "base": "ETH",
     "scroll":"ETH"
}
NATIVE_WRAPPED_CONTRACTS = {
    "arbitrum": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
    "optimism": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
    "ethereum": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
    "base": "0x4200000000000000000000000000000000000006",
    "scroll": "0x5300000000000000000000000000000000000004"
}

slippage = SETTINGS["Slippage"]



out_wallets_result = {
    
}
addr_dict = {}

indexes = []

def req_post(url: str, **kwargs):
    try:
        resp = requests.post(url, **kwargs)
        if resp.status_code == 200:
            return resp.json()
        else:
            logger.error("Bad status code, will try again")
            pass
    except Exception as error:
        logger.error(f"Requests error: {error}")



async def handle_dangerous_request(func, message, address = "", *args):
    while True:
        try:
            return await func(*args)
        except Exception as e:
            pass
            logger.error(f"[{address}] {message}: {e}")
            await sleeping(address, True)

def get_random_value_int(param):
    return random.randint(param[0], param[1])

def get_random_value(param):
    return random.uniform(param[0], param[1])


def sleeping_sync(address, error = False):
    if error:
        rand_time = random.randint(SETTINGS["ErrorSleepeng"][0], SETTINGS["ErrorSleepeng"][1])
    else:
        rand_time = random.randint(SETTINGS["TaskSleep"][0], SETTINGS["TaskSleep"][1])
    logger.info(f'[{address}] sleeping {rand_time} s')
    time.sleep(rand_time)


with open(f"{SETTINGS_PATH}starkstats.csv", "w") as f:
    f.write("address;txn count;ETH balance;USDC balance;USDT balance;DAI balance;WBTC balance;WSTETH balance;LORDS balance\n")

starkstats = ""

from loguru import logger as console_log

global_log = {}
indexes = []
pairs_for_okx = {}

date_and_time = str(datetime.datetime.now()).replace(":", ".")

def write_global_log():
    log = ""
    for key in global_log:
        buff = f"{key}:\n"
        for data in global_log[key]:
            buff += f"{data}\n" 
        log += buff + "\n"
    with open(f"{SETTINGS_PATH}logs/log_{date_and_time}.txt", "w") as f:
        f.write(log)

class logger():
    @staticmethod
    def info(message: str):
        try:

            addr = message.split("]")[0][1::]
            if addr not in indexes:
                indexes.append(addr)
            console_log.info(f"[{addr}] [{indexes.index(addr)+1}/{len(indexes)}] {message.split(']')[1]}")
            if addr not in list(global_log.keys()):
                global_log[addr] = [f"[INFO] [{indexes.index(addr)+1}/{len(indexes)}] {message.split(']')[1]}"]
            else:
                global_log[addr].append(f"[INFO] [{indexes.index(addr)+1}/{len(indexes)}] {message.split(']')[1]}")
            write_global_log()
        except:
            pass
    
    @staticmethod
    def error(message: str):
        try:
            addr = message.split("]")[0][1::]
            if addr not in indexes:
                indexes.append(addr)
            msg = ""
            for i in range(1, len(message.split("]"))):
                msg += message.split("]")[i]
                if i < len(message.split("]"))-1:
                    msg += "]"
            console_log.error(f"[{addr}] [{indexes.index(addr)+1}/{len(indexes)}] {msg}")
            if addr not in list(global_log.keys()):
                global_log[addr] = [f"[ERROR] [{indexes.index(addr)+1}/{len(indexes)}] {msg}"]
            else:
                global_log[addr].append(f"[ERROR] [{indexes.index(addr)+1}/{len(indexes)}] {msg}")

            write_global_log()
        except:
            pass
    
    @staticmethod
    def success(message: str):
        try:
            addr = message.split("]")[0][1::]
            if addr not in indexes:
                indexes.append(addr)
            console_log.success(f"[{addr}] [{indexes.index(addr)+1}/{len(indexes)}] {message.split(']')[1]}")
            if addr not in list(global_log.keys()):
                global_log[addr] = [f"[SUCCESS] [{indexes.index(addr)+1}/{len(indexes)}] {message.split(']')[1]}"]
            else:
                global_log[addr].append(f"[SUCCESS] [{indexes.index(addr)+1}/{len(indexes)}] {message.split(']')[1]}")

            write_global_log()
        except:
            pass


async def sleeping(address, error = False):
        if error:
            rand_time = random.randint(SETTINGS["ErrorSleepeng"][0], SETTINGS["ErrorSleepeng"][1])
        else:
            rand_time = random.randint(SETTINGS["TaskSleep"][0], SETTINGS["TaskSleep"][1])
        logger.info(f'[{address}] sleeping {rand_time} s')
        await asyncio.sleep(rand_time)


true = True
false = False