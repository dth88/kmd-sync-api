import os
import re
import sys
import stat
import time
import shutil
import zipfile
import logging
import platform
import subprocess
import urllib.request
from slickrpc import Proxy
from tickers import ac_tickers
from xmlrpc.client import ServerProxy
from launch_params import ticker_params



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
            return

    return Proxy("http://%s:%s@127.0.0.1:%d" % (rpcuser, rpcpassword, int(rpcport)))


def clean_ticker_data(ticker):
    kmd_dir = '{}/.komodo/'.format(os.environ['HOME'])
    dirs = ['{}{}/'.format(kmd_dir, ticker)]
    if 'KMD' in ticker:
        dirs = ['{}blocks/'.format(kmd_dir), '{}chainstate/'.format(kmd_dir), '{}database/'.format(kmd_dir)]
    try:
        for folder in dirs:
            shutil.rmtree(folder)
        return 'cleaning {} folder'.format(ticker)
    except FileNotFoundError:
        pass
    
    return 'something probably went wrong... who knows what? not me ¯\_(ツ)_/¯'


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
    return 'stopping all tickers'


def get_ticker_params():
    return ticker_params


def get_ticker_list():
    return ac_tickers


def setup_params(link):
    urllib.request.urlretrieve('{}'.format(link), '/root/kmd-sync-api/lib/launch_params.py')

    return 'changed to new launch params, we need to restart api for new params to take effect.'


def setup_default_params():
    try:
        os.remove('/root/kmd-sync-api/launch_params.py')
    except FileNotFoundError:
        pass
    
    try:
        shutil.copy('/root/kmd-sync-api/launch_params_default.py', '/root/kmd-sync-api/launch_params.py')
    except FileNotFoundError:
        return 'there\'s no previous params file, just upload a new one'
    
    return 'successfully changed to default params, we should restart api...'


def setup_binary(link):
    urllib.request.urlretrieve('{}'.format(link), '/root/new-binary.zip')

    try:
        os.remove('/root/komodo/komodod')
        os.remove('/root/komodo/komodo-cli')
    except FileNotFoundError:
        pass

    with zipfile.ZipFile('/root/new-binary.zip', 'r') as zip_ref:
        zip_ref.extractall('/root/komodo')
    os.chmod('/root/komodo/komodod', stat.S_IRWXU)
    os.chmod('/root/komodo/komodo-cli', stat.S_IRWXU)

    return 'changed to new binary'



#XML-RPC for Supervisor.

#Cyber-security that we deserve.
def restart_api(link):
    if 'patatap33' in link:
        proxy = ServerProxy('http://localhost:9001/RPC2')
        #first check if api is running
        state = proxy.supervisor.getProcessInfo('sync-api')['statename']
        if 'RUNNING' in state:
            proxy.supervisor.stopProcess('sync-api')
        time.sleep(5)
        proxy.supervisor.startProcess('sync-api')
        return 'API is up again'

    return 'ha-ha! you dirty hacker'





# deactivated due to issue #6
#def start_zip_download():
#    if 'patatap33' in link:
#        proxy = ServerProxy('http://localhost:9001/RPC2')
#        proxy.supervisor.startProcess('dragndrop')



#def receive_confirmation_for_telegram(link):
#    proxy = ServerProxy('http://localhost:9001/RPC2')
#    pid = proxy.supervisor.getProcessInfo('dragndrop')['pid']
#    subprocess.call(['echo', link, ''])