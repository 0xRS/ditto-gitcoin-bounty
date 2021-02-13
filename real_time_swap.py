import argparse
from web3 import Web3
import json
import requests
import csv
from prettytable import PrettyTable
from dotenv import load_dotenv
from os import getenv

infura_id = "60e52c2fc2764ffab5385cc6342fca3a"

#save pk in a .env file
load_dotenv('.env')
private_key = getenv('pk')


def handle_event(event):
    print(event)

async def log_loop(event_filter, poll_interval):
    while True:
        for event in event_filter.get_new_entries():
            handle_event(event)
        await asyncio.sleep(poll_interval)

def main():
    abi = json.load(open('abi.json', 'r'))
    contract_address = "0xFDaCD496EfFB198C81Fb5E74F156e889f4ecCF91"
    w3r = Web3(Web3.HTTPProvider('https://ropsten.infura.io/v3/'+infura_id))
    w3b = Web3(Web3.HTTPProvider('https://bsc-dataseed.binance.org/'))
    ditto_contract = w3r.eth.contract(address=contract_address, abi=abi)
    block_filter = w3.eth.filter('latest')
    tx_filter = w3.eth.filter('pending')
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            asyncio.gather(
                log_loop(block_filter, 2),
                log_loop(tx_filter, 2)))
    finally:
        loop.close()
