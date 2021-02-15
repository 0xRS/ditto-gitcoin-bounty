from web3 import Web3
import json
import requests
import csv
from prettytable import PrettyTable

from dotenv import load_dotenv
from os import getenv

import asyncio

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import Style
from pygments.lexers.solidity import SolidityLexer
from prompt_toolkit import print_formatted_text, HTML
from halo import Halo
from time import sleep

@Halo(text='Sending DITTO Drops on BSC', spinner='dots')
def send_tx(receiver, amount):
    ditto_erc20_address = getenv('ditto_erc20')
    pk = getenv('pk')
    bsctestnet_rpc = getenv('bsctestnet_rpc')
    w3b = Web3(Web3.HTTPProvider(bsctestnet_rpc))
    acc = w3b.eth.account.from_key(pk)
    erc20_abi = json.load(open('erc20_abi.json', 'r'))
    erc20 = w3b.eth.contract(address=ditto_erc20_address, abi=erc20_abi)
    nonce = w3b.eth.getTransactionCount(acc.address)
    tx = erc20.functions.transfer(receiver, amount).buildTransaction({
        'chainId': 97,
        'gas': 200000,
        'gasPrice': w3b.toWei('20', 'gwei'),
        'nonce': nonce,
    })
    signed_txn = w3b.eth.account.sign_transaction(tx, private_key=pk)

    spinner = Halo(text='Sending Ditto Tokens to '+receiver, spinner='line')
    spinner.start()

    sent_tx = w3b.eth.sendRawTransaction(signed_txn.rawTransaction)

    # wait for deployment transaction to be mined
    while True:
        try:
            receipt = w3b.eth.getTransactionReceipt(sent_tx)
            if receipt:
                break
        except:
            sleep(1)
    spinner.stop()
    # erc20.functions.transfer(str(receiver), int(amount)).transact({"from": acc})

def check_to_send(tx_list, latest_block, confirmations):
    while True:
        if(len(tx_list)>0):
            if (latest_block - int(tx_list[0][0]) >= confirmations):
                receiver = tx_list[0][1]
                amount = tx_list[0][4]
                send_tx(receiver, amount)
                del tx_list[0]
            else:
                return
        else:
            return

def handle_event(e, tx_list, confirmations):
    block_number = e['blockNumber']
    depositor = e['args']['depositor']
    input_token = e['args']['input']
    input_amount = e['args']['inputAmount']
    output_amount = e['args']['outputAmount']
    tx = [block_number, depositor, input_token, input_amount, output_amount]
    # print(tx[1], tx[2], tx[3], tx[4])
    # print("-"*120)
    tx_list.append(tx)
    print("=====Pending Transfers===")
    x  = PrettyTable()
    header = ['block', 'address', 'inputTokenName', 'inputAmount', 'outputAmount']
    x.field_names = header
    x.add_rows(tx_list)
    print(x)

async def log_loop(event_filter, poll_interval, tx_list, confirmations):
    while True:
        infura_id = getenv('infura_id')
        w3r = Web3(Web3.HTTPProvider('https://ropsten.infura.io/v3/'+infura_id))
        latest_block = w3r.eth.getBlock('latest')['number']
        if(len(tx_list)>0):
            check_to_send(tx_list, latest_block, confirmations)
        # check_to_send(tx_list, latest_block, confirmations)
        for event in event_filter.get_new_entries():
            handle_event(event, tx_list, confirmations)
        await asyncio.sleep(poll_interval)

def real_time_swap_events(ditto_contract, pk, confirmations):
    event_filter = ditto_contract.events.SwapDeposit.createFilter(fromBlock='latest')
    loop = asyncio.get_event_loop()
    tx_list = []
    try:
        loop.run_until_complete(
            asyncio.gather(log_loop(event_filter, 2, tx_list, confirmations)))
    finally:
        loop.close()

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
    print_formatted_text(HTML("<aaa fg='ansiwhite' bg='ansigreen'>&#9989; Saved to "+str(fromBlock)+"-"+str(toBlock)+".csv</aaa>"))



def main():
    abi = json.load(open('abi.json', 'r'))

    #load env
    load_dotenv('.env')
    pk = getenv('pk')
    infura_id = getenv('infura_id')
    ditto_erc20 = getenv('ditto_erc20')
    contract_address = getenv('ditto_contract')
    bsctestnet_rpc = getenv('bsctestnet_rpc')

    #init web3
    w3r = Web3(Web3.HTTPProvider('https://ropsten.infura.io/v3/'+infura_id))
    w3b = Web3(Web3.HTTPProvider(bsctestnet_rpc))
    ditto_contract = w3r.eth.contract(address=contract_address, abi=abi)

    #init prompt toolkit
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
                print_deposit_events(ditto_contract, int(startBlock), int(endBlock))
            elif (text == 'real time swaps'):
                real_time_swap_events(ditto_contract, pk, 15)

        except KeyboardInterrupt:
            continue  # Control-C pressed. Try again.
        except EOFError:
            break  # Control-D pressed.

if __name__ == '__main__':
    main()
