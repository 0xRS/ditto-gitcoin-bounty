import argparse
from web3 import Web3
import json
import requests
import csv
from prettytable import PrettyTable
infura_id = "60e52c2fc2764ffab5385cc6342fca3a"

def print_deposit_events(ditto_contract, fromBlock, toBlock):
    events = ditto_contract.events.SwapDeposit.getLogs(fromBlock=fromBlock, toBlock=toBlock)
    f = open(str(fromBlock)+"-"+str(toBlock)+'.csv', 'w')
    writer = csv.writer(f)
    x  = PrettyTable()
    header = ['block', 'address', 'inputTokenName', 'inputAmount', 'outputAmount']
    writer.writerow(header)
    x.field_names = header
    for e in events:
        block_number = e['blockNumber']
        depositor = e['args']['depositor']
        input_token = e['args']['input']
        input_amount = e['args']['inputAmount']
        output_amount = e['args']['outputAmount']
        row = [block_number, depositor, input_token, input_amount, output_amount]
        writer.writerow(row)
        x.add_row(row)
    f.close()
    print(x)
abi = json.load(open('abi.json', 'r'))
contract_address = "0xFDaCD496EfFB198C81Fb5E74F156e889f4ecCF91"
w3r = Web3(Web3.HTTPProvider('https://ropsten.infura.io/v3/'+infura_id))
w3b = Web3(Web3.HTTPProvider('https://bsc-dataseed.binance.org/'))
ditto_contract = w3r.eth.contract(address=contract_address, abi=abi)

print_deposit_events(ditto_contract, 1, 1000000000)
