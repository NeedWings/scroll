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
        "https://api.scrolly.xyz/api/badge/check?badge=0x79b4f7492328D0Cc4ED0Ddaee08Cd42f0F36A4CC&recipient=",
        "https://pencilsprotocol.io/api/scroll/canvas/badge/pencil/check?badge=0x766e3f1EE86439DE0597F6e917F980A4e5d187A3&recipient=",
        "https://pencilsprotocol.io/api/scroll/canvas/badge/pencil/check?badge=0x2d8E67c1427a1ebb9ddB5c4D38143140B0c19aC8&recipient=",
        "https://vwb06c8e7h.execute-api.us-east-1.amazonaws.com/dev/check?badge=0x9aD600bDD45Cc30242fd905872962dc415F68530&recipient=",
        "https://passport-iam.gitcoin.co/scroll/check?badge=0xa623f348A12cFdC6B64a8c9e883dD9B243438E79&recipient=",
        "https://api.symbiosis.finance/crosschain/v1/scroll-badge/check?badge=0xB936740f00FFA90a55C362C33840913eaCFDcE25&recipient=",
        "https://mp.trustalabs.ai/attestations/media_badge/check?badge=0x47FF789Da49686C6cC38998F76F78A12A5939082&recipient=",
        "https://api.symbiosis.finance/crosschain/v1/scroll-badge/check?badge=0xaE98FC0e46977DaF650B180041dB20155ac66277&recipient=",
        "https://api.symbiosis.finance/crosschain/v1/scroll-badge/check?badge=0x3c1A82D5877AB970Be9d80AB8185C5F9F1505C49&recipient=",
        "https://api.symbiosis.finance/crosschain/v1/scroll-badge/check?badge=0x66703cd7eBA1b114cA652b1C2DE268858cBedEc8&recipient=",
        "https://scroll-canvas-api.xname.app/api/check?badge=0x7C0deB6aBf29cC829186933720af67da8B1EF633&recipient=",
        "https://scroll-canvas-api.xname.app/api/domain/check?badge=0xed269A526ad793CcB671Ef55A7AF6E45F300d462&recipient=",
        "https://api.omnihub.xyz/api/integration/scroll/check?badge=0xdd8CCDad022999afD61DFda146e4C40F47dE4Eec&recipient=",
        "https://mp.trustalabs.ai/attestations/poh_badge/check?badge=0x26B97C832C04C06cAd34dCE23c701beDC3555a5c&recipient=",
        "https://backend.retrobridge.io/api/quest/check?badge=0x59700c6Ed282eD7611943129f226914ACBB3982b&recipient=",
        "https://api.symbiosis.finance/crosschain/v1/scroll-badge/check?badge=0x0a584c042133aF17f3e522F09A77Ee1496f3a567&recipient=",
        "https://api.smilecobra.io/tripartite/scroll/badge/check?badge=0x7ecf596Ed5fE6957158cD626b6bE2A667267424f&recipient=",
        "https://publicapi.xenobunny.xyz/canvas/lands/check?badge=0x7188B352C818f291432CDe8E4B1f0576c188F9e4&recipient=",
        "https://api.symbiosis.finance/crosschain/v1/scroll-badge/check?badge=0xB69cF3247b60F72ba560B3C1e0F53DAF9e9D5201&recipient=",
        "https://api.symbiosis.finance/crosschain/v1/scroll-badge/check?badge=0x35CB802ede5f970AE6d7B8E7b7b82C82Fea273C7&recipient=",
        "https://api.symbiosis.finance/crosschain/v1/scroll-badge/check?badge=0x4445BE64c03154052bd661fD1B0d01FC625Df06E&recipient=",
        "https://api.symbiosis.finance/crosschain/v1/scroll-badge/check?badge=0x475d1E9Be98B7B7b97D7ED9695541A0209e982dE&recipient=",
        "https://api.symbiosis.finance/crosschain/v1/scroll-badge/check?badge=0xCA5d53f143822dd8b9789b1A12d2a10A39a499e4&recipient=",
        "https://api.symbiosis.finance/crosschain/v1/scroll-badge/check?badge=0x9765B7B7926Cb27b84f5F48EA0758Fa99da3C7d6&recipient=",
        "https://api.symbiosis.finance/crosschain/v1/scroll-badge/check?badge=0x6d352E2987C0AC7D896B74453f400477dE7446F0&recipient=",
        "https://api.symbiosis.finance/crosschain/v1/scroll-badge/check?badge=0x5bA1cC19C89BeD7d4660316D1eB41B6A581B98c7&recipient=",
        "https://api.symbiosis.finance/crosschain/v1/scroll-badge/check?badge=0xCd223ce0Cc6C05c1604f8f83A50e98202E600bD6&recipient=",
        "https://api.symbiosis.finance/crosschain/v1/scroll-badge/check?badge=0x3573335B5128F50F79617f1218f2A7aA0EE68703&recipient="
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
        w3 = self.account.get_w3("scroll")

        for badge in self.badges:
            resp = req(f"{badge}{self.account.address}", return_on_fail=True, proxies=self.account.proxies)
            if resp is None:
                continue
            eligibility = resp["eligibility"]
            if eligibility:
                data = w3.eth.call({"to": badge.split('?')[1].split('=')[1].split('&')[0], "data": f"0x5e50864f000000000000000000000000{self.account.address[2::].lower()}"})
                have_minted = decode(["bool"], data)[0]
                if have_minted:
                    continue
                eligble.append(badge)

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

    