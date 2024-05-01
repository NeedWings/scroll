from modules.utils.token import Token, NativeToken



eth = NativeToken("scroll")
usdt = Token("USDT", "0xf55BEC9cafDbE8730f096Aa55dad6D22d44099Df", 6, "scroll", stable=True)
dai = Token("DAI", "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb", 18, "scroll", stable=True)
usdc = Token("USDC", "0x06eFdBFf2a14a7c8E15944D1F4A48F9F95F663A4", 6, "scroll", stable=True)

eth_ethereum = NativeToken("ethereum")
weth_bsc = Token("ETH", "0x2170Ed0880ac9A755fd29B2688956BD959F933F8", 18, "bsc")
weth_polygon = Token("ETH", "0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619", 18, "polygon")
eth_optimism = NativeToken("optimism")
eth_arbitrum = NativeToken("arbitrum")
eth_zksync = NativeToken("zksync")

usdt_arbitrum = Token("USDT", "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9", 6, "arbitrum", stable=True)
usdc_arbitrum = Token("USDC", "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8", 6, "arbitrum", stable=True)


usdt_polygon = Token("USDT", "0xc2132D05D31c914a87C6611C10748AEb04B58e8F", 6, "polygon", stable=True)
usdc_polygon = Token("USDC", "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174", 6, "polygon", stable=True)

usdt_bsc = Token("USDT", "0x55d398326f99059fF775485246999027B3197955", 18, "bsc", stable=True)

eth_linea = NativeToken("linea")
eth_base = NativeToken("base")

nets_stables = {
    "arbitrum": [usdt_arbitrum, usdc_arbitrum],
    "polygon": [usdt_polygon, usdc_polygon],
    "bsc": [usdt_bsc]
}

nets_weth = {
    "bsc": weth_bsc,
    "polygon": weth_polygon
}

nets_eth = {
    "arbitrum": eth_arbitrum,
    "optimism": eth_optimism,
    "zksync": eth_zksync,
    "ethereum": eth_ethereum,
    "linea": eth_linea,
    "scroll": eth,
    "base": eth_base
}

tokens = [eth, usdc, usdt, dai]

tokens_dict = {
    "ETH": eth,
    "USDC": usdc,
    "USDT": usdt,
    "DAI": dai
}