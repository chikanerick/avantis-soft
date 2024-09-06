import logging
import time
from web3 import Web3
from colorama import Fore, Style
from utils import wait_for_low_gas_price

def approve_usdt(web3, usdc_contract, lombard_adress, private_key, my_address, amount, index):
    try:
        nonce = web3.eth.get_transaction_count(my_address)
        transaction = usdc_contract.functions.approve(lombard_adress, 115792089237316195423570985008687907853269984665640564039457584007913129639935)
        txn = transaction.build_transaction({
            'chainId': 8453,
            'gas': 200000,
            'gasPrice': int(web3.eth.gas_price * 1.1),
            'nonce': nonce,
        })

        signed_txn = web3.eth.account.sign_transaction(txn, private_key=private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        logging.info(f"Waiting approval...")
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

        message = f"[{my_address}] : approval transaction confirmed - {tx_receipt.transactionHash.hex()}"
        logging.info(message)
        print(Fore.GREEN + message + Style.RESET_ALL)

    except Exception as e:
        message = f"[{my_address}] : Error during approval - {e}"
        logging.error(message)
        print(Fore.RED + message + Style.RESET_ALL)

        with open('error_keys.txt', 'a') as error_file:
            error_file.write(private_key + '\n')

def deposit_usdt(web3, abi, wbtc_contract_adress, lombard_adress, private_key, my_address, amount, index, GAS_PRICE_THRESHOLD, total_keys):
    try:
        wait_for_low_gas_price(web3, GAS_PRICE_THRESHOLD)
        nonce = web3.eth.get_transaction_count(my_address)
        contract = web3.eth.contract(address=lombard_adress, abi=abi)
       
        
        adress_aset = '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599'
        transaction = contract.functions.deposit(amount, my_address)

        txn = transaction.build_transaction({
            'chainId': 8453,
            'gas': 600000,
            'gasPrice': int(web3.eth.gas_price * 1.1),
            'nonce': nonce,
        })
        # gas_limit = web3.eth.estimate_gas(txn)
        # txn['gas'] = gas_limit 
        signed_txn = web3.eth.account.sign_transaction(txn, private_key=private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        logging.info(f"Waiting deposit...")
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

        message = f"[{my_address}] : Deposit transaction confirmed - {tx_receipt.transactionHash.hex()}"
        logging.info(message)
        print(Fore.GREEN + message + Style.RESET_ALL)

    except Exception as e:
        message = f"[{my_address}] : Deposit error - {e}"
        logging.error(message)
        print(Fore.RED + message + Style.RESET_ALL)

        with open('error_keys.txt', 'a') as error_file:
            error_file.write(private_key + '\n')

    print(Fore.YELLOW + f"Processed {index + 1} from {total_keys} wallets." + Style.RESET_ALL)

