from brownie import accounts, Contract
from brownie import MockERC20Token
from dotenv import load_dotenv
from os import getenv

def main():
    load_dotenv('.env')
    pk = getenv('pk')
    accounts.add(pk)
    MockERC20Token.deploy("DITTO", "DITTO", 18, {"from": accounts[0]})
