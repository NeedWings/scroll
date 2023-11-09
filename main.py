try:
    from MainRouter import *
    from do_not_touch import *
    
    if __name__ == "__main__":
        pass
        checking_license()
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
                    "(9) dmail",
                    "",
                    "(10) full",
                    "",
                    "(12) deploy contract",
                    "",
                    "(13) mint zkstars",
                    "",
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
        elif action == "(12) deploy contract":
            task_number = 12
        elif action == "(13) mint zkstars":
            task_number = 13

        
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
            if SETTINGS["delayed_start"]:
                console_log.info("sleeping {(SETTINGS['delayed_start_time']} hours")
                sleep(SETTINGS["delayed_start_time"]*3600)
            delay = 0
            shuffle(accounts)
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
