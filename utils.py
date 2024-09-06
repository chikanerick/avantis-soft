import logging
import time

def wait_for_low_gas_price(web3, threshold_gwei):
    while True:
        current_gas_price = web3.from_wei(web3.eth.gas_price, 'gwei')
        if current_gas_price <= threshold_gwei:
            break
        else:
            logging.info(f"Current gas price ({current_gas_price} Gwei) > ({threshold_gwei} Gwei). Waiting...")
            time.sleep(10)