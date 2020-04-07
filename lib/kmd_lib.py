import time
import subprocess
import platform
import pycurl
import stat
import os
import re
import sys
import zipfile
import json
import shutil
import logging
import asyncio
import urllib.request
from telethon import TelegramClient
from slickrpc import Proxy
from launch_params import ticker_params
from tickers import ac_tickers


def start_ticker(ticker):
    ticker_launch = ''
    #get the ticker_launch command
    if 'KMD' in ticker:
        ticker_launch = 'komodod -deamon'.split(" ")
    else:
        try:
            ticker_launch = ticker_params[ticker].split(" ")[:-1]
        except Exception as e:
            return str(e)
    #if ticker exists open up a process
    if ticker_launch:
        ticker_output = open(sys.path[0]+'/ticker_output/'+ticker+"_output.log",'w+')
        subprocess.Popen(ticker_launch, stdout=ticker_output, stderr=ticker_output, universal_newlines=True)
        return 'Sync of ' + ticker + ' has started!'


def stop_ticker(ticker):
    try:
        rpc = set_rpc_proxy(ticker)
        return rpc.stop()
    except Exception as e:
        return "{} : {}".format(ticker, str(e))


def get_sync_stats(ticker):
    try:
        rpc = set_rpc_proxy(ticker)
        info = rpc.getinfo()
        return({
            "coin" : info['name'],
            "synced" : info['synced'],
            "blocks" : info['blocks'],
            "longestchain" : info['longestchain'],
        })
    except Exception as e:
        pass


def get_all_sync_stats():
    stats = {}
    amount = 0
    for ticker in ac_tickers:
        current = get_sync_stats(ticker)
        if current:
            stats[ticker] = current
    
    for k,v in stats.items():
        try:
            if v["coin"]:
                amount += 1
        except TypeError:
            pass

    return {"amount" : str(amount), "stats" : stats}


def set_rpc_proxy(ticker):
    rpcport = ''
    ac_dir = ''
    operating_system = platform.system()
    if 'Darwin' in operating_system:
        ac_dir = '{}/Library/Application Support/Komodo'.format(os.environ['HOME'])
    elif 'Linux' in operating_system:
        ac_dir = '{}/.komodo'.format(os.environ['HOME'])
    elif 'Win64' in operating_system or 'Windows' in operating_system:
        ac_dir = '{}/komodo/'.format(os.environ['APPDATA'])
    if ticker == 'KMD':
        coin_config_file = '{}/komodo.conf'.format(ac_dir)
    else:
        coin_config_file = '{}/{}/{}.conf'.format(ac_dir, ticker, ticker, '.conf')

    with open(coin_config_file, 'r') as config_file:
        for line in config_file:
            line = line.rstrip()
            if 'rpcuser' in line:
                rpcuser = line[7:]
                continue
            elif 'rpcpassword' in line:
                rpcpassword = line[11:]
                continue
            elif 'rpcport' in line:
                rpcport = line[7:]

    if not rpcport:
        if 'KMD' in ticker:
            rpcport = 7771
        else:
            #logger.info("rpcport not in conf file, exiting")
            #logger.info("check "+coin_config_file)
            return

    return Proxy("http://{}:{}@127.0.0.1:{}".format(rpcuser, rpcpassword, int(rpcport)))


def clean_ticker_data(ticker):
    kmd_dir = '{}/.komodo/'.format(os.environ['HOME'])
    dirs = ['{}{}/'.format(kmd_dir, ticker)]
    if "KMD" in ticker:
        dirs = ['{}blocks/'.format(kmd_dir), '{}chainstate/'.format(kmd_dir), '{}database/'.format(kmd_dir)]
    try:
        for folder in dirs:
            shutil.rmtree(folder)
        return 'cleaning {} folder'.format(ticker)
    except FileNotFoundError:
        pass


def clean_all_ticker_data():
    for ticker in ac_tickers[1:]:
        clean_ticker_data(ticker)
    return 'cleaning assetchains folders'


def start_all_tickers():
    for ticker in ac_tickers[1:]:
        start_ticker(ticker)
    return 'starting all tickers'


def stop_all_tickers():
    for ticker in ac_tickers[1:]:
        stop_ticker(ticker)
    retur 'stopping all tickers'



def get_ticker_params():
    return ticker_params


def get_ticker_list():
    return ac_tickers


def setup_params(link):
    pass


def download_binary(link):
    urllib.request.urlretrieve('{}'.format(link), 'newbinary.zip')


async def download_dragndrop():
    async with TelegramClient('ericswan', os.environ['API_ID'], os.environ['API_HASH']) as client:
        last_msg = await client.get_messages('komodo_sync_bot', 1)
        await client.download_media(last_msg, '/root/new-binary.zip')


async def setup_binary_dragndrop(link):
    if 'drag' in link:
        loop = asyncio.get_event_loop()
        await loop.run_until_complete(download_dragndrop())
    else:
        download_binary(link)
    
    try:
        os.remove('/root/komodo/komodod')
        os.remove('/root/komodo/komodo-cli')
    except FileNotFoundError:
        pass
    with zipfile.ZipFile('/root/new-binary.zip', 'r') as zip_ref:
        zip_ref.extractall('/root/komodo')
    os.chmod('/root/komodo/komodod', stat.S_IRWXU)
    os.chmod('/root/komodo/komodo-cli', stat.S_IRWXU)

    return "changed to new binary"