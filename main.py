import json
import multiprocessing

from termcolor import colored
import inquirer
from inquirer.themes import load_theme_from_dict as loadth

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
            "Bridge",
            "Withdraw", 
            
            "Add To Lend",
            "Borrow",
            "Remove From Lend",
            "Repay",
            "Add Liquidity",
            "Remove Liquidity",
            "Send To OKX Subs",
            "Withdraw From OKX",
            "Dmail",
            "Random Swaps",
            "Save Assets",
            "ZkStars mint",

            "========================",
            "encrypt_secret_keys"
        ],
    )
    ]
    action = inquirer.prompt(question, theme=loadth(theme))['action']
    return action



def main():
    run_app()
            
if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()


