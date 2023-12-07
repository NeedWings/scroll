from BaseClasses import *


eth = EVMNativeToken("scroll")
usdt = EVMToken("USDT", "0xf55BEC9cafDbE8730f096Aa55dad6D22d44099Df", 6, "scroll", stable=True)
dai = EVMToken("DAI", "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb", 18, "scroll", stable=True)
usdc = EVMToken("USDC", "0x06eFdBFf2a14a7c8E15944D1F4A48F9F95F663A4", 6, "scroll", stable=True)

eth_arb = EVMNativeToken("arbitrum")
usdt_arb = EVMToken("USDT", "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9", 6, "arbitrum", stable=True)
usdc_arb = EVMToken("USDC", "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8", 6, "arbitrum", stable=True)

usdc_opt = EVMToken("USDC", "0x7F5c764cBc14f9669B88837ca1490cCa17c31607", 6, "optimism", stable=True)

eth_eth = EVMNativeToken("ethereum")
usdt_eth = EVMToken("USDT", "0xdAC17F958D2ee523a2206206994597C13D831ec7", 6, "ethereum", stable=True)
usdc_eth = EVMToken("USDC", "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", 6, "ethereum", stable=True)

bsc_usdt = EVMToken("USDT", "0x55d398326f99059fF775485246999027B3197955", 18, "bsc", stable=True)

avax_usdt = EVMToken("USDT", "0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7", 6, "avalanche", stable=True)
avax_usdc = EVMToken("USDC", "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E", 6, "avalanche", stable=True)

polygon_usdt = EVMToken("USDT", "0xc2132D05D31c914a87C6611C10748AEb04B58e8F", 6, "polygon", stable=True)
polygon_usdc = EVMToken("USDC", "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174", 6, "polygon", stable=True)

eth_zk = EVMNativeToken("zksync")

tokens = [
    eth,
    dai,
    usdt,
    usdc
]

tokens_dict = {
    "ETH": eth,
    "DAI": dai,
    "USDT": usdt,
    "USDC": usdc
}

chains_tokens = {
    "ethereum": [usdt_eth, usdc_eth],
    "optimism": [usdc_opt],
    "arbitrum": [usdt_arb, usdc_arb],
    "bsc": [bsc_usdt],
    "avalanche": [avax_usdc, avax_usdt],
    "polygon": [polygon_usdc, polygon_usdt],
    "scroll": [usdt, usdc]
}

chain_natives = {
    "scroll": eth,
    "arbitrum": eth_arb,
    "ethereum": eth_eth,
    "zksync": eth_zk
}