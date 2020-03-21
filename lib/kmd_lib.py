from slickrpc import Proxy
import time
import subprocess
import platform
import pycurl
import os
import re
import sys
import zipfile
import json
import shutil
import logging
import urllib.request
#from launch_params import ticker_params
#from tickers import ac_tickers


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
    ac_dir = str(kmd_dir + ticker + '/')
    try:
        shutil.rmtree(ac_dir)
        return('cleaning ' + ticker + ' folder')
    except FileNotFoundError:
        pass


def clean_all_ticker_data():
    for ticker in ac_tickers:
        clean_ticker_data(ticker)
    return('cleaning assetchains folders')


def start_all_tickers():
    for ticker in ac_tickers:
        start_ticker(ticker)
    return('starting all tickers')


def stop_all_tickers():
    for ticker in ac_tickers:
        stop_ticker(ticker)
    return('stopping all tickers')


def setup_binary(link):
    urllib.request.urlretrieve('{}'.format(link), 'newbinary.zip')
    os.remove('/root/komodo/komodod')
    os.remove('/root/komodo/komodo-cli')
    with zipfile.ZipFile('newbinary.zip', 'r') as zip_ref:
        zip_ref.extractall('/root/komodo')
    return({"changed to new binary"})
    





#if __name__ == "__main__":
    #ticker = "AXO"
    #start_ticker(ticker)
    #for ticker in ac_tickers:
    #get_sync_stats(ticker)
    #stop_all_tickers()
    #stop_ticker(ticker)
    #clean_ticker_data(ticker)
    #clean_all_ticker_data()






ac_tickers = ["REVS", "SUPERNET", "DEX",
              "PANGEA", "JUMBLR", "BET",
              "CRYPTO", "HODL", "MSHARK",
              "BOTS", "MGW", "COQUICASH", 
              "KV", "MESH", "AXO", "ETOMIC",
              "BTCH", "NINJA", "OOT", "ZILLA",
              "RFOX", "SEC", "CCL", "PIRATE",
              "PGT", "KSB", "OUR", "ILN",
              "RICK", "MORTY", "KOIN",
              "ZEXO", "K64", "THC", "WLC21"]





