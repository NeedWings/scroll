try:
    from MainRouter import *

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
                console_log.error(f'Cant auth your device/subs')
                input("Press any key to exit")
                exit()
        except Exception as error:
            console_log.error(f'SEnd this message to dev: {error}')
            input("Press any key to exit")
            exit()

    def checking_license():
        text = wmi.WMI().Win32_ComputerSystemProduct()[0].UUID + ':SOFT'
        sha = hashlib.sha1(text.encode()).hexdigest()
        return check_license_elig(sha)

    if __name__ == "__main__":
        pass
        #checking_license()

    def get_disks():
        c = wmi.WMI()
        logical_disks = {}
        for drive in c.Win32_DiskDrive():
            for partition in drive.associators("Win32_DiskDriveToDiskPartition"):
                for disk in partition.associators("Win32_LogicalDiskToPartition"):
                    logical_disks[disk.Caption] = {"model":drive.Model, "serial":drive.SerialNumber}
        return logical_disks

    def decode_secrets():
        console_log.info("Decrypting your secret keys..")
        logical_disks = get_disks()
        decrypt_type = SETTINGS["DecryptType"].lower()
        disk = SETTINGS["LoaderDisk"]
        if decrypt_type == "flash":
            disk_data = logical_disks[disk]
            data_to_be_encoded = disk_data["model"] + '_' + disk_data["serial"]
        elif decrypt_type == "password":
            data_to_be_encoded = getpass.getpass('[DECRYPTOR] Write here password to decrypt secret keys: ')
        key = hashlib.sha256(data_to_be_encoded.encode()).hexdigest()[:43] + "="
        f = Fernet(key)
        while True:
            try:
                path = SETTINGS_PATH + 'encoded_secrets.txt'
                with open(path, 'rb') as file:
                    file_data = file.read()
                    break
            except Exception as error:
                console_log.error(f'Error with trying to open file encoded_secrets.txt! {error}')
                input("Fix it and press enter: ")
        try:
            return json.loads(f.decrypt(file_data).decode())
        except :
            console_log.error("Key to Decrypt files is incorrect!")
            return decode_secrets()

    def transform_keys(private_keys, addresses):
        w3 = Web3(Web3.HTTPProvider(random.choice(RPC_LSIT["scroll"])))
        counter = 0
        accounts = []
        for key in private_keys:
            key = private_keys[key]
            account = Account(key)
            address = account.address
            if address.lower() in addresses:
                counter +=1
                accounts.append(key) 
        return accounts, counter

    def encode_secrets():
        logical_disks = get_disks()
        while True:
            try:
                with open(SETTINGS_PATH + 'to_encrypted_secrets.txt', encoding='utf-8') as file:
                    data = file.readlines()
                    console_log.info(f'Found {len(data)} lines of keys')
                    break
            except Exception as error:
                console_log.error(f"Failed to open {SETTINGS_PATH + 'to_encrypted_secrets.txt'} | {error}")
                input("Create file and try again. Press any key to try again: ")

        json_wallets = {}
        for k in data:
            try:
                address = Account(k.replace("\n", "")).get_address()
                json_wallets.update({
                address.lower(): k.replace("\n", "")
                })
            except Exception as error:
                console_log.error(f'Cant add line: {k}')
        
        with open(SETTINGS_PATH + "data.txt", 'w') as file:
            json.dump(json_wallets, file)
        
        if SETTINGS["DecryptType"].lower() == 'flash':
            while True:
                answer = input(
                    "Write here disk name, like: 'D'\n" + \
                    ''.join(f"Disk name: {i.replace(':', '')} - {logical_disks[i]}\n" for i in logical_disks.keys())
                )
                agree = input(
                    f"OK, your disk with name: {answer} | Data: {logical_disks[answer + ':']}\n" + \
                    "Are you agree to encode data.txt using this data? [Y/N]: "
                )
                if agree.upper().replace(" ", "") == "Y":
                    break

            data = logical_disks[answer + ":"]
            data_to_encoded = data["model"] + '_' + data["serial"]
            key = hashlib.sha256(data_to_encoded.encode()).hexdigest()[:43] + "="

        elif SETTINGS["DecryptType"].lower() == 'password':
            while True:
                data_to_be_encoded = getpass.getpass('Write here password to encrypt secret keys: ')
                agree = input(
                    f"OK, Are you sure that password is correct?: {data_to_be_encoded[:4]}***\n" + \
                    "Are you agree to encode data.txt using this data? [Y/N]: "
                )  
                if agree.upper().replace(" ", "") == "Y":
                    break

            key = hashlib.sha256(data_to_be_encoded.encode()).hexdigest()[:43] + "="

        f = Fernet(key)
        with open(SETTINGS_PATH + "data.txt", 'rb') as file:
            data_file = file.read()

        encrypted = f.encrypt(data_file)

        with open(SETTINGS_PATH + "encoded_secrets.txt", 'wb') as file:
            file.write(encrypted)
        
        os.remove(SETTINGS_PATH + "data.txt")
        open(SETTINGS_PATH + "to_encrypted_secrets.txt", 'w')
        console_log.success(f'All is ok! Check to_run_addresses.txt and run soft again')
        input("Press any key to exit")
        sys.exit()

    def get_action() -> str:
        theme = {
            "Question": {
                "brackets_color": "bright_yellow"
            },
            "List": {
                "selection_color": "bright_blue"
            }
        }

        question = [
            inquirer.List(
                "action",
                message=colored("Choose soft work task", 'light_yellow'),
                choices=[
                    "encode secrets",
                    "",
                    "(1) simple bridge",
                    "(2) collect stables",
                    "(3) withdraw",
                    "",
                    "(4) swaps",
                    "(5) swap to one token",
                    "",
                    "(6) add liquidity",
                    "(7) remove liquidity",
                    "",
                    "(8) merkly",
                    "(9) dmail",
                    "",
                    "(10) full",
                    "own tasks"
                ],
            )
        ]
        action = inquirer.prompt(question, theme=loadth(theme))['action']
        return action


    def main():        
        

        print(autosoft)
        print(subs_text)
        print("\n")
        f = open(f"{SETTINGS_PATH}to_run_addresses.txt", "r")
        addresses = f.read().lower().split("\n")
        f.close()
                    
        action = get_action()
        if action == "encode secrets":
            task_number = 11
        elif action == "(1) simple bridge":
            task_number = 1
        elif action == "(2) collect stables":
            task_number = 2
        elif action ==  "(3) withdraw":
            task_number = 3
        elif action == "(4) swaps":
            task_number = 4
        elif action == "(5) swap to one token":
            task_number = 5
        elif action == "(6) add liquidity":
            task_number = 6
        elif action == "(7) remove liquidity":
            task_number = 7
        elif action == "(8) merkly":
            task_number = 8
        elif action == "(9) dmail":
            task_number = 9
        elif action == "(10) full":
            task_number = 10
        elif action == "own tasks":
            task_number = 0
        elif action == "qwe":
            task_number = 12

        
        for i in range(len(addresses)):
            if len(addresses[i]) < 50:
                addresses[i] = "0x" + "0"*(42-len(addresses[i])) + addresses[i][2::]
            else:
                addresses[i] = "0x" + "0"*(66-len(addresses[i])) + addresses[i][2::]
        if task_number == 11:
            encode_secrets()
        else:    
            private_keys = decode_secrets()
            accounts, counter = transform_keys(private_keys, addresses)
            print(f"Soft found {counter} keys to work")
            tasks = []
            delay = 0
            for account in accounts:
                tasks.append(Thread(target = MainRouter(account, delay, task_number).start))
                delay += get_random_value_int(SETTINGS["ThreadRunnerSleep"])
            
            for i in tasks:
                i.start()

            for k in tasks:
                k.join()
                
    if __name__ == "__main__":
        while True:
            main()
            input("Soft successfully end work")

except Exception as e:
    console_log.error(f"Unexpected error: {e}")

input("Soft successfully end work")
