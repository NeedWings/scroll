from BaseClasses import *
from fast_pedersen_hash import *
from Crypto.Hash import keccak as kkeccak
import ecdsa
from ecdsa.ellipticcurve import Point
from ecdsa.ecdsa import Public_key, Private_key, curve_secp256k1
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import hmac
from eth_keys.backends.native.ecdsa import compress_public_key, decompress_public_key
from eth_utils.curried import keccak
from datetime import datetime
import pytz
import chardet

class Rhino:
    contract_address = "0x10417734001162Ea139e8b044DFe28DbB8B28ad0"
    ABI = [{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"user","type":"address"},{"indexed":true,"internalType":"address","name":"token","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"BridgedDeposit","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"user","type":"address"},{"indexed":true,"internalType":"address","name":"token","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":false,"internalType":"string","name":"withdrawalId","type":"string"}],"name":"BridgedWithdrawal","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint8","name":"version","type":"uint8"}],"name":"Initialized","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"addFunds","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"addFundsNative","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"bool","name":"value","type":"bool"}],"name":"allowDeposits","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"user","type":"address"},{"internalType":"bool","name":"value","type":"bool"}],"name":"authorize","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"authorized","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"deposit","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"depositNative","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"depositsDisallowed","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"initialize","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string","name":"","type":"string"}],"name":"processedWithdrawalIds","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"removeFunds","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address payable","name":"to","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"removeFundsNative","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwner","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"string","name":"withdrawalId","type":"string"}],"name":"withdraw","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address payable","name":"to","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"string","name":"withdrawalId","type":"string"}],"name":"withdrawNative","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address payable","name":"to","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"withdrawNativeV2","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"withdrawV2","outputs":[],"stateMutability":"nonpayable","type":"function"},{"stateMutability":"payable","type":"receive"}]
    def net_name_to_net(self, net_name):
        nets = {
            "arbitrum": "ARBITRUM"
        }
        return nets[net_name]

    dtk = None

    key_pair: tuple = None
    def __init__(self, account: Account) -> None:
       
        self.account = account
    
    def set_key_pair(self, dtk: str):
        private_key = int(dtk, 16)%EC_ORDER
        public_key = private_to_stark_key(private_key)
        self.key_pair = (private_key, public_key)
        self.dtk = dtk

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

    def deposit(self, amount):
        txn_data_handler = EVMTransactionDataHandler(self.account, "arbitrum")
 
        w3: Web3 = Web3(Web3.HTTPProvider(random.choice(RPC_LSIT["arbitrum"])))

        contract = w3.eth.contract(self.contract_address, abi=self.ABI)

        txn = contract.functions.depositNative().build_transaction(txn_data_handler.get_txn_data(int(amount*1e18)))

        return self.account.send_without_wait([txn], "arbitrum")

        

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

        signtature = sign(int(msg, 16), self.key_pair[0])
        return {"r": hex(signtature[0]), "s": hex(signtature[1])}

    def createSignedTransfer(self, tx):

        tx["nonce"] = random.randint(0, 2**31-1)
        tx["expirationTimestamp"] = 476148

        signature = self.sign_tx(tx)
        tx["signature"] = signature
        tx["amount"] = str(tx["amount"])
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
            "senderPublicKey": "0x0"+hex(starkPublicKey)[2::],
            "receiverPublicKey": recipientPublicKey,
            "receiverVaultId": recipientVaultId,
            "senderVaultId": tokenInfo["starkVaultId"],
            "token": tokenInfo["starkTokenId"],
            "type": "TransferRequest"
        }

        return self.createSignedTransfer(txParams)

    def decompress(self, startsWith02Or03):
        if len(startsWith02Or03)%2 == 0:
            add = ""
        else:
            add = "0"
        testBuffer = list(bytes.fromhex(add + startsWith02Or03))
        if len(testBuffer) == 64:
            startsWith02Or03 = "04" + startsWith02Or03

        res = startsWith02Or03

        res = "0x" + res[2::]
        return res
    
    def to_array(self, num: int):
        if len(hex(num))%2 == 0:
            add = ""
        else:
            add = "0"
        byteLength = len(bytes.fromhex(add + hex(num)[2::]))

        res = [0]*byteLength

        q = num
        i = 0
        while q != 0:
            b = q & 0xff
            q = q >> 8
            res[byteLength - i - 1] = b
            i += 1
        return res


    def encrypt(self, pub_key, msg):
        ephemPrivateKey = random.randint(0, 256**32-1)
        #ephemPrivateKey = 0x1ef61986631bf16f379a2c0e691cb76e3e8baa8b575d66bc3589d448d88bfa28
        keyA =  keys.PrivateKey((bytes.fromhex("0"*(64-len(hex(ephemPrivateKey)[2::])) + hex(ephemPrivateKey)[2::]   )))
        ephemPublicKey = keyA.public_key.to_hex()
        curve = ecdsa.SECP256k1
   
        pub_x = int(pub_key[2:66], 16)
        pub_y = int(pub_key[66::], 16)

        pub_point = Point(curve_secp256k1, pub_x, pub_y, curve.order)
        Px = (pub_point * ephemPrivateKey).x()
        
        Px = self.to_array(Px)
        buff = ""
        for i in Px:
            buff += "0"*(4-len(hex(i))) + hex(i)[2::]
        Px = int(buff, 16)

        if len(hex(Px))%2 == 0:
            add = ""
        else:
            add = "0"

        hsh = hashlib.sha512(bytes.fromhex(add + hex(Px)[2::])).hexdigest()
        if len(hsh) % 2 == 0:
            hsh = hsh
        else:
            hsh = "0" + hsh
        iv = random.randint(0, 256**16-1)

        if len(hex(iv))%2 == 0:
            add = ""
        else:
            add = "0"
        encryptionKey = hsh[0:64]
        macKey = hsh[64::]
        cipher = AES.new(bytes.fromhex(encryptionKey), AES.MODE_CBC, iv=bytes.fromhex(add + hex(iv)[2::]))

        ct_bytes = cipher.encrypt(pad(msg, AES.block_size))
        dataToMac = add + hex(iv)[2::] + "04"+ephemPublicKey[2::] + ct_bytes.hex()


        mac = hmac.new(bytes.fromhex(macKey), bytes.fromhex(dataToMac), hashlib.sha256).hexdigest()

        return {
            "iv": hex(iv),
            "ephemPublicKey": "0x04"+ephemPublicKey[2::],
            "ciphertext": ct_bytes.hex(),
            "mac": "0x"+mac
        }




    def encryptWithPublicKey(self, public_key, message: str):
        public_key = "0x" + public_key[2::]

        bytes_msg = message.encode()
        data = self.encrypt(public_key, bytes_msg)

        if len(data["ephemPublicKey"][4::])%2 == 0:
            add = ""
        else:
            add = "0"
        compressedKey = compress_public_key(bytes.fromhex(add + data["ephemPublicKey"][4::])).hex()
       
        encryptedMessage = data["iv"][2::] + compressedKey + data["mac"][2::] + data["ciphertext"]
        return encryptedMessage


    def recover_trading_key(self, auth):
        r = requests.post("https://api.rhino.fi/v1/trading/r/recoverTradingKey", headers={
            "authorization": auth
        }, json={"ethAddress": self.account.address})

        encrypted_key =  r.json()["encryptedTradingKey"]

        return self.decode_trading_key(encrypted_key)

    def decode_trading_key(self, encrypted_key):
        iv = encrypted_key[0:32]
        compressedKey = encrypted_key[32:66+32]
        mac = encrypted_key[66+32:66+32+64]
        cipher_text = encrypted_key[66+32+64::]

        

        enable_msg = {"types":{"EIP712Domain":[{"name":"name","type":"string"},{"name":"version","type":"string"}],"rhino.fi":[{"type":"string","name":"action"},{"type":"string","name":"onlySignOn"}]},"domain":{"name":"rhino.fi","version":"1.0.0"},"primaryType":"rhino.fi","message":{"action":"Access your rhino.fi account","onlySignOn":"app.rhino.fi"}}
        encoded_enable_msg = encode_structured_data(enable_msg)
        w3 = Web3(Web3.HTTPProvider(RPC_LSIT["scroll"]))
        signed_enable = w3.eth.account.sign_message(encoded_enable_msg, private_key = self.account.private_key)
        r = hex(signed_enable.r)
        if len(r)%2 != 0:
            r = "0x0"+r[2::]
        s = hex(signed_enable.s)
        if len(s)%2 != 0:
            s = "0x0"+s[2::]
        v = hex(signed_enable.v)
        if len(v)%2 != 0:
            v = "0x0"+v[2::]

        data = r + s[2::] + v[2::]
        #data = "0x14f6ccb3f2ce5f67d0e85bc92c4b8bee464b39fa275e388de7e75df7e8205aab7b600ee52f56ccfba1b1b79e9ca83b15834820926c9a0519b96f8c8c8448b8b41b"
       
        k = kkeccak.new(digest_bits=256)
        k.update(data.encode())
        encryptionKey = k.hexdigest()
        pk = keys.PrivateKey((bytes.fromhex(encryptionKey)))
        public_key = pk.public_key.to_hex()
        decompressed_pub = decompress_public_key(bytes.fromhex(compressedKey)).hex()

        ephemPrivateKey = int(encryptionKey, 16)
        #ephemPrivateKey = 0x1ef61986631bf16f379a2c0e691cb76e3e8baa8b575d66bc3589d448d88bfa28
        keyA =  keys.PrivateKey((bytes.fromhex("0"*(64-len(hex(ephemPrivateKey)[2::])) + hex(ephemPrivateKey)[2::]   )))
        ephemPublicKey = keyA.public_key.to_hex()
        curve = ecdsa.SECP256k1
   
        pub_x = int(decompressed_pub[0:64], 16)
        pub_y = int(decompressed_pub[64::], 16)
      
        pub_point = Point(curve_secp256k1, pub_x, pub_y, curve.order)
        Px = (pub_point * ephemPrivateKey).x()

        Px = self.to_array(Px)
        buff = ""
        for i in Px:
            buff += "0"*(4-len(hex(i))) + hex(i)[2::]
        Px = int(buff, 16)

        if len(hex(Px))%2 == 0:
            add = ""
        else:
            add = "0"

        hsh = hashlib.sha512(bytes.fromhex(add + hex(Px)[2::])).hexdigest()
        if len(hsh) % 2 == 0:
            hsh = hsh
        else:
            hsh = "0" + hsh
       

        encryptionKey = hsh[0:64]
        cipher = AES.new(bytes.fromhex(encryptionKey), AES.MODE_CBC, iv=bytes.fromhex(iv))
        
        byte_msg = bytes.fromhex(cipher.decrypt(bytes.fromhex(cipher_text)).hex())
        msg = byte_msg.decode().replace("\x05", "") 

       
        return json.loads(msg.replace("\x05", ""))['data']



    def register(self, authNonce, signature):
        dtk = hex(random.randint(0, 256**32-1))
        #dtk = "0x6156e5c85c87d2b085f0d5a439c5cce6c5fd8933f1ad5878ef5692f8923bc478"
        enable_msg = {"types":{"EIP712Domain":[{"name":"name","type":"string"},{"name":"version","type":"string"}],"rhino.fi":[{"type":"string","name":"action"},{"type":"string","name":"onlySignOn"}]},"domain":{"name":"rhino.fi","version":"1.0.0"},"primaryType":"rhino.fi","message":{"action":"Access your rhino.fi account","onlySignOn":"app.rhino.fi"}}
        encoded_enable_msg = encode_structured_data(enable_msg)
        w3 = Web3(Web3.HTTPProvider(RPC_LSIT["scroll"]))
        signed_enable = w3.eth.account.sign_message(encoded_enable_msg, private_key = self.account.private_key)
        data = hex(signed_enable.r) + hex(signed_enable.s)[2::] + hex(signed_enable.v)[2::]
        r = hex(signed_enable.r)
        if len(r)%2 != 0:
            r = "0x0"+r[2::]
        s = hex(signed_enable.s)
        if len(s)%2 != 0:
            s = "0x0"+s[2::]
        v = hex(signed_enable.v)
        if len(v)%2 != 0:
            v = "0x0"+v[2::]
        data = r + s[2::] + v[2::]
        #data = "0x14f6ccb3f2ce5f67d0e85bc92c4b8bee464b39fa275e388de7e75df7e8205aab7b600ee52f56ccfba1b1b79e9ca83b15834820926c9a0519b96f8c8c8448b8b41b"
        k = kkeccak.new(digest_bits=256)
        k.update(data.encode())
        encryptionKey = k.hexdigest()

        pk = keys.PrivateKey((bytes.fromhex(encryptionKey)))
        public_key = pk.public_key.to_hex()
        b = "{"
        bc = "}"
        
        encryptedTradingKey = self.encryptWithPublicKey(public_key,f"{b}\"data\":\"{dtk[2::]}\"{bc}")
        
        data = {
            "private_key": dtk[2::],
            "encryptedTradingKey":{
                "dtk": encryptedTradingKey,
                "dtkVersion":"v3"
            }
        }
      
        self.set_key_pair(dtk)
        
        r = requests.post("https://api.rhino.fi/v1/trading/w/register", json={
            "encryptedTradingKey":data["encryptedTradingKey"],
            "meta":{
                 "walletType":"metamask",
                 "campaign":None,
                 "referer":None,
                 "platform":"DESKTOP"
                },
            "nonce":authNonce,
            "signature":signature,
            "starkKey":"0"+hex(self.key_pair[1])[2::]
        },
            headers={
                "Accept":"application/json",
                "Accept-Encoding":"utf-8",
                "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                "Content-Type":"application/json",
                "Origin":"https://app.rhino.fi",
                "Referer":"https://app.rhino.fi/",
                "Sec-Ch-Ua":'"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
                "Sec-Ch-Ua-Mobile":"?0",
                "Sec-Ch-Ua-Platform":'"Windows"',
                "Sec-Fetch-Dest":"empty",
                "Sec-Fetch-Mode":"cors",
                "Sec-Fetch-Site":"same-site",
                "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
            }
            )
        return r.status_code

    def get_eth_info(self, auth):
        for i in range(5):
            try:
                r = requests.post("https://api.rhino.fi/v1/trading/r/getVaultIdAndDeversifiVaultId", json={"token":"ETH"}, headers={
                    "authorization": auth

                })
            
                return r.json()["starkVaultId"]
            except Exception as e:
                logger.error(f"[{self.account.address}] got error, while trying to get eth vaultId")
                sleeping_sync(self.account.address, True)
        a = 1/0

    def generate_auth(self):
        date = datetime.now(pytz.timezone('UTC')).strftime("%a, %d %b %Y %H:%M:%S")
        ts = str(int(time.time() * 1000)/1000).replace(",",".")
        text = f"To protect your rhino.fi privacy we ask you to sign in with your wallet to see your data.\nSigning in on {date} GMT. For your safety, only sign this message on rhino.fi!"
        
        auth_msg = "0x"+ text.encode().hex()
        encoded_auth_msg = encode_defunct(hexstr=auth_msg)
        w3 = Web3(Web3.HTTPProvider(RPC_LSIT["scroll"]))
        signed_auth = w3.eth.account.sign_message(encoded_auth_msg, private_key = self.account.private_key)
        authNonce = f"v3-{ts}"
        signature = hex(signed_auth.r) + hex(signed_auth.s)[2::] + hex(signed_auth.v)[2::]
        r = hex(signed_auth.r)
        if len(r)%2 != 0:
            r = "0x0"+r[2::]
        s = hex(signed_auth.s)
        if len(s)%2 != 0:
            s = "0x0"+s[2::]
        v = hex(signed_auth.v)
        if len(v)%2 != 0:
            v = "0x0"+v[2::]
        signature = r + s[2::] + v[2::]
        return authNonce, signature

    def get_user_data(self, auth):
        for i in range(5):
            try:
                r = requests.post("https://api.rhino.fi/v1/trading/r/getUserConf", headers={
                    "authorization": auth

                })

                return r.json()
            except Exception as e:
                logger.error(f"[{self.account.address}] got error, while trying to get conf")
                sleeping_sync(self.account.address, True)
        a = 1/0

    def createBridgedWithdrawalPayload(self, data):
        authNonce, signature = self.generate_auth()
        auth = json.dumps({"signature": signature, "nonce": authNonce}).replace(" ", "")
        auth = "EcRecover " + base64.b64encode(auth.encode()).decode()
        registered = self.get_user_data(auth)["isRegistered"]
        if not registered:
            c = -1
            sc = 500
            while c != 5 and (sc == 500 or sc == 422):
                authNonce, signature = self.generate_auth()
                c+=1
                sc = self.register(authNonce, signature)
                if sc == 500 or sc == 422:
                    logger.error(f"[{self.account.address}] failed to registrer on rhino. trying again")
                    sleeping_sync(self.account.address, True)
            
            if c == 5:
                logger.info(f"[{self.account.address}] can't registrer on rhino. End.")
                return 0,0,0,0
            else:
                logger.success(f"[{self.account.address}] registered successfully")
            auth = json.dumps({"signature": signature, "nonce": authNonce}).replace(" ", "")
            auth = "EcRecover " + base64.b64encode(auth.encode()).decode()
            starkVaultId = self.get_eth_info(auth)
        else:
            logger.info(f"[{self.account.address}] recovering trading key")
            
            dtk = self.recover_trading_key(auth)
            self.set_key_pair(dtk)
            try:
                starkVaultId = self.get_user_data(auth)["tokenRegistry"]["ETH"]["starkVaultId"]
            except:
                starkVaultId = self.get_eth_info(auth)

        token, chain, amount, nonce = data["token"], data["chain"], data["amount"], data["nonce"]
        url = "https://api.rhino.fi/v1/trading/r/vaultIdAndStarkKey?token=ETH&targetEthAddress=0xaf8ae6955d07776ab690e565ba6fbc79b8de3a5d"
        c = 0
        while True:
            try:
                r = requests.get(url, headers={
                    "authorization": auth
                })
                vaultId = r.json()["vaultId"]
                starkKey = r.json()["starkKey"]
                break
            except:
                logger.error(f"[{self.account.address}] failed to get data, trying again")
            c+=1
            if c == 10:
                logger.error(f"[{self.account.address}] to many attemts. end.")
                return 0,0,0,0
        r = requests.post("https://api.rhino.fi/v1/trading/deposits-validate", json={"token":"ETH","amount":str(int(amount*100000000))}, headers ={"authorization": auth} )

        tx = self.createTransferPayload(
            starkKey,
            vaultId,
            {
                "starkVaultId": starkVaultId,
                "starkTokenId": "0xb333e3142fe16b78628f19bb15afddaef437e72d6d7f5c6c20c6801a27fba6"
            },
            int(amount*100000000)
        )

        return {
            "chain": "SCROLL",
            "token": "ETH",
            "amount": str(int(amount*100000000)),
            "nonce": random.randint(0, 9007199254740991),
            "tx": tx
        }, authNonce, signature, auth
    
    def get_bridges(self, auth):
        r = requests.get("https://api.rhino.fi/v1/trading/bridges?",
                         headers={
                              "authorization": auth,
                              "Accept":"application/json"
                         })

        return r.json()

    def bridge_to_scroll(self, amount, net):
       
        data, authNonce, signature, auth = self.createBridgedWithdrawalPayload({"token": "ETH", "chain": "SCROLL", "amount": amount, "nonce": None})
        if auth == 0:
            logger.error(f"[{self.account.address}] can't create rhino txn")
            return
        success, signed_txn, tx_token =self.deposit(amount=amount) #True, 0, "0xd787e2ddfa3da5e3cb3a8b48b4181bba9a4125888d57580735c5c98f3ef5fc4d"#

        if not success:
            return
        data ={
            "amount": str(int(amount*100000000)),
            "bridge": data,
            "chain": "ARBITRUM",
            "token": "ETH",
            "txHash": tx_token
        }
        r = requests.post("https://api.rhino.fi/v1/trading/bridge", json=data, headers={
            "authorization": auth,
            "Accept":"application/json",
            "Accept-Encoding":"utf-8",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Content-Type":"application/json",
            "Origin":"https://app.rhino.fi",
            "Referer":"https://app.rhino.fi/",
            "Sec-Ch-Ua":'"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
            "Sec-Ch-Ua-Mobile":"?0",
            "Sec-Ch-Ua-Platform":'"Windows"',
            "Sec-Fetch-Dest":"empty",
            "Sec-Fetch-Mode":"cors",
            "Sec-Fetch-Site":"same-site",
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
        })
        logger.success(f"[{self.account.address}] Bridge sent. Bridge data:{r.json()}")

        #for i in range(10):
        #    print(i)
        #    print(self.get_bridges(auth)["items"][0])
        #    sleep(10)
