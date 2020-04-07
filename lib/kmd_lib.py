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
            return(str(e))
    #if ticker exists open up a process
    if ticker_launch:
        ticker_output = open(sys.path[0]+'/ticker_output/'+ticker+"_output.log",'w+')
        subprocess.Popen(ticker_launch, stdout=ticker_output, stderr=ticker_output, universal_newlines=True)
        return('Sync of ' + ticker + ' has started!')


def stop_ticker(ticker):
    try:
        rpc = set_rpc_proxy(ticker)
        return(rpc.stop())
    except Exception as e:
        return(ticker + " : " + str(e))


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

    return({"amount" : str(amount), "stats" : stats})


def set_rpc_proxy(ticker):
    rpcport = ''
    ac_dir = ''
    operating_system = platform.system()
    if operating_system == 'Darwin':
        ac_dir = os.environ['HOME'] + '/Library/Application Support/Komodo'
    elif operating_system == 'Linux':
        ac_dir = os.environ['HOME'] + '/.komodo'
    elif operating_system == 'Win64' or operating_system == 'Windows':
        ac_dir = '%s/komodo/' % os.environ['APPDATA']
    if ticker == 'KMD':
        coin_config_file = str(ac_dir + '/komodo.conf')
    else:
        coin_config_file = str(ac_dir + '/' + ticker + '/' + ticker + '.conf')
    with open(coin_config_file, 'r') as f:
        for line in f:
            l = line.rstrip()
            if re.search('rpcuser', l):
                rpcuser = l.replace('rpcuser=', '')
            elif re.search('rpcpassword', l):
                rpcpassword = l.replace('rpcpassword=', '')
            elif re.search('rpcport', l):
                rpcport = l.replace('rpcport=', '')
    if len(rpcport) == 0:
        if ticker == 'KMD':
            rpcport = 7771
        else:
            #logger.info("rpcport not in conf file, exiting")
            #logger.info("check "+coin_config_file)
            exit(1)

    return Proxy("http://%s:%s@127.0.0.1:%d" % (rpcuser, rpcpassword, int(rpcport)))


def clean_ticker_data(ticker):
    kmd_dir = os.environ['HOME'] + '/.komodo/'
    dirs = [str(kmd_dir + ticker + '/')]
    if "KMD" in ticker:
        dirs = [str(kmd_dir + 'blocks/'), str(kmd_dir + 'chainstate/'), str(kmd_dir + 'database/')]
    try:
        for folder in dirs:
            shutil.rmtree(folder)
        return('cleaning ' + ticker + ' folder')
    except FileNotFoundError:
        pass


def clean_all_ticker_data():
    for ticker in ac_tickers[1:]:
        clean_ticker_data(ticker)
    return('cleaning assetchains folders')


def start_all_tickers():
    for ticker in ac_tickers[1:]:
        start_ticker(ticker)
    return('starting all tickers')


def stop_all_tickers():
    for ticker in ac_tickers[1:]:
        stop_ticker(ticker)
    return('stopping all tickers')


def download_binary(link):
    urllib.request.urlretrieve('{}'.format(link), 'newbinary.zip')


async def download_dragndrop():
    async with TelegramClient('ericswan', os.environ['API_ID'], os.environ['API_HASH']) as client:
        last_msg = await client.get_messages('komodo_sync_bot', 1)
        await client.download_media(last_msg, '/root/new-binary.zip')


async def setup_binary_dragndrop(link):
    if 'drag' in link:
        await download_dragndrop()
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

    return("changed to new binary")