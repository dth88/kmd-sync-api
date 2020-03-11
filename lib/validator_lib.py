from slickrpc import Proxy
import time
import subprocess
import platform
#import requests
import os
import re
import sys
import json
import math
import shutil
from . import oraclelib
import logging
from tickers import ac_tickers
from pubkeys import validator_pubkeys, notary_pubkey


def colorize(string, color):
    colors = {
        'blue': '\033[94m',
        'cyan': '\033[96m',
        'yellow': '\033[93m',
        'magenta': '\033[95m',
        'green': '\033[92m',
        'red': '\033[91m',
        'black': '\033[30m',
        'grey': '\033[90m',
        'pink': '\033[95m'
    }
    if color not in colors:
        return string
    else:
        return colors[color] + str(string) + '\033[0m'


# Set RPC proxy
def def_credentials(chain):
    rpcport = ''
    ac_dir = ''
    operating_system = platform.system()
    if operating_system == 'Darwin':
        ac_dir = os.environ['HOME'] + '/Library/Application Support/Komodo'
    elif operating_system == 'Linux':
        ac_dir = os.environ['HOME'] + '/.komodo'
    elif operating_system == 'Win64' or operating_system == 'Windows':
        ac_dir = '%s/komodo/' % os.environ['APPDATA']
    if chain == 'KMD':
        coin_config_file = str(ac_dir + '/komodo.conf')
    else:
        coin_config_file = str(ac_dir + '/' + chain + '/' + chain + '.conf')
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
        if chain == 'KMD':
            rpcport = 7771
        else:
            logger.info("rpcport not in conf file, exiting")
            logger.info("check "+coin_config_file)
            exit(1)

    return Proxy("http://%s:%s@127.0.0.1:%d" % (rpcuser, rpcpassword, int(rpcport)))


# sync chains
def sim_chains_start_and_sync():
    launch_stats_oracle(oracle_ticker)
    stats_orcl_info = get_node_oracle(oracle_ticker)
    # start with creating a proxy for each assetchain
    for ticker in ac_tickers:
        # 30 sec wait during restart for getting rpc credentials
        # 30 sec * approx. 40 chains = 20 min to start
        restart_ticker(ticker)
        if ticker not in sync_status:
            sync_status.update({ticker:{}})
    while True:
        update_oracle = False
        for ticker in ac_tickers:
            try:
                ticker_rpc = globals()["assetchain_proxy_{}".format(ticker)]
                ticker_timestamp = int(time.time())
                sync_status[ticker].update({"last_updated":ticker_timestamp})
                get_info_result = ticker_rpc.getinfo()
                sync_status[ticker].update({
                        "blocks":get_info_result["blocks"],
                        "longestchain":get_info_result["longestchain"]
                    })
                if get_info_result["blocks"] < get_info_result["longestchain"]:
                    logger.info(colorize("Chain " + ticker + " is NOT synced."
                                 + " Blocks: " + str(get_info_result["blocks"]) 
                                 + " Longestchain: " + str(get_info_result["longestchain"]),
                                   "red"))
                else:
                    update_oracle = True
                    logger.info(colorize("Chain " + ticker + " is synced."
                                + " Blocks: " + str(get_info_result["blocks"])
                                + " Longestchain: " + str(get_info_result["longestchain"])
                                + " Latest Blockhash: " + ticker_rpc.getblock(str(get_info_result["blocks"]))["hash"],
                                  "green"))
                    latest_block_fifth = int(math.floor(get_info_result["longestchain"]/5)*5)
                    latest_block_fifth_hash = ticker_rpc.getblock(str(latest_block_fifth))["hash"]
                    sync_status[ticker].update({
                            "last_longesthash":latest_block_fifth_hash,
                            "last_longestchain":latest_block_fifth
                        })
                    # save timestamped file for ticker if synced
                    filename = ticker+'_sync_'+str(ticker_timestamp)+'.json'
                    with open(sys.path[0]+'/chains_status/' + filename, 'w+') as fp:
                        json.dump(sync_status[ticker], fp, indent=4)
                    logger.info("Saved "+ticker+" sync data to " + filename)
                    clean_chain_data(ticker)
                    restart_ticker(ticker)
            except Exception as e:
                logger.info(e)
        # save global state file
        sync_status.update({"last_updated":ticker_timestamp})
        with open(sys.path[0]+'/chains_status/global_sync.json', 'w+') as fp:
            json.dump(sync_status, fp, indent=4)
        logger.info("Saved global state data to global_sync.json")
        if update_oracle:
            oracle_rpc = globals()["assetchain_proxy_{}".format(oracle_ticker)]
            oraclelib.write2oracle(oracle_rpc, stats_orcl_info['txid'], str(sync_status))
        # loop again in 15 min
        time.sleep(900)
    return True


