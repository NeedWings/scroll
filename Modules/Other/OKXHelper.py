from Modules.BaseClasses.BaseAccount import BaseAccount
from Modules.Utils.Logger import logger
from Modules.Utils.TxnDataHandler import TxnDataHandler
from Modules.Utils.utils import sleeping_sync, get_random_value, get_random_value_int, get_pair_for_address_from_file, param_to_list_selected
from Modules.Utils.token_stor import nets_eth
from Modules.config import get_launch_settings, get_general_settings
from random import choice
import requests
import ccxt
from time import sleep
import base64
import hmac




class OKXHelper:
    net_names = {
        "arbitrum": "Arbitrum One",
        "optimism": "Optimism",
        "zksync": "zkSync Era",
        "linea": "Linea"
    }

    fees = {
        "arbitrum":  0.0001,
        "optimism":  0.0001,
        "zksync": 0.00015,
        "linea": 0.0002
    }
    def __init__(self, api_key: str, secret: str, password: str, account: BaseAccount) -> None:
        self.LAUNCH_SETTINGS = get_launch_settings()
        self.GENERAL_SETTINGS = get_general_settings()

        self.okx_account = ccxt.okex5({
            'apiKey': api_key,
            'secret': secret,
            'password': password,
            'enableRateLimit': True,
        })
        self.account = account

    def okx_data(self, api_key, secret_key, passphras, request_path="/api/v5/account/balance?ccy=USDT", body='', meth="GET"):
        try:
            import datetime
            def signature(
                timestamp: str, method: str, request_path: str, secret_key: str, body: str = ""
            ) -> str:
                if not body:
                    body = ""

                message = timestamp + method.upper() + request_path + body
                mac = hmac.new(
                    bytes(secret_key, encoding="utf-8"),
                    bytes(message, encoding="utf-8"),
                    digestmod="sha256",
                )
                d = mac.digest()
                return base64.b64encode(d).decode("utf-8")

            dt_now = datetime.datetime.utcnow()
            ms = str(dt_now.microsecond).zfill(6)[:3]
            timestamp = f"{dt_now:%Y-%m-%dT%H:%M:%S}.{ms}Z"

            base_url = "https://www.okex.com"
            headers = {
                "Content-Type": "application/json",
                "OK-ACCESS-KEY": api_key,
                "OK-ACCESS-SIGN": signature(timestamp, meth, request_path, secret_key, body),
                "OK-ACCESS-TIMESTAMP": timestamp,
                "OK-ACCESS-PASSPHRASE": passphras,
                'x-simulated-trading': '0'
            }
        except Exception as ex:
            logger.error(f"[{self.account.address}] got error: {ex}")
        return base_url, request_path, headers

    def withdraw(self, amount, net):
        try:            
            self.okx_account.withdraw(
                code    = "ETH",
                amount  = amount,
                address = self.account.address,
                tag     = None, 
                params  = {
                    "network": self.net_names[net],
                    "fee": self.fees[net],
                    "pwd": self.okx_account.password
                }
            )
            logger.success(f"[{self.account.address}] withdraw successfull: {amount}")
            return True
        
        except Exception as error:
            logger.error(f"[{self.account.address}] got errror : {error}")
        return False

    def withdraw_handl(self):
        net = choice(param_to_list_selected(self.LAUNCH_SETTINGS["OKX"]["NetsForOKX"]))
        start_balance = self.account.get_balance(nets_eth[net])[1]
        new_balance = start_balance
        res = False
        while not res:
            to_withdraw = get_random_value([self.LAUNCH_SETTINGS["OKX"]["to-withdraw-from-okx-min"], self.LAUNCH_SETTINGS["OKX"]["to-withdraw-from-okx-max"]])
    
            logger.info(f"[{self.account.address}] going to withdraw {to_withdraw} ETH from OKX")
            res = self.withdraw(to_withdraw, net)
            if not res:
                logger.error(f"[{self.account.address}] got error. trying to send from subs")
                self.transfer_to_main_account()
                sleeping_sync(self.account.address, True)
        while new_balance == start_balance:
            new_balance = self.account.get_balance(nets_eth[net])[1]

            logger.info(f"[{self.account.address}] waiting for balance. current: {new_balance} ETH")
            
            sleeping_sync(self.account.address)

        logger.success(f"[{self.account.address}] found balance! Current: {new_balance} ETH")

    def deposit(self, to: str, amount: float, from_net: str):
        
        try:
            w3 = self.account.get_w3(from_net)
            txn_data_handler = TxnDataHandler(self.account, from_net, w3=w3)
            txn = txn_data_handler.get_txn_data(value=int(amount*1e18))
            txn["to"] = to

            self.account.send_txn(txn, from_net)
            return True
        except Exception as e:
            logger.error(f"[{self.account.address}] can't deposit to okx. Error: {e}")
            return False
        
    def deposit_handl(self):
        
        rec = get_pair_for_address_from_file("okx_wallet_pairs.txt", self.account.address)
        if not rec:
            logger.error(f"[{self.account.address}] can't find pair. Skip")
            return
        net = param_to_list_selected(self.LAUNCH_SETTINGS["OKX"]["send-to-okx-from"])[0]
        eth = nets_eth[net]
        new_balance = self.account.get_balance(eth)[1]
        
        res = False
        for i in range(10):
            to_withdraw = new_balance - get_random_value([self.LAUNCH_SETTINGS["Bridges"]["save-when-withdraw-min"], self.LAUNCH_SETTINGS["Bridges"]["save-when-withdraw-max"]])
            logger.info(f"[{self.account.address}] going to send {to_withdraw} ETH to {rec}")
            res = self.deposit(rec, to_withdraw, net)
            if not res:
                sleeping_sync(self.account.address, True)
            if res:
                break
        logger.info(f"[{self.account.address}] waiting {self.LAUNCH_SETTINGS['OKX']['wait-for-okx-deposit']} minutes")
        sleep(self.LAUNCH_SETTINGS["OKX"]['wait-for-okx-deposit']*60)
        self.transfer_to_main_account()

    def transfer_to_main_account(self):
        
        api_key = self.okx_account.apiKey
        secret = self.okx_account.secret
        password =  self.okx_account.password
        session = requests.Session()
        
        _, _, headers = self.okx_data(api_key, secret, password, request_path=f"/api/v5/users/subaccount/list", meth="GET")
        while True:
            try:
                list_sub =  session.get("https://www.okx.cab/api/v5/users/subaccount/list", timeout=10, headers=headers).json()
                list_sub["data"]
                break
            except:
                sleep(2)
        for sub_data in list_sub['data']:

            name_sub = sub_data['subAcct']

            _, _, headers = self.okx_data(api_key, secret, password, request_path=f"/api/v5/asset/subaccount/balances?subAcct={name_sub}&ccy=ETH", meth="GET")
            while True:
                try:
                    sub_balance = session.get(f"https://www.okx.cab/api/v5/asset/subaccount/balances?subAcct={name_sub}&ccy=ETH",timeout=10, headers=headers)
                    sub_balance = sub_balance.json()  
                    sub_balance = sub_balance['data'][0]['bal']
                    break
                except:
                    sleep(4)
            logger.info(f'[{self.account.address}] {name_sub} | sub_balance : {sub_balance} ETH')
            if float(sub_balance) > 0:
                while True:
                    body = {"ccy": f"ETH", "amt": str(sub_balance), "from": 6, "to": 6, "type": "2", "subAcct": name_sub}

                    _, _, headers = self.okx_data(api_key, secret, password, request_path=f"/api/v5/asset/transfer", body=str(body), meth="POST")
                    a = session.post("https://www.okx.cab/api/v5/asset/transfer", data=str(body), timeout=10, headers=headers)
                    if a.status_code != 200:
                        logger.error(f"[{self.account.address}] failed to send from sub: {a.text}")
                        sleeping_sync(self.account.address, True)
                        continue
                    logger.success(f"[{self.account.address}] sent from sub({name_sub}) ")
                    sleep(1)
                    break