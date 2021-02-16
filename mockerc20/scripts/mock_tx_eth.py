from brownie import accounts, Contract
from brownie import MockERC20Token
from dotenv import load_dotenv
from os import getenv
import json
from time import sleep
import random

def main():
    load_dotenv('.env')
    pk = getenv('pk')
    swap_contract_address = getenv('swap_contract_address')
    mock_erc20_address = getenv('mock_erc20')
    accounts.add(pk)
    abi = json.load(open('abi.json', 'r'))
    erc20_abi = json.load(open('erc20_abi.json', 'r'))
    mockerc20 = Contract.from_abi("Mock ERC20", mock_erc20_address, erc20_abi)
    swap_contract = Contract.from_abi("Swap Contract", swap_contract_address, abi)
    mockerc20.approve(swap_contract_address, 10**30, {"from": accounts[0], "allow_revert": True})

    while True:
        amount = random.randint(1, 10)
        swap_contract.swap(mock_erc20_address, amount*10**18, {"from": accounts[0], "allow_revert": True})
        sleep_time = random.randint(15, 30)
        sleep(sleep_time)
