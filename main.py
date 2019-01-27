import sys
import json
import time
import socket
import urllib.parse
import urllib.request
import signal
from mastodon import Mastodon
from config import config

# Ctrl-C でkill
signal.signal(signal.SIGINT, signal.SIG_DFL)

server_domain = config('domain')
access_token = config('access_token')
api_base_url = 'https://' + server_domain

mstdn = Mastodon(access_token=access_token, api_base_url=api_base_url)

def request_hashtag(url):
    timeout = 5
    request = urllib.request.Request(url)
    request.add_header("User-Agent", "Mozilla/5.0")
    try:
        response = urllib.request.urlopen(request, timeout=timeout)
    except:
        print('request error')
        return []

    try:
        jsn = json.loads(response.read())
    except:
        print('json decode error')
        return []
    return jsn

def get_peers():
    return mstdn.instance_peers()

limit = 20
def get_hashtag(domain, hashtag, max_id=None):
    hashtag_url = 'https://' + domain + '/api/v1/timelines/tag/' + urllib.parse.quote(hashtag) + '?local=1' + ('&max_id=' + urllib.parse.quote(max_id) if max_id else '') + '&limit=' + str(limit)
    toot_list = request_hashtag(hashtag_url)
    if len(toot_list) == limit:
        last_id = toot_list[len(toot_list) - 1]['id']
        _toot_list = get_hashtag(domain, hashtag, last_id)
        toot_list.extend(_toot_list)
    return toot_list

def get_search(url):
    return mstdn.search(url)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Useage: main.py <hashtag>')
        exit()

    hashtag = sys.argv[1]

    peers = get_peers()
    peers_num = str(len(peers))
    print(peers_num + ' peers')
    count = 1
    try:
        for peer in peers:
            print(peer + ' start (' + str(count) + '/' + peers_num  + ') -------------')
            count += 1
            toot_list = get_hashtag(peer, hashtag)
            print(str(len(toot_list)) + ' toots')
            for toot in toot_list:
                print(toot['url'])
                get_search(toot['url'])
    except KeyboardInterrupt:
        exit()
