import sys
from threading import Event

from web3 import Web3

from ui_utils import *
from Modules.Utils.launch import encode_secrets, decrypt_private_keys, check_license_elig, user_key
from Modules.config import accounts
from Modules.Utils.Account import Account
from Modules.Utils.starter import Starter

local_files_path = get_correct_path(getcwd() + "/data/app/")

general_settings_path = local_files_path + "general-settings.json"
launch_path = local_files_path + "launch.json"
wallets_path = local_files_path + "wallets.json"
logs_path = local_files_path + "logs.json"
logs_txt_path = local_files_path + "logs.txt"

app = Flask(__name__)
CORS(app)


closing = False
gas_lock = Event()
starter = Starter()
eth_provider = Web3(Web3.HTTPProvider("https://gateway.tenderly.co/public/mainnet"))

@app.route("/ping", methods=["POST"])
def ping():
    return answer()


@app.route("/change_logger", methods=["POST"])
def change_logger():
    _local_data = load_json_file(general_settings_path)
    _local_data["Logger"] = request.json

    dump_json(general_settings_path, _local_data)
    return answer()


@app.route("/close", methods=["POST"])
def close():
    global closing
    closing = True
    return answer(True)  # обязательно возвращать ответ


@app.route("/get-launch-json", methods=["POST"])
def get_launch_json():
    try:
        _local_data = load_json_file(launch_path)
        return answer(_local_data)

    except:
        return answer("error", details=traceback.format_exc())


@app.route("/set_max_gwei", methods=["POST"])
def set_max_gwei():
    try:
        _local_data = load_json_file(general_settings_path)
        _local_data["max-gwei"] = request.json

        dump_json(general_settings_path, _local_data)

        return answer(_local_data)

    except:
        return answer("error", details=traceback.format_exc())


@app.route("/check_pass_exist", methods=["POST"])
def ceck_pass_exist():
    with open(get_correct_path(getcwd() + "/data/encoded_secrets.txt")) as file:
        if len(file.read()) < 5:
            return answer(False)

    return answer()


@app.route("/get-wallets-json", methods=["POST"])
def get_wallets_json():
    try:
        _local_data = load_json_file(wallets_path)
        return answer(_local_data)

    except:
        return answer("error", details=traceback.format_exc())


@app.route("/get-settings-json", methods=["POST"])
def get_sensetings_json():
    try:
        _local_data = load_json_file(general_settings_path)
        return answer(_local_data)

    except:
        return answer("error", details=traceback.format_exc())


@app.route("/get-logs-json", methods=["POST"])
def get_logs_json():
    try:
        _local_data = load_json_file(logs_path)
        return answer(_local_data)

    except:
        return answer("error", details=traceback.format_exc())


@app.route("/get_logs", methods=["POST"])
def get_logs():
    try:
        with open(logs_txt_path, encoding="utf-8") as file:
            data = file.read()
        return data

    except:
        return answer("error", details=traceback.format_exc())


@app.route("/check_license", methods=["POST"])
def check_license():
    try:
        soft_type = "scroll"
        key = user_key
        print(key)
        print(key)
        print(key)
        print(key)
        print(key)
        _local_data = load_json_file(general_settings_path)
        _local_data["main"]["key"] = key
        dump_json(general_settings_path, _local_data)

        check_license_elig(key)
        return answer(license_status=True, user_key=key)

    except:
        return answer(license_status=False, user_key=key)


@app.route("/change_wallets", methods=["POST"])
def change_wallets():
 
    try:
        data = request.json
        for wallet in data.keys():
            addr = wallet.lower().replace("\r", "")
            prev: Account = accounts.get(addr)
            if prev is None:
                continue
            prev.set_proxy(data[wallet]['proxy'])
            prev.active = data[wallet]['flag']
            accounts[wallet.lower().replace("\r", "")] = prev

        dump_json(wallets_path, request.json)
        return answer(data=request.json)

    except:
        print(traceback.format_exc())
        return answer("error", details=traceback.format_exc())


@app.route("/start", methods=["POST"])
def start():
    global gas_lock
    print(request.json)
    error = starter.start(request.json, gas_lock)
    print(error)
    if error is not None: 
        return answer("error", details=error)
    flip_work_status(True, general_settings_path)

    date_time_obj = datetime.datetime.fromtimestamp(int(time()))

    data = {"amount": 0, "success": 0, "fail": 0, "start": date_time_obj.isoformat()}
    dump_json(logs_path, data)
    return answer()


@app.route("/stop", methods=["POST"])
def stop():
    os.environ["soft_status"] = "end"
    flip_work_status(False, general_settings_path)
    if starter.running_threads is not None:
        starter.running_threads.kill()
        starter.running_threads = None
    if closing:
        kill()
    return answer()


