from BaseClasses import *
from token_stor import *


class Dmail():
    w3: Web3 = Web3(Web3.HTTPProvider(random.choice(RPC_LSIT["scroll"])))
    contract_address = "0x47fbe95e981C0Df9737B6971B451fB15fdC989d9"
    ABI = [{"type":"event","name":"Message","inputs":[{"type":"address","name":"from","internalType":"address","indexed":true},{"type":"string","name":"to","internalType":"string","indexed":true},{"type":"string","name":"path","internalType":"string","indexed":true}],"anonymous":false},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"send_mail","inputs":[{"type":"string","name":"to","internalType":"string"},{"type":"string","name":"path","internalType":"string"}]}]
    contract: Contract = w3.eth.contract(contract_address, abi=ABI)
    name = "Dmail"

    def send_msg(self, sender: BaseAccount):
        a = "1234567890qwertyuiopasdfghjklzxcvbnm"
        msg = ""
        for i in range(random.randint(5,9)):
            msg += random.choice(a)

        to = ""
        for i in range(random.randint(5, 9)):
            to += random.choice(a)
        to += "@gmail.com"

        txn_data_handler = EVMTransactionDataHandler(sender, "scroll")
        logger.info(f"[{sender.get_address()}] going to send message")
        txn = self.contract.functions.send_mail(msg, to).build_transaction(txn_data_handler.get_txn_data())

        return [txn]



