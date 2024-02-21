import json

from eth_account import Account as ethAccount

from just_server import run_app
from Modules.config import SETTINGS_PATH, get_general_settings

def main():
    run_app()
            
if __name__ == "__main__":
    main()


