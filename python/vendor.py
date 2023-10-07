#!/usr/bin/env python3
import concurrent.futures
import requests

from progress.bar import ChargingBar

from entity import Entity, read_entities
from common import defaults,mkdir
import web

PARALLEL = 20

def do_screenshot(e: Entity):
    assert(e.url)
    sfn = requests.post('http://puppet:8000/screenshot', json={
        'url': e.url,
        'id': e.id,
        'path': f'{defaults.SCREENSHOT_PATH}/{e.bco}.png',
        'logos': f'{defaults.LOGOS_DATA_PATH}/{e.bco}.png'
    })

def get_entity_logo(e: Entity):
    fn = f"{defaults.LOGOS_DATA_PATH}/{e.bco}.0.png"
    web.get_img_logo(e.logo, fn)

def from_csv(args):
    ACTIONS = []
    if (args.certs):
        ACTIONS.append(web.get_cert)
        mkdir.make_dirs([defaults.CERTS_PATH])
    if (args.logos):
        ACTIONS.append(web.get_logos)
        mkdir.make_dirs([defaults.LOGOS_DATA_PATH])
    if (args.screenshots):
        ACTIONS.append(do_screenshot)
        mkdir.make_dirs([defaults.SCREENSHOT_PATH])
    if (args.entity_logo):
        ACTIONS.append(get_entity_logo)
        mkdir.make_dirs([defaults.LOGOS_DATA_PATH])

    print(ACTIONS)
    with concurrent.futures.ThreadPoolExecutor(max_workers = args.parallel) as executor:
            futures = {}
            entities = read_entities(args.csv)
            qs = len(entities.keys())*len(ACTIONS)
            bar = ChargingBar(f'vendor ({qs} jobs)', max=qs)

            for e in entities.values():
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
    print("🌏 getting vendor data")
    parser = argparse.ArgumentParser(description='extract certificates and screenshots websites')
    parser.add_argument('--csv', metavar='csv', type=str,
                        default=defaults.MAIN_CSV_PATH,
                        help='main database')
    parser.add_argument('--parallel', metavar='parallel', type=int,
                        default=PARALLEL,
                        help='number of concurrent jobs')
    parser.add_argument('--logos', metavar='logos', type=bool,
                        action=argparse.BooleanOptionalAction,
                        default=True, help='try to get logos')
    parser.add_argument('--entity-logo', metavar='entity_logo', type=bool,
                        action=argparse.BooleanOptionalAction,
                        default=True, help='try to get logos form ENTITY')
    parser.add_argument('--certs', metavar='certs', type=bool,
                        action=argparse.BooleanOptionalAction,
                        default=True, help='try to get certs')
    parser.add_argument('--screenshots', metavar='screenshots', type=bool,
                        action=argparse.BooleanOptionalAction,
                        default=True, help='try to get screenshots')

    args = parser.parse_args()
    from_csv(args)
