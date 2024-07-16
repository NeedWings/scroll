from random import choice

from eth_abi import decode, encode

from modules.base_classes.base_account import BaseAccount
from modules.utils.Logger import logger
from modules.utils.txn_data_handler import TxnDataHandler
from modules.utils.utils import req, sleeping_sync, get_random_string, get_random_value_int
from modules.config import SETTINGS

class ScrollCanvas:

    badges = [
        "https://canvas.scroll.cat/badge/check?badge=0x3dacAd961e5e2de850F5E027c70b56b5Afa5DfeD&recipient=",
        "https://ambient-scroll-badge.liquidity.tools/api/check?badge=0xDaf958ec36dB494e82709a3AaB9FA6981EfC4Dad&recipient=",
        "https://ambient-scroll-badge.liquidity.tools/api/check?badge=0xC634b718618729df70331D79fcd6E889a547fbEB&recipient=",
        "https://ambient-scroll-badge.liquidity.tools/api/check?badge=0x21C5E85eBCbd924BA633D4A7A5F2718f25C713D8&recipient=",
        "https://ambient-scroll-badge.liquidity.tools/api/check?badge=0x7bD1AEADCc59EedaF4775E4D3197Ce9a7031BD01&recipient=",
        "https://zebra.xyz/api/badge/check?badge=0x09E14E520eec3583681Fe225a4B506743EC3cc78&recipient=",
        "https://api.scrolly.xyz/api/badge/check?badge=0x79b4f7492328D0Cc4ED0Ddaee08Cd42f0F36A4CC&recipient="
    ]



    def __init__(self, account: BaseAccount) -> None:
        self.account = account

    def mint_canvas(self):
        logger.info(f"[{self.account.address}] going to mint canvas")
        w3 = self.account.get_w3("scroll")
        txn_data_handler = TxnDataHandler(self.account, "scroll", w3=w3)
        if SETTINGS["Use Ref for Canvas"]:
            ref_code = choice(SETTINGS["Ref for Canvas"])
            resp = req(f"https://canvas.scroll.cat/code/{ref_code}/sig/{self.account.address}", proxies=self.account.proxies)
            signature = bytes.fromhex(resp["signature"][2::])
            value = int(0.0005*1e18)
        else:
            signature = b''        
            value = int(0.001*1e18)
        
        txn = txn_data_handler.get_txn_data(value)
        txn["to"] = "0xB23AF8707c442f59BDfC368612Bd8DbCca8a7a5a"
        txn["data"] = "0x4737576e" + encode(["string", "bytes"], [get_random_string(get_random_value_int([5,10])), signature]).hex()

        self.account.send_txn(txn, "scroll")
        sleeping_sync(self.account.address)
        
        



    def get_eligble_badges(self):
        logger.info(f"[{self.account.address}] checking for eligble badges")
        eligble = []

        for badge in self.badges:
            resp = req(f"{badge}{self.account.address}", proxies=self.account.proxies)
            eligibility = resp["eligibility"]
            if eligibility:
                eligble.append(badge)

        w3 = self.account.get_w3("scroll")
        data = w3.eth.call({"to": "0x74670A3998d9d6622E32D0847fF5977c37E0eC91", "data": f"0x70a08231000000000000000000000000{self.account.address[2::].lower()}"})
        amount = decode(["uint256"], data)[0]
        if amount > 0:
            eligble.append("origins")

        logger.info(f"[{self.account.address}] found {len(eligble)} eligble badges")

        return eligble
    
    def mint_badge(self, badge):
        w3 = self.account.get_w3("scroll")
        txn_data_handler = TxnDataHandler(self.account, "scroll", w3=w3)

        if badge != "origins":
            mint_data = req(f"{badge.replace('check', 'claim')}{self.account.address}", proxies=self.account.proxies)

            if mint_data["message"] != "success":
                logger.info(mint_data)
                return
            
            txn = txn_data_handler.get_txn_data()
            txn["data"] = mint_data["tx"]["data"]
            txn["to"] = w3.to_checksum_address(mint_data["tx"]["to"])
        else:
            txn = txn_data_handler.get_txn_data()
            data = w3.eth.call({"to": "0x74670A3998d9d6622E32D0847fF5977c37E0eC91", "data": f"0x2f745c59000000000000000000000000{self.account.address[2::].lower()}0000000000000000000000000000000000000000000000000000000000000000"})
            token_id = decode(["uint256"], data)[0]
            txn["to"] = "0xC47300428b6AD2c7D03BB76D05A176058b47E6B0"
            txn["data"] = "0xf17325e7" + encode(["(bytes32,(address,uint64,bool,bytes32,bytes,uint256))"], 
                                                [(bytes.fromhex("d57de4f41c3d3cc855eadef68f98c0d4edd22d57161d96b7c06d2f4336cc3b49"), 
                                                                (
                                                                    self.account.address,
                                                                    0,
                                                                    False,
                                                                    bytes.fromhex("0000000000000000000000000000000000000000000000000000000000000000"),
                                                                    bytes.fromhex(f"0000000000000000000000002dbce60ebeaafb77e5472308f432f78ac3ae07d90000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000004000000000000000000000000074670a3998d9d6622e32d0847ff5977c37e0ec910000000000000000000000{hex(token_id)[2::].rjust(42, '0')}"),
                                                                    0))]).hex()



        self.account.send_txn(txn, "scroll")
        sleeping_sync(self.account.address)

    def handle(self):

        eligble = self.get_eligble_badges()

        for badge in eligble:
            try:
                if badge == "origins":
                    logger.info(f"[{self.account.address}] going to mint badge: {badge}")
                else:
                    logger.info(f"[{self.account.address}] going to mint badge: {badge.split('?')[1].split('=')[1].split('&')[0]}")
                self.mint_badge(badge)
            except Exception as e:
                logger.error(f"[{self.account.address}] got error: {e}")
                sleeping_sync(self.account.address, True)

    