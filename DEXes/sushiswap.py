from BaseClasses import *
from token_stor import *

class SushiSwap:
    contract_addresses = {
        "ethereum": "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F",
        "arbitrum": "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506"
    }
    weth = {
        "ethereum": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        "arbitrum": "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1"
    }
    def swap_token_for_eth(self, token: EVMToken, amount_in: float, sender: BaseAccount):

        txn_data_handler = EVMTransactionDataHandler(sender, token.net_name)
        w3: Web3 = Web3(Web3.HTTPProvider(random.choice(RPC_LSIT[token.net_name])))
        contract = w3.eth.contract(self.contract_addresses[token.net_name], abi=SUSHI)

        usd_val = token.get_usd_value(amount_in)
        eth_price = eth.get_price()
        eth_val = usd_val/eth_price
        eth_val = int((1-SETTINGS["Slippage"])*eth_val*1e18)
        logger.info(f"[{sender.get_address()}] going to swap {amount_in} {token.symbol} for ETH")
        approve_txn = token.get_approve_txn(sender, self.contract_addresses[token.net_name], int(amount_in*10**token.decimals))
        txn = contract.functions.swapExactTokensForETH(
            int(amount_in*10**token.decimals),
            eth_val,
            [
                token.contract_address,
                self.weth[token.net_name]
            ],
            sender.get_address(),
            int(time.time()+3600)
        ).build_transaction(txn_data_handler.get_txn_data())

        sender.send_txn([txn], token.net_name)
        return


        