# Clean ticker data folder
def clean_chain_data(ticker):
    stop_result = globals()["assetchain_proxy_{}".format(ticker)].stop()
    logger.info(ticker + " stopped!")
    time.sleep(30)
    ac_dir = str(kmd_dir + '/' + ticker + '/')
    shutil.rmtree(ac_dir)
    logger.info(ac_dir+" deleted")


def restart_ticker(ticker):
    ticker_launch = ''
    with open(sys.path[0]+'/assetchains.old') as fp:
        line = fp.readline()
        while line:
            if line.find(ticker) > 0:
                ticker_launch = line.strip().split(" ")[:-1]
                break
            line = fp.readline()
    if ticker_launch != '':
        ticker_output = open(sys.path[0]+'/ticker_output/'+ticker+"_output.log",'w+')
        logger.info("starting "+ticker)
        subprocess.Popen(ticker_launch, stdout=ticker_output, stderr=ticker_output, universal_newlines=True)
        time.sleep(30)
        globals()["assetchain_proxy_{}".format(ticker)] = def_credentials(ticker)


def launch_stats_oracle(oracle_ticker):
    ticker_output = open(sys.path[0]+'/ticker_output/'+oracle_ticker+"_output.log",'w+')
    logger.info("starting "+oracle_ticker)
    subprocess.Popen(oracle_launch, stdout=ticker_output, stderr=ticker_output, universal_newlines=True)
    time.sleep(15)
    globals()["assetchain_proxy_{}".format(oracle_ticker)] = def_credentials(oracle_ticker)


def get_node_oracle(oracle_ticker):
    if not os.path.isfile(sys.path[0]+'/config/oracle.json'):
        local_oracle_params = {}
        orcl_info = create_node_oracle(oracle_ticker)
        with open(sys.path[0]+'/config/oracle.json', 'w+') as fp:
            json.dump(orcl_info, fp, indent=4)
        logger.info("Saved oracle info data to "+sys.path[0]+"/config/oracle.json")
    with open(sys.path[0]+'/config/oracle.json', 'r') as fp:
        orcl_info = json.loads(fp.read())
    return orcl_info


def get_local_node_name():
    node_name = ''
    logger.info("Checking if ["+local_pubkey+"] in notary_pubkeys")
    for node in list(notary_pubkeys.keys()):
        if notary_pubkeys[node] == local_pubkey:
            node_name = node
            break
    if node_name == '':
        logger.info("Checking if ["+local_pubkey+"] in validator_pubkeys")
        for node in list(validator_pubkeys.keys()):
            if validator_pubkeys[node] == local_pubkey:
                node_name = node
                break
    return node_name


def create_node_oracle(oracle_ticker):
    node_name = get_local_node_name()
    if node_name != '':
        logger.info("Welcome "+node_name+"!")
        logger.info("Creating your oracle...")
        try:
            oracle_ticker_rpc = globals()["assetchain_proxy_{}".format(oracle_ticker)]
            get_info = oracle_ticker_rpc.getinfo()
            get_info_pubkey = get_info['pubkey']
            get_info_balance = get_info['balance']
            if get_info_pubkey == local_pubkey:
                if get_info_balance < 10:
                    logger.warning("Oracle creation aborted: "+oracle_ticker+" has insufficient funds (10005 required)")
                    logger.warning("Ask @smk762#7640 on Discord to send some.")
                    sys.exit()
                else:
                    oracle_txid = oraclelib.create_oracle(oracle_ticker, oracle_ticker_rpc,
                                                          node_name+"_blockhash_stats",
                                                          node_name+" blockhash stats", 'S', 0.001)
                    orcl_info = oracle_ticker_rpc.oraclesinfo(oracle_txid)
                    return orcl_info
            else:
                logger.warning("Oracle creation aborted: "+oracle_ticker+" not launched with pubkey ["+local_pubkey+"]")
                sys.exit()
        except Exception as e:
            logger.warning("Oracle creation failed: "+str(e))
            logger.warning("Did you launch "+oracle_ticker+" with pubkey ["+local_pubkey+"]?")
            sys.exit()
    else:
        logger.warning("Oracle creation aborted: pubkey ["+local_pubkey+"] not recognised in notary / validator pubkeys dicts.")
        logger.warning("Submit a Pull Request to add it...")
        sys.exit()


