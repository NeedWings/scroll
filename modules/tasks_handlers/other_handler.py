from random import choice

from web3 import Web3

from modules.other.dmail import Dmail
from modules.other.zkstars import ZkStars
from modules.other.check_in import CheckIn
from modules.other.alpha_key import AlphaKey
from modules.other.points_checker import PointsChecker
from modules.config import SETTINGS
from modules.base_classes.base_account import BaseAccount
from modules.utils.Logger import logger
from modules.utils.utils import get_random_value_int, sleeping_sync
from modules.utils.token import ERC721Token

dmail = Dmail()
zkstars = ZkStars()
check_in = CheckIn()

class OtherHandler:
    def __init__(self, account: BaseAccount) -> None:
        self.account = account
        self.checker = PointsChecker(self.account)
        self.alpha_key = AlphaKey(self.account)

    def dmail(self):
        for _ in range(get_random_value_int(SETTINGS["Use dmail times"])):
            try:
                logger.info(f"[{self.account.address}] going to send message")
                txn = dmail.send_msg(self.account)
                self.account.send_txn(txn, "scroll")
                sleeping_sync(self.account.get_address())
            except Exception as e:
                logger.error(f"[{self.account.get_address()}] got erroor: {e}")
                sleeping_sync(self.account.get_address(), True)

    def check_contracts(self):
        logger.info(f"[{self.account.address}] checking contracts")
        contracts = zkstars.contracts.copy()
        used = []

        for i in range(len(contracts)):
            token = ERC721Token("ZkStars NFT", contracts[i], "scroll")
            balance = self.account.get_balance(token)
            if balance > 0:
                used.append(contracts[i])

        for address in used:
            contracts.remove(address)

        return contracts        


    def zkstars(self):
        ref = SETTINGS["Ref for ZkStars"]
        if ref == "":
            ref = "0x739815d56a5ffc21950271199d2cf9e23b944f1c"
        if SETTINGS["Do not mint minted"]:
            not_used_contracts = self.check_contracts()
            for _ in range(get_random_value_int(SETTINGS["ZkSars Mints Amount"])):
                try:
                    if len(not_used_contracts) == 0:
                        logger.info(f"[{self.account.address}] all NFTs minted")
                        return
                    to_mint = choice(not_used_contracts)
                    logger.info(f"[{self.account.address}] going to mint zkstars")
                    ref = Web3.to_checksum_address(ref)
                    txn = zkstars.get_txn_for_mint(ref, self.account, to_mint)
                    self.account.send_txn(txn, "scroll")
                    not_used_contracts.remove(to_mint)
                    sleeping_sync(self.account.get_address())
                except Exception as e:
                    logger.error(f"[{self.account.get_address()}] got erroor: {e}")
                    sleeping_sync(self.account.get_address(), True)
        else:
            for _ in range(get_random_value_int(SETTINGS["ZkSars Mints Amount"])):
                try:
                    logger.info(f"[{self.account.address}] going to mint zkstars")
                    ref = Web3.to_checksum_address(ref)
                    txn = zkstars.get_txn_for_mint(ref, self.account)
                    self.account.send_txn(txn, "scroll")
                    sleeping_sync(self.account.get_address())
                except Exception as e:
                    logger.error(f"[{self.account.get_address()}] got erroor: {e}")
                    sleeping_sync(self.account.get_address(), True)

    def checkin_owlto(self):
        logger.info(f"[{self.account.address}] going to check in in owlto")
        txn = check_in.owlto(self.account)
        self.account.send_txn(txn, "scroll")
        sleeping_sync(self.account.get_address())

    def checkin_rubyscore(self):
        logger.info(f"[{self.account.address}] going to check in in rubyscore")
        txn = check_in.rubyscore(self.account)
        self.account.send_txn(txn, "scroll")
        sleeping_sync(self.account.get_address())

    def check_points(self):
        self.checker.handle()
        sleeping_sync(self.account.get_address())

    def mint_alpha_key(self):
        txn = self.alpha_key.mint()
        self.account.send_txn(txn, "scroll")
        sleeping_sync(self.account.get_address())
