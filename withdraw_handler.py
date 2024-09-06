import logging
from web3 import Web3
from colorama import Fore, Style
import time
from utils import wait_for_low_gas_price

def get_balance_to_withdraw(web3, abi, xp_farm_address, my_address):
    contract = web3.eth.contract(xp_farm_address, abi=abi)
    try:
        balance = contract.functions.balanceOf(my_address).call()
        print(f"Balance to withdraw for {my_address}: {web3.from_wei(balance,'ether')} jvUSDC")
        return balance
    except Exception as e:
        logging.error(f"Error fetching shares: {e}")
        return 0


def withdraw(web3, abi, usdc_contract_address, avantis_adress, private_key, my_address, GAS_PRICE_THRESHOLD):
    wait_for_low_gas_price(web3, GAS_PRICE_THRESHOLD)
    nonce = web3.eth.get_transaction_count(my_address)
    amount_to_withdraw = get_balance_to_withdraw(web3, abi, avantis_adress, my_address)
    
    if amount_to_withdraw == 0:
        logging.info(f"Staked USDT < 0...")
        return
    
    contract = web3.eth.contract(address=avantis_adress, abi=abi)
    transaction = contract.functions.increaseAllowance('0x944766f715b51967E56aFdE5f0Aa76cEaCc9E7f9', amount_to_withdraw)

    txn = transaction.build_transaction({
            'chainId': 8453,
            'gas': 300000,
            'gasPrice': web3.eth.gas_price,
            'nonce': nonce,
        })
    
    signed_txn = web3.eth.account.sign_transaction(txn, private_key=private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    logging.info(f"Waiting 1st transaction for withdraw...")
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    message = f"[{my_address}] : Withdraw 1st transaction confirmed - {tx_receipt.transactionHash.hex()}"
    logging.info(message)
    print(Fore.GREEN + message + Style.RESET_ALL)

def withdraw2(web3, abi, usdc_contract_address, avantis_adress, private_key, my_address, GAS_PRICE_THRESHOLD):
    wait_for_low_gas_price(web3, GAS_PRICE_THRESHOLD)
    nonce = web3.eth.get_transaction_count(my_address)
    amount_to_withdraw = get_balance_to_withdraw(web3, abi, avantis_adress, my_address)
        
    if amount_to_withdraw == 0:
        logging.info(f"Staked USDT < 0...")
        return
        
    contract = web3.eth.contract(address=avantis_adress, abi=abi)
    transaction = contract.functions.redeem(amount_to_withdraw, my_address, my_address)

    txn = transaction.build_transaction({
                'chainId': 8453,
                'gas': 300000,
                'gasPrice': web3.eth.gas_price,
                'nonce': nonce,
        })
        
    signed_txn = web3.eth.account.sign_transaction(txn, private_key=private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    logging.info(f"Waiting 2st transaction for withdraw...")
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    message = f"[{my_address}] : Withdraw 2st transaction confirmed - {tx_receipt.transactionHash.hex()}"
    logging.info(message)
    print(Fore.GREEN + message + Style.RESET_ALL)

