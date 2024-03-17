
import sys, os
import traceback
from platform import system
import socket
import hashlib
import getpass
import json

from cryptography.fernet import Fernet, InvalidToken
from loguru import logger as console_log

from modules.config import SECRETS_PATH, KEY, SETTINGS_PATH, SERVER_DATA
from modules.utils.account import Account

PLATFORM = system()
if PLATFORM == "Windows":
    import wmi

    def decrypt():
        f = Fernet(KEY)
        encrypted_data = SERVER_DATA
        decrypted_data = f.decrypt(encrypted_data).decode()
        return decrypted_data.split(':')

    server_data = decrypt()
    connect_data = (server_data[0], int(server_data[1]))

    def check_license_elig(sha):
        console_log.info("Checking license expiration date...")
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(connect_data)
            message = {
                "auth": 'scroll',
                "key": sha
            }
            client.send(json.dumps(message).encode())
            response = client.recv(1024).decode()
            client.close()
            if response == "True":
                return True
            else:
                raise Exception(f'Cant auth your device/subs')
                input("Press any key to exit")
                exit()
        except Exception as error:
            raise Exception(f'{error}')
            input("Press any key to exit")
            exit()

    def checking_license():
        text = wmi.WMI().Win32_ComputerSystemProduct()[0].UUID + ':SOFT'
        sha = hashlib.sha1(text.encode()).hexdigest()
        return check_license_elig(sha), sha
    
    def get_license_key():
        text = wmi.WMI().Win32_ComputerSystemProduct()[0].UUID + ':SOFT'
        sha = hashlib.sha1(text.encode()).hexdigest()
        return sha

    if __name__ == "__main__":
        pass
        checking_license()
    user_key = get_license_key()

else:
    import subprocess
    def decrypt(filename):
        f = Fernet(KEY)
        with open(filename, 'rb') as file:
            encrypted_data = file.read()
        decrypted_data = f.decrypt(encrypted_data).decode()
        return decrypted_data.split(':')


    server_data = decrypt(f"{SETTINGS_PATH}server_data.txt")
    connect_data = (server_data[0], int(server_data[1]))

    def check_license_elig(sha):
        console_log.info("Checking license expiration date...")
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(connect_data)
            message = {
                "auth": 'scroll',
                "key": sha
            }
            client.send(json.dumps(message).encode())
            response = client.recv(1024).decode()
            client.close()
            if response == "True":
                return True
            else:
                raise Exception(f'Cant auth your device/subs')
                input("Press any key to exit")
                exit()
        except Exception as error:
            raise Exception(f'{error}')
            input("Press any key to exit")
            exit()

    def hash_string(input_string: str) -> str:
        # Создание объекта sha256
        sha256 = hashlib.sha256()

        # Передача байтовой строки в функцию хеширования
        sha256.update(input_string.encode('utf-8'))

        # Получение и возврат хеша в шестнадцатеричном формате
        return sha256.hexdigest()


    def get_serial_number():
        try:
            # Запуск shell-команды для получения серийного номера
            serial_number = subprocess.check_output("system_profiler SPHardwareDataType | awk '/Serial/ {print $4}'", shell=True).strip().decode("utf-8")
            return serial_number
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def get_disk_uuid():
        try:
            # Запуск shell-команды для получения UUID диска
            disk_uuid = subprocess.check_output("diskutil info / | awk '/Volume UUID/ {print $3}'", shell=True).strip().decode("utf-8")
            return disk_uuid
        except Exception as e:
            print(f"An error occurred while getting disk UUID: {e}")
            return None

    def get_cpu_info():
        try:
            # Запуск shell-команды для получения информации о CPU
            cpu_info = subprocess.check_output("sysctl -n machdep.cpu.brand_string", shell=True).strip().decode("utf-8")
            return cpu_info
        except Exception as e:
            print(f"An error occurred while getting CPU information: {e}")
            return None

    def get_user_key():
        values = [
            get_cpu_info(), get_disk_uuid(), get_serial_number()
        ]
        if None in values:
            input("Cant generate api key, pls contact with support")
            return
        
        user_key = "mac_" + hash_string(''.join(i for i in values))
        return user_key

    def checking_license():
        return check_license_elig(get_user_key()), get_user_key()
    

    if __name__ == "__main__":
        pass
        checking_license()

    user_key = get_user_key()
    

def decrypt_private_keys(password):

    key = hashlib.sha256(password.encode()).hexdigest()[:43] + "="
    f = Fernet(key)
    try:
        with open(SECRETS_PATH, 'rb') as file:
            return json.loads(f.decrypt(file.read()).decode())
        
    except InvalidToken:
        error = "Key to Decrypt files is incorrect!"
        console_log.error(error)

    except Exception as error:
        error = traceback.format_exc()

    return error

def encode_secrets(password, private_keys, add_to_work):
    json_wallets = {}
    addresses = []

    for private_key in private_keys:
        address: str = Account(private_key).address
        addresses.append(address)

        json_wallets.update(
            {
                address.lower(): private_key
            }
        )

    key = hashlib.sha256(password.encode()).hexdigest()[:43] + "="
    f = Fernet(key)

    encrypted = f.encrypt(json.dumps(json_wallets).encode())

    with open(SECRETS_PATH, 'wb') as file:
        file.write(encrypted)
    
    os.environ["addresses"] = json.dumps([i.lower() for i in addresses])
    os.environ["decrypt_password"] = password

    if add_to_work:

        path = SETTINGS_PATH + "wallets.json"
        
        with open(path, "r") as f:
            data = json.load(f)

        for address in addresses:
            data[address.lower()] = {
                "flag": True,
                "proxy": "-",
                "status": True
            }
        with open(path, "w") as f:
            data = json.dump(data, f)