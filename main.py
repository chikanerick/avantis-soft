import curses
import logging
import random
import time
import pyfiglet
from web3 import Web3
from colorama import Fore, Style, init
from settings import DELAY, RPC_URL, PERCENT_TO_DEP, GAS_PRICE_THRESHOLD
from abi import usdc_abi, avantis_abi
from deposit_handler import approve_usdt, deposit_usdt
from withdraw_handler import withdraw, withdraw2

init()

logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler('transactions.log')
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

web3 = Web3(Web3.HTTPProvider(RPC_URL))

if not web3.is_connected():
    raise Exception("Can't connect to Base network")

usdc_contract_adress = Web3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")
avantis_contract_address = Web3.to_checksum_address("0x944766f715b51967E56aFdE5f0Aa76cEaCc9E7f9")
usdc_contract = web3.eth.contract(address=usdc_contract_adress, abi=usdc_abi)

with open('private_keys.txt', 'r') as file:
    private_keys = [line.strip() for line in file.readlines()]

total_keys = len(private_keys)

def draw_menu(stdscr, selected_row_idx):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    ascii_art = pyfiglet.figlet_format("AUTOSOFT", font="slant")
    lines = ascii_art.split("\n")

    try:
        for i, line in enumerate(lines):
            if i < h - 4:  
                stdscr.attron(curses.color_pair(2))
                stdscr.addstr(i, 0, line, curses.A_BOLD) 
                stdscr.attroff(curses.color_pair(2))
    except curses.error as e:
        print(f"Curses error: {e}")

    try:
        stdscr.attron(curses.color_pair(1))
        stdscr.addstr(len(lines), 0, "deposit and withdraw usdc on avantisfi.com", curses.A_BOLD)
        stdscr.attroff(curses.color_pair(1))
    except curses.error as e:
        print(f"Curses error: {e}")

    menu = ['deposit', 'withdraw']
    try:
        for idx, row in enumerate(menu):
            x = 0  
            y = len(lines) + 2 + idx
            if y < h:  
                if idx == selected_row_idx:
                    stdscr.attron(curses.color_pair(1))
                    stdscr.addstr(y, x, row)
                    stdscr.attroff(curses.color_pair(1))
                else:
                    stdscr.addstr(y, x, row)
    except curses.error as e:
        print(f"Curses error: {e}")

    stdscr.refresh()
    
def main(stdscr):
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)  

    current_row = 0

    draw_menu(stdscr, current_row)

    while True:
        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(['deposit', 'withdraw']) - 1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if current_row == 0:
                choice = 'deposit'
            elif current_row == 1:
                choice = 'withdraw'
            break

        draw_menu(stdscr, current_row)

  
    curses.endwin()

    if choice == 'deposit':
        process_deposit()
    elif choice == 'withdraw':
        process_withdraw()


def process_deposit():
    for index, private_key in enumerate(private_keys):
        my_address = web3.eth.account.from_key(private_key).address
        balance = usdc_contract.functions.balanceOf(my_address).call()
        amount = int(balance * PERCENT_TO_DEP/100)
        print (f'[{my_address}] working...')
        print(f"Balance: {web3.from_wei(balance,'ether')} usdt")
        print(f"Staking amount: {web3.from_wei(amount,'ether')} usdt")

        approve_usdt(web3, usdc_contract, avantis_contract_address, private_key, my_address, amount, index)
        deposit_usdt(web3, avantis_abi, usdc_contract_adress, avantis_contract_address, private_key, my_address, amount, index, GAS_PRICE_THRESHOLD, total_keys)

        delay = random.uniform(DELAY[0], DELAY[1])
        logging.info(f"Delay for {delay:.2f} seconds.")
        time.sleep(delay)

def process_withdraw():
    for index, private_key in enumerate(private_keys):
        my_address = web3.eth.account.from_key(private_key).address
        
        withdraw(web3, avantis_abi, usdc_contract_adress, avantis_contract_address, private_key, my_address, GAS_PRICE_THRESHOLD)
        withdraw2(web3, avantis_abi, usdc_contract_adress, avantis_contract_address, private_key, my_address, GAS_PRICE_THRESHOLD)
        delay = random.uniform(DELAY[0], DELAY[1])
        logging.info(f"Delay for {delay:.2f} seconds.")
        time.sleep(delay)

curses.wrapper(main)