@app.route("/check_pass", methods=["POST"])
def check_pass():

    with open(get_correct_path(getcwd() + "/data/encoded_secrets.txt")) as file:
        data = file.read()

    addrs_data = load_json_file(wallets_path)

    if len(data) > 5:
        wallets = decrypt_private_keys(request.json["password"])

        if isinstance(wallets, dict):
            print(len(wallets))
            buff = dict(addrs_data)
            for address in buff:
                if address not in list(wallets.keys()):
                    del addrs_data[address]
                    dump_json(wallets_path, addrs_data)
            for address in wallets:
                try:
                    account = Account(wallets[address], proxy=addrs_data[address]["proxy"])
                    account.active = addrs_data[address]['flag']
                    accounts[address] = account
                except:
                    pass
        
        if isinstance(wallets, str):
            return answer(False, msg=wallets, change_status=False)

    return answer()


@app.route("/change_settings", methods=["POST"])
def change_settings():
    try:
        data = request.json
        if isinstance(data, dict):
            dump_json(launch_path, data)
            return answer()
        else:
            return answer(False)

    except:
        return answer("error", details=traceback.format_exc())


@app.route("/change_rpc", methods=["POST"])
def change_rpc():
    try:
        """
        example request data :-> {"ethereum": [{}, {}], "bsc": [{},{}]}
        """
        _local_data = load_json_file(general_settings_path)
        _local_data["RPC"] = request.json

        dump_json(general_settings_path, _local_data)

        return answer()

    except:
        return answer("error", details=traceback.format_exc())


@app.route("/check_exchange_key", methods=["POST"])
def check_exchange_key():
    try:
        """
        example request data :-> {"cex_name": "binance", "data": {"key": "", "Secret": "", "Password": "pAsSw0Rd"}}
        """
        # status = checking key status func()

        status = True  # example

        if status:
            return answer()
        else:
            return answer("error")

    except:
        return answer("error", details=traceback.format_exc())


@app.route("/save_exchanges_keys", methods=["POST"])
def save_exchanges_keys():
    try:
        """
        example request data :-> {"binance": {some data}, "okx": {some data}}
        """

        _local_data = load_json_file(general_settings_path)
        _local_data["Exchanges"] = request.json

        dump_json(general_settings_path, _local_data)

        return answer()

    except:
        return answer("error", details=traceback.format_exc())


@app.route("/change_timesleep", methods=["POST"])
def change_timesleep():
    try:
        """
        example request data :-> {"TimeSleeps": {data}}
        """
        _local_data = load_json_file(general_settings_path)
        _local_data["TimeSleeps"] = request.json

        dump_json(general_settings_path, _local_data)

        return answer()

    except:
        return answer("error", details=traceback.format_exc())


@app.route("/change_bridge_settings", methods=["POST"])
def change_bridge_settings():
    try:
        """
        example request data :-> {"TimeSleeps": {data}}
        """
        _local_data = load_json_file(general_settings_path)
        _local_data["BridgeSettings"] = request.json

        dump_json(general_settings_path, _local_data)

        return answer()

    except:
        return answer("error", details=traceback.format_exc())


@app.route("/set-encode", methods=["POST"])
def set_encode():
    data = request.json
    password = data["password"]
    secrets = [i for i in data["wallets"] if len(i) in [64, 66]]

    add_status = data["add-to-work"]

    if len(secrets) != 0:
        encode_secrets(password, secrets, add_status)
    else:
        return answer("error", details=traceback.format_exc())

    return answer()


@app.route("/get_gas", methods=["POST"])
def get_gas():
    global gas_lock

    gwei = Web3.from_wei(eth_provider.eth.gas_price, "gwei")
    _local_data = load_json_file(general_settings_path)
    max_gwei = float(_local_data["TimeSleeps"]["max-ETH-gwei"])
    if gwei > max_gwei:
        gas_lock.set()
    return answer(price=round(float(gwei), 2))


@app.route("/send_error", methods=["POST"])
def get_error(msg):
    logger.info(msg)


def kill():
    def _get_executable_name():
        full_path = sys.argv[0]
        executable_name = os.path.basename(full_path)

        return executable_name
    subprocess.run(["taskkill", "/IM", "Scroll.exe", "/F"], shell=True)
    subprocess.run(["taskkill", "/IM", _get_executable_name(), "/F"], shell=True)
    sys.exit()

def run_app(): 
    flip_work_status(False, general_settings_path)

    if PLATFORM == "Darwin":
        subprocess.run(["open", local_files_path + 'Scroll.app'])
    else:
        subprocess.run(["start", local_files_path + "Scroll.exe"], shell=True)

    os.environ["last_request"] = str(int(time()))

    app.run(host="127.0.0.1", port=5000)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
