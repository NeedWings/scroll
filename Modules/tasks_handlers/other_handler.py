from web3 import Web3

from modules.other.dmail import Dmail
from modules.other.zkstars import ZkStars
from modules.config import SETTINGS
from modules.base_classes.base_account import BaseAccount
from modules.utils.Logger import logger
from modules.utils.utils import get_random_value_int, sleeping_sync

dmail = Dmail()
zkstars = ZkStars()

class OtherHandler:
    def __init__(self, account: BaseAccount) -> None:
        self.account = account

    def dmail(self):
        for _ in range(get_random_value_int(SETTINGS["Use dmail times"])):
            try:
                logger.info(f"[{self.account.address}] going to send message")
                txn = dmail.send_msg(self.account)
                self.account.send_txn(txn, "scroll")
            except Exception as e:
                logger.error(f"[{self.account.get_address()}] got erroor: {e}")
                sleeping_sync(self.account.get_address(), True)

    def zkstars(self):
        ref = SETTINGS["Ref for ZkStars"]
        if ref == "":
            ref = "0x739815d56a5ffc21950271199d2cf9e23b944f1c"
        for _ in range(get_random_value_int(SETTINGS["ZkSars Mints Amount"])):
            try:
                logger.info(f"[{self.account.address}] going to mint zkstars")
                ref = Web3.to_checksum_address(ref)
                txn = zkstars.get_txn_for_mint(ref, self.account)
                self.account.send_txn(txn, "scroll")
            except Exception as e:
                logger.error(f"[{self.account.get_address()}] got erroor: {e}")
                sleeping_sync(self.account.get_address(), True)

