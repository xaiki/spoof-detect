#!/usr/bin/env python
import requests

import concurrent.futures
from progress.bar import ChargingBar

from common import defaults,mkdir

PARALLEL = 20

def get(json):
    return requests.post('http://puppet:8000/screenshot',
                         json=json)

def download_all(feed, n_workers=PARALLEL, dest=defaults.FISH_PATH):
    mkdir.make_dirs([dest])
    res = requests.get(feed)
    with concurrent.futures.ThreadPoolExecutor(max_workers = n_workers) as executor:
        futures = {executor.submit(get, {
            'url': u,
            'path': f'''{dest}/{u
            .replace('http://', '')
            .replace('https://', '')
            .replace('/', '_')
            .replace('&', '_')
            .replace('=', '_')
            .replace('?', '_')
            }.png'''
        }): u for u in res.text.split('\n')}
        print(f'will get {len(futures)} domains')
        bar = ChargingBar('Processing', max=len(futures), suffix='%(index)d/%(max)d')
        for f in concurrent.futures.as_completed(futures):
            url = futures[f]
            try:
                ret = f.result()
            except:
                print(f'{url} generated an exception')
            else:
                print(ret)
            bar.next()
        bar.finish()

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='screenshot openfish open list')
    parser.add_argument('--parallel', metavar='parallel', type=int,
                        default=PARALLEL,
                        help='number of concurrent jobs')
    parser.add_argument('--feed', metavar='feed', type=str,
                        default='https://raw.githubusercontent.com/mitchellkrogza/Phishing.Database/master/phishing-links-ACTIVE-TODAY.txt',
                        help='''
                        fishing feed to use we recomend
                         - https://github.com/mitchellkrogza/Phishing.Database/blob/master/phishing-links-ACTIVE-TODAY.txt
                        - https://openphish.com/feed.txt
                        ''')
    args = parser.parse_args()
    download_all(args.feed, n_workers=args.parallel)
