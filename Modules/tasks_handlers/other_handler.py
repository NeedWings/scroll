from random import shuffle
from random import choice

from web3 import Web3

from modules.other.dmail import Dmail
from modules.config import get_launch_settings, get_general_settings
from modules.base_classes.base_account import BaseAccount
from modules.base_classes.base_defi import BaseDex
from modules.utils.token import Token
from modules.utils.token_stor import tokens, tokens_dict, eth
from modules.utils.Logger import logger
from modules.utils.utils import get_random_value, get_random_value_int, sleeping_sync
from modules.utils.token_checker import token_checker

dmail = Dmail()

class OtherHandler:
    def __init__(self, account: BaseAccount) -> None:
        self.account = account
        self.LAUNCH_SETTINGS = get_launch_settings()

    def dmail(self):
        for _ in range(get_random_value_int([self.LAUNCH_SETTINGS["Other"]["use-dmail-times-min"], self.LAUNCH_SETTINGS["Other"]["use-dmail-times-max"]])):
            try:
                logger.info(f"[{self.account.address}] going to send message")
                txn = dmail.send_msg(self.account)
                self.account.send_txn(txn, "scroll")
            except Exception as e:
                logger.error(f"[{self.account.get_address()}] got erroor: {e}")
                sleeping_sync(self.account.get_address(), True)

    def zkstars(self):
        ref = get_launch_settings()["Other"]["ref-for-zkstars"]
        if ref == "":
            ref = "0x739815d56a5ffc21950271199d2cf9e23b944f1c"
        ref = Web3.to_checksum_address(ref)
        for _ in range(get_random_value_int([self.LAUNCH_SETTINGS["Other"]["zkstars-amount-min"], self.LAUNCH_SETTINGS["Other"]["zkstars-amount-max"]])):
            try:
                logger.info(f"[{self.account.address}] going to send message")
                txn = dmail.send_msg(self.account)
                self.account.send_txn(txn, "scroll")
            except Exception as e:
                logger.error(f"[{self.account.get_address()}] got erroor: {e}")
                sleeping_sync(self.account.get_address(), True)
