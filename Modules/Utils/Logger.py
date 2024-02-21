from loguru import logger as console_log
from Modules.config import SETTINGS_PATH
import json

global_log = ""
indexes = []
def write_global_log():
    global global_log
    print(global_log)
    print(f"{SETTINGS_PATH}logs.txt")
    with open(f"{SETTINGS_PATH}logs.txt", "w") as f:
        f.write(global_log)

write_global_log()

class logger():
    @staticmethod
    def info(message: str):
        global global_log
        try:
            addr = message.split("]")[0][1::]

            if addr not in indexes:
                indexes.append(addr)

            console_log.info(f"[{addr}] [{indexes.index(addr)+1}/{len(indexes)}] {message.split(']')[1]}")

        except Exception as e:
            print(e)
    
    @staticmethod
    def error(message: str):
        global global_log
        try:
            addr = message.split("]")[0][1::]

            if addr not in indexes:
                indexes.append(addr)
            with open(f"{SETTINGS_PATH}logs.json") as f:
                init_log = json.load(f)
            init_log["fail"] += 1
            with open(f"{SETTINGS_PATH}logs.json", "w") as f:
                json.dump(init_log, f, indent=1)
            msg = ""
            for i in range(1, len(message.split("]"))):
                msg += message.split("]")[i]
                if i < len(message.split("]"))-1:
                    msg += "]"

            console_log.error(f"[{addr}] [{indexes.index(addr)+1}/{len(indexes)}] {msg}")

        except Exception as e:
            print(e)
    
    @staticmethod
    def success(message: str):
        global global_log
        try:
            addr = message.split("]")[0][1::]

            if addr not in indexes:
                indexes.append(addr)

            console_log.success(f"[{addr}] [{indexes.index(addr)+1}/{len(indexes)}] {message.split(']')[1]}")
            with open(f"{SETTINGS_PATH}logs.json") as f:
                init_log = json.load(f)
            init_log["success"] += 1
            with open(f"{SETTINGS_PATH}logs.json", "w") as f:
                json.dump(init_log, f, indent=1)
        except Exception as e:
            print(e)
