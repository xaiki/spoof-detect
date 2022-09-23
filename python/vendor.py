#!/usr/bin/env python3
import csv
import concurrent.futures
import requests

from progress.bar import ChargingBar

from entity import Entity
from common import defaults,mkdir
import web

PARALLEL = 20

def do_screenshot(e: Entity):
    sfn = requests.post('http://puppet:8000/screenshot', json={
        'url': e.url,
        'id': e.id,
        'path': f'{defaults.SCREENSHOT_PATH}/{e.bco}.png',
        'logos': f'{defaults.LOGOS_DATA_PATH}/{e.bco}.png'
    })

ACTIONS = [web.get_cert, web.get_logos, do_screenshot]

def from_csv(fn: str, n_workers = PARALLEL):
    mkdir.make_dirs([defaults.SCREENSHOT_PATH])
    with open(fn, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        with concurrent.futures.ThreadPoolExecutor(max_workers = n_workers) as executor:
            futures = {}
            entities = [Entity.from_dict(d) for d in reader]
            bar = ChargingBar('vendor', max=len(entities*len(ACTIONS)))

            for e in entities:
                futures.update({executor.submit(f, e): (e, f) for f in ACTIONS})
            print('waiting for futures')

            for f in concurrent.futures.as_completed(futures):
                (e, a) = futures[f]
                try:
                    f.result()
                except Exception as err:
                    print(f'{a}({e.url}) generated an exception: {err}')
                bar.next()
            bar.finish()

#query_vendor_site(Entity.from_dict({'url':'http://www.bancoprovincia.com.ar', 'bco':'debug'}))
#exit()

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='extract certificates and screenshots websites')
    parser.add_argument('--csv', metavar='csv', type=str,
                        default=defaults.MAIN_CSV_PATH,
                        help='main database')
    parser.add_argument('--parallel', metavar='parallel', type=int,
                        default=PARALLEL,
                        help='number of concurrent jobs')

    args = parser.parse_args()
    from_csv(args.csv)
