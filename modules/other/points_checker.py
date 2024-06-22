from modules.utils.account import Account
from modules.utils.utils import req
from modules.utils.Logger import logger
from modules.config import SETTINGS_PATH

class PointsChecker:

    def __init__(self, account: Account) -> None:
        self.account = account
        self.proxies = self.account.proxies

    def wrap(self, data):
        return {data["bridge_asset"]: str(round(data["points"], 5)).replace(".", ",")}
        
    def get_total_points(self):
        resp = req(f"https://kx58j6x5me.execute-api.us-east-1.amazonaws.com/scroll/wallet-points?walletAddress={self.account.address}", proxies=self.proxies)
        return str(round(resp[0]["points"], 5)).replace(".", ",")
    
    def get_points_for_hold(self):
        data = {
            "ETH": "0",
            "USDT": "0",
            "USDC": "0"
        }
        resp = req(f"https://kx58j6x5me.execute-api.us-east-1.amazonaws.com/scroll/bridge-balances?walletAddress={self.account.address}", proxies=self.proxies)
        for i in list(map(self.wrap, resp)):
            data.update(i)
        return data
    
    def write(self, data):
        with open(f"{SETTINGS_PATH}scroll-points.csv", "r") as f:
            prev = f.read()

        prev += "\n" + data

        with open(f"{SETTINGS_PATH}scroll-points.csv", "w") as f:
            f.write(prev)

    def handle(self):
        hold_points = self.get_points_for_hold()
        total = self.get_total_points()

        data = f"{self.account.address};{hold_points['ETH']};{hold_points['USDT']};{hold_points['USDC']};{total}"

        logger.info(f"[{self.account.address}] ETH: {hold_points['ETH']} USDC: {hold_points['USDC']} USDT: {hold_points['USDT']} Total: {total}")

        self.write(data)