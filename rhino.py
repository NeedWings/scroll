from BaseClasses import *
from fast_pedersen_hash import *
from Crypto.Hash import keccak

class Rhino:
    key_pair: tuple = None
    def __init__(self, account: Account) -> None:
        private_key = random.randint(0, 2**31-1)
        public_key = private_to_stark_key(private_key)
        self.key_pair = (private_key, public_key)
        self.account = account
    
    def get_transfer_message_hash(
            self,
            amount,
            nonce,
            senderVaultId,
            token,
            receiverVaultId,
            receiverPublicKey,
            expirationTimestamp,
            condition = None):
        return hashMsg(
            1,
            senderVaultId,
            receiverVaultId,
            amount,
            0,
            nonce,
            expirationTimestamp,
            token,
            receiverPublicKey,
            condition
        )

    def get_message(self, tx):
        condition = None
        return self.get_transfer_message_hash(
            tx["amount"],
            tx["nonce"],
            tx["senderVaultId"],
            tx["token"],
            tx["receiverVaultId"],
            tx["receiverPublicKey"],
            tx["expirationTimestamp"],
            condition,
        )

    def sign_tx(self, tx):

        msg = self.get_message(tx)

        signtature = sign(msg, self.key_pair[0])

        return {"r": hex(signtature[0]), "s": hex(signtature[1])}

    def createSignedTransfer(self, tx):

        tx["nonce"] = random.randint(1, 2**31-1)
        tx["expirationTimestamp"] = 476148

        signature = self.sign_tx(tx)
        tx["signature"] = signature
        return tx
    
    def createTransferPayload(
            self,
            recipientPublicKey,
            recipientVaultId,
            tokenInfo,
            quantisedAmount):
        starkPublicKey = self.key_pair[1]
        txParams = {
            "amount": quantisedAmount,
            "senderPublicKey": hex(starkPublicKey),
            "receiverPublicKey": recipientPublicKey,
            "receiverVaultId": recipientVaultId,
            "senderVaultId": tokenInfo["starkVaultId"],
            "token": tokenInfo["starkTokenId"],
            "type": "TransferRequest"
        }

        return self.createSignedTransfer(txParams)
    
    def register(self, authNonce, signature):
        dtk = hex(random.randint(0, 2**32-1))
        enable_msg = {"types":{"EIP712Domain":[{"name":"name","type":"string"},{"name":"version","type":"string"}],"rhino.fi":[{"type":"string","name":"action"},{"type":"string","name":"onlySignOn"}]},"domain":{"name":"rhino.fi","version":"1.0.0"},"primaryType":"rhino.fi","message":{"action":"Access your rhino.fi account","onlySignOn":"app.rhino.fi"}}
        encoded_enable_msg = encode_structured_data(enable_msg)
        w3 = Web3(Web3.HTTPProvider(RPC_LSIT["scroll"]))
        signed_enable = w3.eth.account.sign_message(encoded_enable_msg, private_key = self.account.private_key)
        data = hex(signed_enable.r) + hex(signed_enable.s)[2::] + hex(signed_enable.v)[2::]
        k = keccak.new(digest_bits=256)
        k.update(bytes.fromhex(data[2::]))
        encryptionKey = k.hexdigest()
        
        pk = keys.PrivateKey((bytes.fromhex(dtk[2::])))
        public_key = pk.public_key.to_hex()
        


        r = requests.post("https://api.rhino.fi/v1/trading/w/register", json={
            "starkKey":hex(self.key_pair[1]),
            "encryptedTradingKey":
                {
                    "dtk":"b1a61b91c798b0edcb23fe759c6add2003ae88aff25ca80fafe782b4138a4ebae49ce7cb10d00bfa1420286867dcb2a2f18d7e46e8afd96cc139bfca8e7c258f8fa93562cc5d3ed0afa06d1804ef65c97ff8a1dce9e9940767579272f80713f7110b8d5f0c42ab478651c978730f82335b33b3d6f32502e9cdf6cfdfb98f39a7117eef1bc41b9de47d02b264b253b457961f383c165634615ac70bc44e000b82da",
                    "dtkVersion":"v3"
                },
                "nonce":authNonce,
                "signature":signature,
                "meta":{
                     "walletType":"metamask",
                     "campaign":None,
                     "referer":None,
                     "platform":"DESKTOP"
                     }
                }
            )
        print(r.json())

    def createBridgedWithdrawalPayload(self, data, authNonce, signature):
        self.register(authNonce, signature)
        auth = json.dumps({"signature": signature, "nonce": authNonce}).replace(" ", "")
        auth = "EcRecover " + base64.b64encode(auth.encode()).decode()
        print(auth)
        token, chain, amount, nonce = data["token"], data["chain"], data["amount"], data["nonce"]
        url = "https://api.rhino.fi/v1/trading/r/vaultIdAndStarkKey?token=ETH&targetEthAddress=0xaf8ae6955d07776ab690e565ba6fbc79b8de3a5d"
        r = requests.get(url, headers={
            "authorization": auth
        })
        print(r.text)
        vaultId = r.json()["vaultId"]
        starkKey = r.json()["starkKey"]

        tx = self.createTransferPayload(
            starkKey,
            vaultId,
            {
                "starkVaultId": 1588952043,
                "starkTokenId": "0xb333e3142fe16b78628f19bb15afddaef437e72d6d7f5c6c20c6801a27fba6"
            },
            int(amount*10000000000)
        )
        return {
            "chain": "SCROLL",
            "token": "ETH",
            "amount": int(amount*10000000000),
            "nonce": random.randint(0, 9007199254740991),
            "tx": tx
        }
    
    def bridge_to_scroll(self, amount):
        auth_msg = "0x546f2070726f7465637420796f7572207268696e6f2e666920707269766163792077652061736b20796f7520746f207369676e20696e207769746820796f75722077616c6c657420746f2073656520796f757220646174612e0a5369676e696e6720696e206f6e2053756e2c203239204f637420323032332030383a35393a323220474d542e20466f7220796f7572207361666574792c206f6e6c79207369676e2074686973206d657373616765206f6e207268696e6f2e666921"
        encoded_auth_msg = encode_defunct(hexstr=auth_msg)
        w3 = Web3(Web3.HTTPProvider(RPC_LSIT["scroll"]))
        signed_auth = w3.eth.account.sign_message(encoded_auth_msg, private_key = self.account.private_key)
        authNonce = "v3-1698559162.507"
        signature = hex(signed_auth.r) + hex(signed_auth.s)[2::] + hex(signed_auth.v)[2::]

        data = self.createBridgedWithdrawalPayload({"token": "ETH", "chain": "SCROLL", "amount": amount, "nonce": None}, authNonce, signature)
        auth = json.dumps({"nonce": authNonce, "signature": signature, "address": self.account.address})

        print(data)