ticker_params = {
    "ILN" : "komodod -ac_name=ILN -ac_supply=10000000000 -ac_cc=2 -addressindex=1 -spentindex=1 -addnode=51.75.122.83 -deamon &>/dev/null",
    "RICK" : "komodod -ac_name=RICK -ac_supply=90000000000 -ac_reward=100000000 -ac_cc=3 -ac_staked=10 -addnode=95.217.44.58 -addnode=138.201.136.145 -deamon &>/dev/null",
    "MORTY" : "komodod -ac_name=MORTY -ac_supply=90000000000 -ac_reward=100000000 -ac_cc=3 -ac_staked=10 -addnode=95.217.44.58 -addnode=138.201.136.145 -deamon &>/dev/null",
    "REVS" : "komodod -ac_name=REVS -ac_supply=1300000 -addnode=95.213.238.98 -deamon &>/dev/null",
    "SUPERNET" : "komodod -ac_name=SUPERNET -ac_supply=816061 -addnode=95.213.238.98 -deamon &>/dev/null",
    "DEX" : "komodod -ac_name=DEX -ac_supply=999999 -addnode=95.213.238.98 -deamon &>/dev/null",
    "PANGEA" : "komodod -ac_name=PANGEA -ac_supply=999999 -addnode=95.213.238.98 -deamon &>/dev/null",
    "JUMBLR" : "komodod -ac_name=JUMBLR -ac_supply=999999 -addnode=95.213.238.98 -deamon &>/dev/null",
    "BET" : "komodod -ac_name=BET -ac_supply=999999 -addnode=95.213.238.98 -deamon &>/dev/null",
    "CRYPTO" : "komodod -ac_name=CRYPTO -ac_supply=999999 -addnode=95.213.238.98 -deamon &>/dev/null",
    "HODL" : "komodod -ac_name=HODL -ac_supply=9999999 -addnode=95.213.238.98 -deamon &>/dev/null",
    "MSHARK" : "komodod -ac_name=MSHARK -ac_supply=1400000 -addnode=95.213.238.98 -deamon &>/dev/null",
    "BOTS" : "komodod -ac_name=BOTS -ac_supply=999999 -addnode=95.213.238.98 -deamon &>/dev/null",
    "MGW" : "komodod -ac_name=MGW -ac_supply=999999 -addnode=95.213.238.98 -deamon &>/dev/null",
    "COQUICASH" : "komodod -ac_name=COQUICASH -ac_supply=72000000 -ac_reward=7200000000 -ac_staked=50 -ac_halving=420000 -ac_cc=2 -ac_ccenable=227,235,236,241 -addnode=78.47.108.168 -deamon &>/dev/null",
    "WLC" : "komodod -ac_name=WLC -ac_supply=210000000 -addnode=95.213.238.98 -deamon &>/dev/null",
    "KV" : "komodod -ac_name=KV -ac_supply=1000000 -addnode=95.213.238.98 -deamon &>/dev/null",
    "MESH" : "komodod -ac_name=MESH -ac_supply=1000007 -addnode=95.213.238.98 -deamon &>/dev/null",
    "AXO" : "komodod -ac_name=AXO -ac_supply=200000000 -ac_ccactivate=130000 -addnode=95.213.238.98 -deamon &>/dev/null",
    "ETOMIC" : "komodod -ac_name=ETOMIC -ac_supply=100000000 -addnode=95.213.238.98 -deamon &>/dev/null",
    "BTCH" : "komodod -ac_name=BTCH -ac_supply=20998641 -addnode=95.213.238.98 -deamon &>/dev/null",
    "NINJA" : "komodod -ac_name=NINJA -ac_supply=100000000 -addnode=95.213.238.98 -deamon &>/dev/null",
    "OOT" : "komodod -ac_name=OOT -ac_supply=216000000 -ac_sapling=5000000 -addnode=95.213.238.98 -deamon &>/dev/null",
    "ZILLA" : "komodod -ac_name=ZILLA -ac_supply=11000000 -ac_sapling=5000000 -addnode=51.68.215.104 -deamon &>/dev/null",
    "RFOX" : "komodod -ac_name=RFOX -ac_supply=1000000000 -ac_reward=100000000 -addnode=95.213.238.98 -deamon &>/dev/null",
    "SEC" : "komodod -ac_name=SEC -ac_cc=333 -ac_supply=1000000000 -addnode=185.148.145.43 -deamon &>/dev/null",
    "CCL" : "komodod -ac_name=CCL -ac_supply=200000000 -ac_end=1 -ac_cc=2 -addressindex=1 -spentindex=1 -addnode=142.93.136.89 -addnode=195.201.22.89 -deamon &>/dev/null",
    "PIRATE" : "komodod -ac_name=PIRATE -ac_supply=0 -ac_reward=25600000000 -ac_halving=77777 -ac_private=1 -addnode=178.63.77.56 -deamon &>/dev/null",
    "PGT" : "komodod -ac_name=PGT -ac_supply=10000000 -ac_end=1 -addnode=190.114.254.104 -deamon &>/dev/null",
    "KSB" : "komodod -ac_name=KSB -ac_supply=1000000000 -ac_end=1 -ac_public=1 -addnode=37.187.225.231 -deamon &>/dev/null",
    "OUR" : "komodod -ac_name=OUR -ac_reward=1478310502 -ac_halving=525600 -ac_cc=42 -ac_supply=100000000 -ac_perc=77700 -ac_staked=93 -ac_pubkey=02652a3f3e00b3a1875a918314f0bac838d6dd189a346fa623f5efe9541ac0b98c -ac_public=1 -addnode=51.255.195.65 -addnode=217.182.129.38 -addnode=37.187.225.231 -deamon &>/dev/null",
    "KOIN" : "komodod -ac_name=KOIN -ac_supply=125000000 -addnode=3.0.32.10 -deamon &>/dev/null",
    "ZEXO" : "komodod -ac_name=ZEXO -ac_supply=100000000 -ac_reward=1478310502 -ac_halving=525600 -ac_cc=42 -ac_ccenable=236 -ac_perc=77700 -ac_staked=93 -ac_pubkey=02713bd85e054db923694b6b7a85306264edf4d6bd6d331814f2b40af444b3ebbc -ac_public=1 -addnode=80.240.17.222 -deamon &>/dev/null",
    "K64" : "komodod -ac_name=K64 -ac_supply=64000777 -ac_reward=0 -ac_staked=10 -addnode=18.197.20.211 -deamon &>/dev/null",
    "THC" : "komodod -ac_name=THC -ac_supply=251253103 -ac_reward=360000000,300000000,240000000,180000000,150000000,90000000,0 -ac_staked=100 -ac_eras=7 -ac_end=500001,1000001,1500001,2000001,2500001,4500001,0 -ac_perc=233333333 -ac_cc=2 -ac_ccenable=229,236,240 -ac_script=2ea22c8020987fad30df055db6fd922c3a57e55d76601229ed3da3b31340112e773df3d0d28103120c008203000401ccb8 -ac_founders=150 -ac_cbmaturity=1 -ac_sapling=1 -addnode=157.230.45.184 -addnode=165.22.52.123 -earlytxid=7e4a76259e99c9379551389e9f757fc5f46c33ae922a8644dc2b187af2a6adc1 -deamon &>/dev/null",
    "WLC21" : "komodod -ac_name=WLC21 -ac_supply=21000000 -ac_reward=190258751 -ac_staked=90 -ac_public=1 -addnode=37.187.225.231 -addnode=51.38.38.134 -deamon &>/dev/null",
}

