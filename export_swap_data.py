import argparse
from web3 import Web3
import json
import requests
import csv
from prettytable import PrettyTable

from dotenv import load_dotenv
from os import getenv

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import Style
from pygments.lexers.solidity import SolidityLexer
from prompt_toolkit import print_formatted_text, HTML

infura_id = "60e52c2fc2764ffab5385cc6342fca3a"

def print_deposit_events(ditto_contract, fromBlock, toBlock, session):
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
    print_formatted_text(HTML("<aaa fg='ansiwhite' bg='ansigreen'>&#9989; Saved to "+str(fromBlock)+"-"+str(toBlock)+".csv</aaa>"))



def main():
    abi = json.load(open('abi.json', 'r'))
    contract_address = "0xFDaCD496EfFB198C81Fb5E74F156e889f4ecCF91"
    w3r = Web3(Web3.HTTPProvider('https://ropsten.infura.io/v3/'+infura_id))
    w3b = Web3(Web3.HTTPProvider('https://bsc-dataseed.binance.org/'))
    ditto_contract = w3r.eth.contract(address=contract_address, abi=abi)
    fromBlock = 1
    toBlock = 1000000000
    completer = WordCompleter(['historical swaps', 'real time swaps'])
    style = Style.from_dict({
        'completion-menu.completion': 'bg:#008888 #ffffff',
        'completion-menu.completion.current': 'bg:#00aaaa #000000',
        'scrollbar.background': 'bg:#88aaaa',
        'scrollbar.button': 'bg:#222222',
    })
    session = PromptSession(
        lexer=PygmentsLexer(SolidityLexer), completer=completer, style=style)

    while True:
        try:
            text = session.prompt('> ')
            print(text)
            if (text == 'historical swaps'):
                startBlock = session.prompt(HTML('> &#9658; Start Block: '))
                endBlock = session.prompt(HTML('> &#9658; End Block: '))
                print_deposit_events(ditto_contract, int(startBlock), int(endBlock), session)
        except KeyboardInterrupt:
            continue  # Control-C pressed. Try again.
        except EOFError:
            break  # Control-D pressed.
    # print_deposit_events(ditto_contract, 1, 1000000000)

if __name__ == '__main__':
    main()
