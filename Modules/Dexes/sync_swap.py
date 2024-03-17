import time

import eth_abi
from eth_account.messages import encode_structured_data

from modules.base_classes.base_account import BaseAccount
from modules.base_classes.base_defi import BaseDex
from modules.utils.token import Token   
from modules.utils.txn_data_handler import TxnDataHandler
from modules.utils.Logger import logger
from modules.utils.utils import sleeping_sync
from modules.utils.token_stor import eth, usdc, usdt
from modules.config import get_slippage, ABI

INF_VALUE = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
class SyncSwap(BaseDex):
    contract_address = "0x80e38291e06339d10AAB483C65695D004dBD5C69"
    ABI = [
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "_vault",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "_wETH",
        "type": "address"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "constructor"
  },
  {
    "inputs": [],
    "name": "ApproveFailed",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "Expired",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "NotEnoughLiquidityMinted",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "TooLittleReceived",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "TransferFromFailed",
    "type": "error"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "pool",
        "type": "address"
      },
      {
        "components": [
          {
            "internalType": "address",
            "name": "token",
            "type": "address"
          },
          {
            "internalType": "uint256",
            "name": "amount",
            "type": "uint256"
          }
        ],
        "internalType": "struct SyncSwapRouter.TokenInput[]",
        "name": "inputs",
        "type": "tuple[]"
      },
      {
        "internalType": "bytes",
        "name": "data",
        "type": "bytes"
      },
      {
        "internalType": "uint256",
        "name": "minLiquidity",
        "type": "uint256"
      },
      {
        "internalType": "address",
        "name": "callback",
        "type": "address"
      },
      {
        "internalType": "bytes",
        "name": "callbackData",
        "type": "bytes"
      }
    ],
    "name": "addLiquidity",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "liquidity",
        "type": "uint256"
      }
    ],
    "stateMutability": "payable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "pool",
        "type": "address"
      },
      {
        "components": [
          {
            "internalType": "address",
            "name": "token",
            "type": "address"
          },
          {
            "internalType": "uint256",
            "name": "amount",
            "type": "uint256"
          }
        ],
        "internalType": "struct SyncSwapRouter.TokenInput[]",
        "name": "inputs",
        "type": "tuple[]"
      },
      {
        "internalType": "bytes",
        "name": "data",
        "type": "bytes"
      },
      {
        "internalType": "uint256",
        "name": "minLiquidity",
        "type": "uint256"
      },
      {
        "internalType": "address",
        "name": "callback",
        "type": "address"
      },
      {
        "internalType": "bytes",
        "name": "callbackData",
        "type": "bytes"
      }
    ],
    "name": "addLiquidity2",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "liquidity",
        "type": "uint256"
      }
    ],
    "stateMutability": "payable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "pool",
        "type": "address"
      },
      {
        "components": [
          {
            "internalType": "address",
            "name": "token",
            "type": "address"
          },
          {
            "internalType": "uint256",
            "name": "amount",
            "type": "uint256"
          }
        ],
        "internalType": "struct SyncSwapRouter.TokenInput[]",
        "name": "inputs",
        "type": "tuple[]"
      },
      {
        "internalType": "bytes",
        "name": "data",
        "type": "bytes"
      },
      {
        "internalType": "uint256",
        "name": "minLiquidity",
        "type": "uint256"
      },
      {
        "internalType": "address",
        "name": "callback",
        "type": "address"
      },
      {
        "internalType": "bytes",
        "name": "callbackData",
        "type": "bytes"
      },
      {
        "components": [
          {
            "internalType": "address",
            "name": "token",
            "type": "address"
          },
          {
            "internalType": "uint256",
            "name": "approveAmount",
            "type": "uint256"
          },
          {
            "internalType": "uint256",
            "name": "deadline",
            "type": "uint256"
          },
          {
            "internalType": "uint8",
            "name": "v",
            "type": "uint8"
          },
          {
            "internalType": "bytes32",
            "name": "r",
            "type": "bytes32"
          },
          {
            "internalType": "bytes32",
            "name": "s",
            "type": "bytes32"
          }
        ],
        "internalType": "struct IRouter.SplitPermitParams[]",
        "name": "permits",
        "type": "tuple[]"
      }
    ],
    "name": "addLiquidityWithPermit",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "liquidity",
        "type": "uint256"
      }
    ],
    "stateMutability": "payable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "pool",
        "type": "address"
      },
      {
        "components": [
          {
            "internalType": "address",
            "name": "token",
            "type": "address"
          },
          {
            "internalType": "uint256",
            "name": "amount",
            "type": "uint256"
          }
        ],
        "internalType": "struct SyncSwapRouter.TokenInput[]",
        "name": "inputs",
        "type": "tuple[]"
      },
      {
        "internalType": "bytes",
        "name": "data",
        "type": "bytes"
      },
      {
        "internalType": "uint256",
        "name": "minLiquidity",
        "type": "uint256"
      },
      {
        "internalType": "address",
        "name": "callback",
        "type": "address"
      },
      {
        "internalType": "bytes",
        "name": "callbackData",
        "type": "bytes"
      },
      {
        "components": [
          {
            "internalType": "address",
            "name": "token",
            "type": "address"
          },
          {
            "internalType": "uint256",
            "name": "approveAmount",
            "type": "uint256"
          },
          {
            "internalType": "uint256",
            "name": "deadline",
            "type": "uint256"
          },
          {
            "internalType": "uint8",
            "name": "v",
            "type": "uint8"
          },
          {
            "internalType": "bytes32",
            "name": "r",
            "type": "bytes32"
          },
          {
            "internalType": "bytes32",
            "name": "s",
            "type": "bytes32"
          }
        ],
        "internalType": "struct IRouter.SplitPermitParams[]",
        "name": "permits",
        "type": "tuple[]"
      }
    ],
    "name": "addLiquidityWithPermit2",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "liquidity",
        "type": "uint256"
      }
    ],
    "stateMutability": "payable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "pool",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "liquidity",
        "type": "uint256"
      },
      {
        "internalType": "bytes",
        "name": "data",
        "type": "bytes"
      },
      {
        "internalType": "uint256[]",
        "name": "minAmounts",
        "type": "uint256[]"
      },
      {
        "internalType": "address",
        "name": "callback",
        "type": "address"
      },
      {
        "internalType": "bytes",
        "name": "callbackData",
        "type": "bytes"
      }
    ],
    "name": "burnLiquidity",
    "outputs": [
      {
        "components": [
          {
            "internalType": "address",
            "name": "token",
            "type": "address"
          },
          {
            "internalType": "uint256",
            "name": "amount",
            "type": "uint256"
          }
        ],
        "internalType": "struct IPool.TokenAmount[]",
        "name": "amounts",
        "type": "tuple[]"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "pool",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "liquidity",
        "type": "uint256"
      },
      {
        "internalType": "bytes",
        "name": "data",
        "type": "bytes"
      },
      {
        "internalType": "uint256",
        "name": "minAmount",
        "type": "uint256"
      },
      {
        "internalType": "address",
        "name": "callback",
        "type": "address"
      },
      {
        "internalType": "bytes",
        "name": "callbackData",
        "type": "bytes"
      }
    ],
    "name": "burnLiquiditySingle",
    "outputs": [
      {
        "components": [
          {
            "internalType": "address",
            "name": "token",
            "type": "address"
          },
          {
            "internalType": "uint256",
            "name": "amount",
            "type": "uint256"
          }
        ],
        "internalType": "struct IPool.TokenAmount",
        "name": "amountOut",
        "type": "tuple"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "pool",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "liquidity",
        "type": "uint256"
      },
      {
        "internalType": "bytes",
        "name": "data",
        "type": "bytes"
      },
      {
        "internalType": "uint256",
        "name": "minAmount",
        "type": "uint256"
      },
      {
        "internalType": "address",
        "name": "callback",
        "type": "address"
      },
      {
        "internalType": "bytes",
        "name": "callbackData",
        "type": "bytes"
      },
      {
        "components": [
          {
            "internalType": "uint256",
            "name": "approveAmount",
            "type": "uint256"
          },
          {
            "internalType": "uint256",
            "name": "deadline",
            "type": "uint256"
          },
          {
            "internalType": "bytes",
            "name": "signature",
            "type": "bytes"
          }
        ],
        "internalType": "struct IRouter.ArrayPermitParams",
        "name": "permit",
        "type": "tuple"
      }
    ],
    "name": "burnLiquiditySingleWithPermit",
    "outputs": [
      {
        "components": [
          {
            "internalType": "address",
            "name": "token",
            "type": "address"
          },
          {
            "internalType": "uint256",
            "name": "amount",
            "type": "uint256"
          }
        ],
        "internalType": "struct IPool.TokenAmount",
        "name": "amountOut",
        "type": "tuple"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "pool",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "liquidity",
        "type": "uint256"
      },
      {
        "internalType": "bytes",
        "name": "data",
        "type": "bytes"
      },
      {
        "internalType": "uint256[]",
        "name": "minAmounts",
        "type": "uint256[]"
      },
      {
        "internalType": "address",
        "name": "callback",
        "type": "address"
      },
      {
        "internalType": "bytes",
        "name": "callbackData",
        "type": "bytes"
      },
      {
        "components": [
          {
            "internalType": "uint256",
            "name": "approveAmount",
            "type": "uint256"
          },
          {
            "internalType": "uint256",
            "name": "deadline",
            "type": "uint256"
          },
          {
            "internalType": "bytes",
            "name": "signature",
            "type": "bytes"
          }
        ],
        "internalType": "struct IRouter.ArrayPermitParams",
        "name": "permit",
        "type": "tuple"
      }
    ],
    "name": "burnLiquidityWithPermit",
    "outputs": [
      {
        "components": [
          {
            "internalType": "address",
            "name": "token",
            "type": "address"
          },
          {
            "internalType": "uint256",
            "name": "amount",
            "type": "uint256"
          }
        ],
        "internalType": "struct IPool.TokenAmount[]",
        "name": "amounts",
        "type": "tuple[]"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "_factory",
        "type": "address"
      },
      {
        "internalType": "bytes",
        "name": "data",
        "type": "bytes"
      }
    ],
    "name": "createPool",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "payable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "name": "enteredPools",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "account",
        "type": "address"
      }
    ],
    "name": "enteredPoolsLength",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "name": "isPoolEntered",
    "outputs": [
      {
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "bytes[]",
        "name": "data",
        "type": "bytes[]"
      }
    ],
    "name": "multicall",
    "outputs": [
      {
        "internalType": "bytes[]",
        "name": "results",
        "type": "bytes[]"
      }
    ],
    "stateMutability": "payable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "token",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "value",
        "type": "uint256"
      },
      {
        "internalType": "uint256",
        "name": "deadline",
        "type": "uint256"
      },
      {
        "internalType": "uint8",
        "name": "v",
        "type": "uint8"
      },
      {
        "internalType": "bytes32",
        "name": "r",
        "type": "bytes32"
      },
      {
        "internalType": "bytes32",
        "name": "s",
        "type": "bytes32"
      }
    ],
    "name": "selfPermit",
    "outputs": [],
    "stateMutability": "payable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "token",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "value",
        "type": "uint256"
      },
      {
        "internalType": "uint256",
        "name": "deadline",
        "type": "uint256"
      },
      {
        "internalType": "bytes",
        "name": "signature",
        "type": "bytes"
      }
    ],
    "name": "selfPermit2",
    "outputs": [],
    "stateMutability": "payable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "token",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "value",
        "type": "uint256"
      },
      {
        "internalType": "uint256",
        "name": "deadline",
        "type": "uint256"
      },
      {
        "internalType": "bytes",
        "name": "signature",
        "type": "bytes"
      }
    ],
    "name": "selfPermit2IfNecessary",
    "outputs": [],
    "stateMutability": "payable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "token",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "nonce",
        "type": "uint256"
      },
      {
        "internalType": "uint256",
        "name": "expiry",
        "type": "uint256"
      },
      {
        "internalType": "uint8",
        "name": "v",
        "type": "uint8"
      },
      {
        "internalType": "bytes32",
        "name": "r",
        "type": "bytes32"
      },
      {
        "internalType": "bytes32",
        "name": "s",
        "type": "bytes32"
      }
    ],
    "name": "selfPermitAllowed",
    "outputs": [],
    "stateMutability": "payable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "token",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "nonce",
        "type": "uint256"
      },
      {
        "internalType": "uint256",
        "name": "expiry",
        "type": "uint256"
      },
      {
        "internalType": "uint8",
        "name": "v",
        "type": "uint8"
      },
      {
        "internalType": "bytes32",
        "name": "r",
        "type": "bytes32"
      },
      {
        "internalType": "bytes32",
        "name": "s",
        "type": "bytes32"
      }
    ],
    "name": "selfPermitAllowedIfNecessary",
    "outputs": [],
    "stateMutability": "payable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "token",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "value",
        "type": "uint256"
      },
      {
        "internalType": "uint256",
        "name": "deadline",
        "type": "uint256"
      },
      {
        "internalType": "uint8",
        "name": "v",
        "type": "uint8"
      },
      {
        "internalType": "bytes32",
        "name": "r",
        "type": "bytes32"
      },
      {
        "internalType": "bytes32",
        "name": "s",
        "type": "bytes32"
      }
    ],
    "name": "selfPermitIfNecessary",
    "outputs": [],
    "stateMutability": "payable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "stakingPool",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "token",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      },
      {
        "internalType": "address",
        "name": "onBehalf",
        "type": "address"
      }
    ],
    "name": "stake",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "components": [
          {
            "components": [
              {
                "internalType": "address",
                "name": "pool",
                "type": "address"
              },
              {
                "internalType": "bytes",
                "name": "data",
                "type": "bytes"
              },
              {
                "internalType": "address",
                "name": "callback",
                "type": "address"
              },
              {
                "internalType": "bytes",
                "name": "callbackData",
                "type": "bytes"
              }
            ],
            "internalType": "struct IRouter.SwapStep[]",
            "name": "steps",
            "type": "tuple[]"
          },
          {
            "internalType": "address",
            "name": "tokenIn",
            "type": "address"
          },
          {
            "internalType": "uint256",
            "name": "amountIn",
            "type": "uint256"
          }
        ],
        "internalType": "struct IRouter.SwapPath[]",
        "name": "paths",
        "type": "tuple[]"
      },
      {
        "internalType": "uint256",
        "name": "amountOutMin",
        "type": "uint256"
      },
      {
        "internalType": "uint256",
        "name": "deadline",
        "type": "uint256"
      }
    ],
    "name": "swap",
    "outputs": [
      {
        "components": [
          {
            "internalType": "address",
            "name": "token",
            "type": "address"
          },
          {
            "internalType": "uint256",
            "name": "amount",
            "type": "uint256"
          }
        ],
        "internalType": "struct IPool.TokenAmount",
        "name": "amountOut",
        "type": "tuple"
      }
    ],
    "stateMutability": "payable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "components": [
          {
            "components": [
              {
                "internalType": "address",
                "name": "pool",
                "type": "address"
              },
              {
                "internalType": "bytes",
                "name": "data",
                "type": "bytes"
              },
              {
                "internalType": "address",
                "name": "callback",
                "type": "address"
              },
              {
                "internalType": "bytes",
                "name": "callbackData",
                "type": "bytes"
              }
            ],
            "internalType": "struct IRouter.SwapStep[]",
            "name": "steps",
            "type": "tuple[]"
          },
          {
            "internalType": "address",
            "name": "tokenIn",
            "type": "address"
          },
          {
            "internalType": "uint256",
            "name": "amountIn",
            "type": "uint256"
          }
        ],
        "internalType": "struct IRouter.SwapPath[]",
        "name": "paths",
        "type": "tuple[]"
      },
      {
        "internalType": "uint256",
        "name": "amountOutMin",
        "type": "uint256"
      },
      {
        "internalType": "uint256",
        "name": "deadline",
        "type": "uint256"
      },
      {
        "components": [
          {
            "internalType": "address",
            "name": "token",
            "type": "address"
          },
          {
            "internalType": "uint256",
            "name": "approveAmount",
            "type": "uint256"
          },
          {
            "internalType": "uint256",
            "name": "deadline",
            "type": "uint256"
          },
          {
            "internalType": "uint8",
            "name": "v",
            "type": "uint8"
          },
          {
            "internalType": "bytes32",
            "name": "r",
            "type": "bytes32"
          },
          {
            "internalType": "bytes32",
            "name": "s",
            "type": "bytes32"
          }
        ],
        "internalType": "struct IRouter.SplitPermitParams",
        "name": "permit",
        "type": "tuple"
      }
    ],
    "name": "swapWithPermit",
    "outputs": [
      {
        "components": [
          {
            "internalType": "address",
            "name": "token",
            "type": "address"
          },
          {
            "internalType": "uint256",
            "name": "amount",
            "type": "uint256"
          }
        ],
        "internalType": "struct IPool.TokenAmount",
        "name": "amountOut",
        "type": "tuple"
      }
    ],
    "stateMutability": "payable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "vault",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "wETH",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  }
]
    name = "SyncSwap"
    supported_tokens = ["ETH", "USDT", "USDC"]

    lpts = [
        Token("ETH:USDT", "0x78ea8E533c834049dE625e05F0B4DeFfe9DB5f6e", 18, "scroll"),
        Token("ETH:USDC", "0x814A23B053FD0f102AEEda0459215C2444799C70", 18, "scroll"),
        Token("USDT:USDC", "0x2076d4632853FB165Cf7c7e7faD592DaC70f4fe1", 18, "scroll"),
   ]
    name_from_contract = {
        "0xf55BEC9cafDbE8730f096Aa55dad6D22d44099Df": "Tether USD",
        "0x06eFdBFf2a14a7c8E15944D1F4A48F9F95F663A4": "USD Coin"
	}
    version_from_contract = {
        "0xf55BEC9cafDbE8730f096Aa55dad6D22d44099Df": "1",
        "0x06eFdBFf2a14a7c8E15944D1F4A48F9F95F663A4": "2"
	}
    lpt_from_tokens = {
        "ETH:USDT":lpts[0],
        "USDT:ETH":lpts[0],
        "USDC:ETH":lpts[1],
        "ETH:USDC":lpts[1],
        "USDC:USDT":lpts[2],
        "USDT:USDC":lpts[2],
    }

    tokens_from_lpt = {
        "0x78ea8E533c834049dE625e05F0B4DeFfe9DB5f6e": [eth, usdt],
        "0x814A23B053FD0f102AEEda0459215C2444799C70": [usdc, eth],
        "0x2076d4632853FB165Cf7c7e7faD592DaC70f4fe1": [usdc, usdt]
    }

    def _get_nonce_of_liq_token(self, address: str, lpt: Token, w3):
        contract = w3.eth.contract(lpt.contract_address, abi=ABI)
        while True:
            try:
                nonce = contract.functions.nonces(address).call()
                return nonce
            except Exception as e:
                logger.error(f"[{address}] got error while trying to get nonce of lpt: {e}")
                sleeping_sync(address, True)

    def create_txn_for_swap(self, amount_in: float, token1: Token, amount_out: float, token2: Token, sender: BaseAccount, full: bool = False, native_first: bool = False):
        w3 = sender.get_w3('scroll')
        contract = w3.eth.contract(self.contract_address, abi=self.ABI)
        stable = token1.stable and token2.stable
        if token1.symbol == "ETH":
            native_first = True
        txn_data_handler = TxnDataHandler(sender, "scroll", w3=w3)
        swap_data = eth_abi.encode(['address', 'address', 'uint8'], [token1.contract_address, sender.get_address(), 1])
        deadline = int(time.time()+3600*5)
        if native_first:
            approve_txn = token1.get_approve_txn(sender, self.contract_address, int(amount_in*10**token1.decimals), w3=w3)
            value = int(amount_in*10**token1.decimals)
            function = contract.functions.swap
            steps = [{
                "pool": self.lpt_from_tokens[f"{token1.symbol}:{token2.symbol}"].contract_address,
                "data": swap_data,
                "callback": "0x0000000000000000000000000000000000000000",
                "callbackData": "0x"
			}]
            paths =[
                {
                    "steps": steps,
                    "tokenIn": "0x0000000000000000000000000000000000000000",
                    "amountIn": value
				}
			]
            txn = function(
                paths,
                int(get_slippage()*amount_out*10**token2.decimals),
                deadline
            ).build_transaction(txn_data_handler.get_txn_data(value))
        else:
            approve_txn = None
            token_nonce = self._get_nonce_of_liq_token(sender.get_address(), token1, w3=w3)
            if token_nonce == 0:
                msg = {
                'types': {
                    'EIP712Domain': [
                    { 'name': 'name', 'type': 'string' },
                    { 'name': 'version', 'type': 'string' },
                    { 'name': 'chainId', 'type': 'uint256' },
                    { 'name': 'verifyingContract', 'type': 'address' },
                    ],
                    'Permit': [
                    { 'name': 'owner', 'type': 'address' },
                    { 'name': 'spender', 'type': 'address' },
                    { 'name': 'value', 'type': 'uint256' },
                    { 'name': 'nonce', 'type': 'uint256' },
                    { 'name': 'deadline', 'type': 'uint256' },
                    ]
                },
                'domain': {
                    'name': self.name_from_contract[token1.contract_address],
                    'version': self.version_from_contract[token1.contract_address],
                    'chainId': 534352,
                    'verifyingContract': token1.contract_address,
                },
                'primaryType': 'Permit',
                'message': {
                    'owner': sender.get_address(),
                    'spender': self.contract_address,
                    'value': INF_VALUE,
                    'nonce': 0,
                    'deadline': deadline
                	},
                }
                
                encoded_msg = encode_structured_data(msg)
                
                signed_msg = w3.eth.account.sign_message(encoded_msg, sender.private_key)
              

                r = signed_msg.r.to_bytes(32, "big")
                s = signed_msg.s.to_bytes(32, "big")
                v = signed_msg.v


                value = 0
                function = contract.functions.swapWithPermit
                steps = [{
					"pool": self.lpt_from_tokens[f"{token1.symbol}:{token2.symbol}"].contract_address,
					"data": swap_data,
					"callback": "0x0000000000000000000000000000000000000000",
					"callbackData": "0x"
				}]
                paths =[
					{
						"steps": steps,
						"tokenIn": token1.contract_address,
						"amountIn": int(amount_in*10**token1.decimals)
					}
				]
                txn = function(
                    paths,
					int(get_slippage()*amount_out*10**token2.decimals),
					deadline,
                    (
						token1.contract_address,
						INF_VALUE,
						deadline,
						v,
						r,
						s
					)
				).build_transaction(txn_data_handler.get_txn_data())
            else:
                steps = [{
                    "pool": self.lpt_from_tokens[f"{token1.symbol}:{token2.symbol}"].contract_address,
                    "data": swap_data,
                    "callback": "0x0000000000000000000000000000000000000000",
                    "callbackData": "0x"
                  }]
                paths =[
                        {
                          "steps": steps,
                          "tokenIn": token1.contract_address,
                          "amountIn": int(amount_in*10**token1.decimals)
                        }
                      ]
                function = contract.functions.swap
                txn = function(
					paths,
					int(get_slippage()*amount_out*10**token2.decimals),
					deadline
				).build_transaction(txn_data_handler.get_txn_data())
        return txn


    def get_pool_rate(self, token1: Token, token2: Token, sender: BaseAccount):
        lpt = self.lpt_from_tokens[f"{token1.symbol}:{token2.symbol}"]
        token1_val = token1.balance_of(lpt.contract_address, w3=sender.get_w3('scroll'), of_wrapped=True)[1]
        token2_val = token2.balance_of(lpt.contract_address, w3=sender.get_w3('scroll'), of_wrapped=True)[1]

        token1_usd_val = token1.get_usd_value(token1_val)
        token2_usd_val = token2.get_usd_value(token2_val)

        return token1_usd_val/token2_usd_val

    def create_txn_for_liq(self, amount1: float, token1: Token, amount2: float, token2: Token, sender: BaseAccount):
        return None

    
    def create_txn_for_remove_liq(self, lptoken: Token, sender: BaseAccount):
        return None
        