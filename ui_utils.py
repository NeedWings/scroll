from imports import *


def get_correct_path(path: str) -> str:
    if PLATFORM == "Windows":
        return path.replace("/", "\\")
    elif PLATFORM == "Darwin":
        return path.replace("\\", "/")


def load_json_file(path: str) -> dict:
    _path = get_correct_path(path)
    with open(_path, encoding="utf-8") as file:
        return json.load(file)


def change_last_req_status():
    os.environ["last_request"] = str(int(time()))


def dump_json(file_path: str, data: dict) -> None:
    with open(get_correct_path(file_path), "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def answer(status: str = "ok", change_status: bool = True, **kwargs) -> dict:
    if change_status: change_last_req_status()

    response = {"status": status}
    for k in kwargs.keys(): response[k] = kwargs[k]

    return jsonify(response)


def flip_work_status(status: bool, general_settings_path) -> None:
    _local_data = load_json_file(general_settings_path)
    _local_data["mainStatus"] = status

    dump_json(general_settings_path, _local_data)


DEFAULT_NODES = {
    "ethereum": ["https://rpc.ankr.com/eth"],
    "bsc": ["https://rpc.ankr.com/bsc"],
    "fantom": ["https://rpc.ankr.com/fantom"],
    "polygon": ["https://rpc.ankr.com/polygon"],
    "arbitrum": ["https://rpc.ankr.com/arbitrum"],
    "avalanche": ["https://rpc.ankr.com/avalanche"],
    "optimism": ["https://rpc.ankr.com/optimism"],
    "celo": ["https://rpc.ankr.com/celo"],
    "gnosis": ["https://rpc.ankr.com/gnosis"],
    "polygon_zkevm": ["https://rpc.ankr.com/polygon_zkevm"],
    "zksync": ["https://rpc.ankr.com/zksync_era"]
}