#~/hush3/src/komodod -ac_name=HUSH3 -ac_sapling=1 -ac_reward=0,1125000000,562500000 -ac_halving=129,340000,840000 -ac_end=128,340000,5422111 -ac_eras=3 -ac_blocktime=150 -ac_cc=2 -ac_ccenable=228,234,235,236,241 -ac_founders=1 -ac_supply=6178674 -ac_perc=11111111 -clientname=GoldenSandtrout -addnode=188.165.212.101 -addnode=136.243.227.142 -addnode=5.9.224.250 -ac_cclib=hush3 -ac_script=76a9145eb10cf64f2bab1b457f1f25e658526155928fac88ac -deamon &>/dev/null
#~/VerusCoin/src/verusd -deamon &>/dev/null





notary_pubkeys =  {
    "madmax_NA": "0237e0d3268cebfa235958808db1efc20cc43b31100813b1f3e15cc5aa647ad2c3", 
    "alright_AR": "020566fe2fb3874258b2d3cf1809a5d650e0edc7ba746fa5eec72750c5188c9cc9",
    "strob_NA": "0206f7a2e972d9dfef1c424c731503a0a27de1ba7a15a91a362dc7ec0d0fb47685",
    "hunter_EU": "0378224b4e9d8a0083ce36f2963ec0a4e231ec06b0c780de108e37f41181a89f6a", 
    "phm87_SH": "021773a38db1bc3ede7f28142f901a161c7b7737875edbb40082a201c55dcf0add",
    "chainmakers_NA": "02285d813c30c0bf7eefdab1ff0a8ad08a07a0d26d8b95b3943ce814ac8e24d885",
    "indenodes_EU": "0221387ff95c44cb52b86552e3ec118a3c311ca65b75bf807c6c07eaeb1be8303c",
    "blackjok3r_SH": "021eac26dbad256cbb6f74d41b10763183ee07fb609dbd03480dd50634170547cc",
    "chainmakers_EU": "03fdf5a3fce8db7dee89724e706059c32e5aa3f233a6b6cc256fea337f05e3dbf7",
    "titomane_AR": "023e3aa9834c46971ff3e7cb86a200ec9c8074a9566a3ea85d400d5739662ee989",
    "fullmoon_SH": "023b7252968ea8a955cd63b9e57dee45a74f2d7ba23b4e0595572138ad1fb42d21", 
    "indenodes_NA": "02698c6f1c9e43b66e82dbb163e8df0e5a2f62f3a7a882ca387d82f86e0b3fa988",
    "chmex_EU": "0281304ebbcc39e4f09fda85f4232dd8dacd668e20e5fc11fba6b985186c90086e",
    "metaphilibert_SH": "0284af1a5ef01503e6316a2ca4abf8423a794e9fc17ac6846f042b6f4adedc3309",
    "ca333_DEV": "02856843af2d9457b5b1c907068bef6077ea0904cc8bd4df1ced013f64bf267958",
    "cipi_NA": "02858904a2a1a0b44df4c937b65ee1f5b66186ab87a751858cf270dee1d5031f18",
    "pungocloud_SH": "024dfc76fa1f19b892be9d06e985d0c411e60dbbeb36bd100af9892a39555018f6",
    "voskcoin_EU": "034190b1c062a04124ad15b0fa56dfdf34aa06c164c7163b6aec0d654e5f118afb",
    "decker_DEV": "028eea44a09674dda00d88ffd199a09c9b75ba9782382cc8f1e97c0fd565fe5707",
    "cryptoeconomy_EU": "0290ab4937e85246e048552df3e9a66cba2c1602db76e03763e16c671e750145d1",
    "etszombi_EU": "0293ea48d8841af7a419a24d9da11c34b39127ef041f847651bae6ab14dcd1f6b4",  
    "karasugoi_NA": "02a348b03b9c1a8eac1b56f85c402b041c9bce918833f2ea16d13452309052a982",
    "pirate_AR": "03e29c90354815a750db8ea9cb3c1b9550911bb205f83d0355a061ac47c4cf2fde",
    "metaphilibert_AR": "02adad675fae12b25fdd0f57250b0caf7f795c43f346153a31fe3e72e7db1d6ac6",
    "zatjum_SH": "02d6b0c89cacd58a0af038139a9a90c9e02cd1e33803a1f15fceabea1f7e9c263a",
    "madmax_AR": "03c5941fe49d673c094bc8e9bb1a95766b4670c88be76d576e915daf2c30a454d3",
    "lukechilds_NA": "03f1051e62c2d280212481c62fe52aab0a5b23c95de5b8e9ad5f80d8af4277a64b",
    "cipi_AR": "02c4f89a5b382750836cb787880d30e23502265054e1c327a5bfce67116d757ce8",
    "tonyl_AR": "02cc8bc862f2b65ad4f99d5f68d3011c138bf517acdc8d4261166b0be8f64189e1",
    "infotech_DEV": "0345ad4ab5254782479f6322c369cec77a7535d2f2162d103d666917d5e4f30c4c",
    "fullmoon_NA": "032c716701fe3a6a3f90a97b9d874a9d6eedb066419209eed7060b0cc6b710c60b",  
    "etszombi_AR": "02e55e104aa94f70cde68165d7df3e162d4410c76afd4643b161dea044aa6d06ce",
    "node-9_EU": "0372e5b51e86e2392bb15039bac0c8f975b852b45028a5e43b324c294e9f12e411",
    "phba2061_EU": "03f6bd15dba7e986f0c976ea19d8a9093cb7c989d499f1708a0386c5c5659e6c4e",
    "indenodes_AR": "02ec0fa5a40f47fd4a38ea5c89e375ad0b6ddf4807c99733c9c3dc15fb978ee147",
    "and1-89_EU": "02736cbf8d7b50835afd50a319f162dd4beffe65f2b1dc6b90e64b32c8e7849ddd",
    "komodopioneers_SH": "032a238a5747777da7e819cfa3c859f3677a2daf14e4dce50916fc65d00ad9c52a",
    "komodopioneers_EU": "036d02425916444fff8cc7203fcbfc155c956dda5ceb647505836bef59885b6866",
    "d0ct0r_NA": "0303725d8525b6f969122faf04152653eb4bf34e10de92182263321769c334bf58",
    "kolo_DEV": "02849e12199dcc27ba09c3902686d2ad0adcbfcee9d67520e9abbdda045ba83227",
    "peer2cloud_AR": "02acc001fe1fe8fd68685ba26c0bc245924cb592e10cec71e9917df98b0e9d7c37", 
    "webworker01_SH": "031e50ba6de3c16f99d414bb89866e578d963a54bde7916c810608966fb5700776",
    "webworker01_NA": "032735e9cad1bb00eaababfa6d27864fa4c1db0300c85e01e52176be2ca6a243ce",
    "pbca26_NA": "03a97606153d52338bcffd1bf19bb69ef8ce5a7cbdc2dbc3ff4f89d91ea6bbb4dc",
    "indenodes_SH": "0334e6e1ec8285c4b85bd6dae67e17d67d1f20e7328efad17ce6fd24ae97cdd65e",
    "pirate_NA": "0255e32d8a56671dee8aa7f717debb00efa7f0086ee802de0692f2d67ee3ee06ee",
    "lukechilds_AR": "025c6a73ff6d750b9ddf6755b390948cffdd00f344a639472d398dd5c6b4735d23",
    "dragonhound_NA": "0224a9d951d3a06d8e941cc7362b788bb1237bb0d56cc313e797eb027f37c2d375",
    "fullmoon_AR": "03da64dd7cd0db4c123c2f79d548a96095a5a103e5b9d956e9832865818ffa7872",
    "chainzilla_SH": "0360804b8817fd25ded6e9c0b50e3b0782ac666545b5416644198e18bc3903d9f9",
    "titomane_EU": "03772ac0aad6b0e9feec5e591bff5de6775d6132e888633e73d3ba896bdd8e0afb", 
    "jeezy_EU": "037f182facbad35684a6e960699f5da4ba89e99f0d0d62a87e8400dd086c8e5dd7",
    "titomane_SH": "03850fdddf2413b51790daf51dd30823addb37313c8854b508ea6228205047ef9b",
    "alien_AR": "03911a60395801082194b6834244fa78a3c30ff3e888667498e157b4aa80b0a65f",
    "pirate_EU": "03fff24efd5648870a23badf46e26510e96d9e79ce281b27cfe963993039dd1351",
    "thegaltmines_NA": "02db1a16c7043f45d6033ccfbd0a51c2d789b32db428902f98b9e155cf0d7910ed",
    "computergenie_NA": "03a78ae070a5e9e935112cf7ea8293f18950f1011694ea0260799e8762c8a6f0a4",
    "nutellalicka_SH": "02f7d90d0510c598ce45915e6372a9cd0ba72664cb65ce231f25d526fc3c5479fc",
    "chainstrike_SH": "03b806be3bf7a1f2f6290ec5c1ea7d3ea57774dcfcf2129a82b2569e585100e1cb",
    "hunter_SH": "02407db70ad30ce4dfaee8b4ae35fae88390cad2b0ba0373fdd6231967537ccfdf", 
    "alien_EU": "03bb749e337b9074465fa28e757b5aa92cb1f0fea1a39589bca91a602834d443cd", 
    "gt_AR": "0348430538a4944d3162bb4749d8c5ed51299c2434f3ee69c11a1f7815b3f46135",
    "patchkez_SH": "03f45e9beb5c4cd46525db8195eb05c1db84ae7ef3603566b3d775770eba3b96ee",
    "decker_AR": "03ffdf1a116300a78729608d9930742cd349f11a9d64fcc336b8f18592dd9c91bc"
}

validator_pubkeys =  {
    "SYNC_24": "02317cf599fb502d96ac36fa239f9cf308825738fbbe0d3237f783f895ab4e5fee", 
}