def get_sync_node_data():
    # Get sync node's latest hashes
    sync_data = {}
    rpc_proxy = def_credentials(oracle_ticker)
    oracle_txid = 'b4fef41d11b6aab51b77945d3df7cdaeb9148dfa4df1e56d2057ec0d4cdab8c4'
    baton = 'RSGFUXm7cYe4h3u312qmtVnyHJnVqpS1EJ'
    samples = rpc_proxy.oraclessamples(oracle_txid, baton, str(1))
    if samples['result'] == 'success':
        if len(samples['samples'][0]['data']) > 0:
            sync_data = json.loads(samples['samples'][0]['data'][0].replace("\'", "\""))
    return sync_data


def report_nn_tip_hashes():
    launch_stats_oracle(oracle_ticker)
    stats_orcl_info = get_node_oracle(oracle_ticker)
    # start with creating a proxy for each assetchain
    for ticker in ac_tickers:
        globals()["assetchain_proxy_{}".format(ticker)] = def_credentials(ticker)
        sync_status.update({ticker:{}})
    this_node_update_time = 0
    while True:
        # read sync node data
        sync_data = get_sync_node_data()
        sync_node_update_time = sync_data['last_updated']
        for ticker in ac_tickers:
            try:
                # compare sync node hash to local hash
                sync_ticker_data = sync_data[ticker]
                sync_ticker_block = sync_ticker_data['last_longestchain']
                sync_ticker_hash = sync_ticker_data['last_longesthash']
                ticker_rpc = globals()["assetchain_proxy_{}".format(ticker)]
                ticker_timestamp = int(time.time())
                sync_status[ticker].update({"last_updated":ticker_timestamp})
                get_info_result = ticker_rpc.getinfo()
                sync_status[ticker].update({
                        "blocks":get_info_result["blocks"],
                        "longestchain":get_info_result["longestchain"]
                    })
                if get_info_result["blocks"] < get_info_result["longestchain"]:
                    logger.info(colorize("Chain " + ticker + " is NOT synced."
                                + " Blocks: " + str(get_info_result["blocks"])
                                + " Longestchain: "+ str(get_info_result["longestchain"]),
                                  "red"))
                else:
                    logger.info(colorize("Chain " + ticker + " is synced."
                                + " Blocks: " + str(get_info_result["blocks"])
                                + " Longestchain: " + str(get_info_result["longestchain"])
                                + " Latest Blockhash: " + ticker_rpc.getblock(str(get_info_result["blocks"]))["hash"],
                                  "green"))
                    ticker_sync_block_hash = ticker_rpc.getblock(str(sync_ticker_block))["hash"]
                    sync_status[ticker].update({
                            "last_longesthash":ticker_sync_block_hash,
                            "last_longestchain":sync_ticker_block
                        })
                if ticker_sync_block_hash == sync_ticker_hash:
                    # all good
                    logger.info(colorize("Sync node comparison for "+ticker+" block ["+str(sync_ticker_block)+"] MATCHING! ", 'green'))
                    logger.info(colorize("Hash: ["+sync_ticker_hash+"]", 'green'))
                else:
                    # possible fork
                    logger.warning(colorize("Sync node comparison for "+ticker+" block ["+str(sync_ticker_block)+"] FAILED! ", "red"))
                    logger.warning(colorize("Sync node hash: ["+sync_ticker_hash+"]", 'red'))
                    logger.warning(colorize("Notary node hash: ["+ticker_sync_block_hash+"]", 'red'))
            except Exception as e:
                logger.warning(ticker+" error: "+str(e))
                logger.info(ticker+" sync data: "+str(sync_ticker_data))
            time.sleep(1)
        # save global state file
        sync_status.update({"last_updated":ticker_timestamp})
        with open(sys.path[0]+'/chains_status/global_sync.json', 'w+') as fp:
            json.dump(sync_status, fp, indent=4)
        logger.info("Saved global state data to global_sync.json")
        # write notary hashes to oracle
        if this_node_update_time < sync_node_update_time:
            this_node_update_time = int(time.time())
            oracle_rpc = globals()["assetchain_proxy_{}".format(oracle_ticker)]
            oraclelib.write2oracle(oracle_rpc, stats_orcl_info['txid'], str(sync_status))
            logger.info("Global sync_status data written to oracle ["+stats_orcl_info['txid']+"]")
        else:
            logger.info("Global sync_status data not written to oracle, waiting for sync node update.")
            logger.info("sync_node_update_time: "+str(sync_node_update_time))
            logger.info("this_node_update_time: "+str(this_node_update_time))
        time.sleep(600)
    return True

