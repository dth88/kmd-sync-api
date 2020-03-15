from slickrpc import Proxy
import time
import subprocess
import platform
import os
import re
import sys
import json
import math
import shutil
import oraclelib
import logging
from tickers import ac_tickers
from pubkeys import validator_pubkeys, notary_pubkeys





def start_ticker(ticker):
    ticker_launch = ''
    with open(sys.path[0] + '/assetchains.old') as f:
        lines = f.readlines()
    #remove \n
    lines = [x.strip() for x in lines]
    #get the ticker_launch command
    for line in lines:
        if ticker in line:
            ticker_launch = line.split(" ")[:-1]

    if ticker_launch:
        ticker_output = open(sys.path[0]+'/ticker_output/'+ticker+"_output.log",'w+')
        subprocess.Popen(ticker_launch, stdout=ticker_output, stderr=ticker_output, universal_newlines=True)
        print('success')


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



# Clean ticker data folder
def clean_chain_data(ticker):
    stop_result = globals()["assetchain_proxy_{}".format(ticker)].stop()
    #logger.info(ticker + " stopped!")
    time.sleep(30)
    ac_dir = str(kmd_dir + '/' + ticker + '/')
    shutil.rmtree(ac_dir)
    #logger.info(ac_dir+" deleted")






if __name__ == "__main__":
    ticker = 'AXO'
    start_ticker(ticker)
