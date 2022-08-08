#!/usr/bin/env python3
import pathlib
import ssl
import shutil
import csv
import concurrent.futures
import requests
from bs4 import BeautifulSoup
from progress.bar import ChargingBar

from entity import Entity
from common import selectors
import screenshot

def write_cert(e: Entity):
    ssl_url = e.url.split("/")[2]
    try:
        cert = ssl.get_server_certificate((ssl_url, 443), ca_certs=None)
        with open(f"{e.DATA_PATH}/cert", 'w') as f:
            f.write(cert)
    except Exception as err:
        with open(f"{e.DATA_PATH}/error.log", 'w+') as f:
            f.write(str(err))

def get_logos(e: Entity, page):
    soup = BeautifulSoup(page.content, "html.parser")
    logos = soup.select(selectors.logo)

    i = 0
    lfn = []
    for l in logos:
        src = l.attrs['src']
        ext = src.split('.')[-1].split('/')[-1]
        try:
            res = requests.get(src, stream=True)
        except Exception:
            res = requests.get(f"{e.url}/{src}")

        fn = f"{e.DATA_PATH}/{i}.{ext}"
        with open(fn, "wb") as f:
            shutil.copyfileobj(res.raw, f)
        lfn.append(fn)
        i+=1

def query_vendor_site(e: Entity):
    pathlib.Path(f"./data/{e.bco}").mkdir(parents=True, exist_ok=True)

    try:
        page = requests.get(e.url)
    except Exception:
        e.url = e.url.replace('http', 'https')
        page = requests.get(e.url)

    write_cert(e)
    get_logos(e, page)
    screenshot.sc_entity(e)
    return (fn, lfn)

def from_csv(fn):
    with open(fn, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        with concurrent.futures.ThreadPoolExecutor(max_workers = 5) as executor:
            futures = {executor.submit(query_vendor_site, e): e for e in [Entity.from_dict(d) for d in reader]}
            bar = ChargingBar('Processing', max=len(futures))
            for f in concurrent.futures.as_completed(futures):
                url = futures[f]
                try:
                    (cert, logos) = f.result()
                except Exception as exc:
                    print('%r generated an exception: %s' % (url, exc))
                else:
                    print(cert, logos)
                bar.next()
            bar.finish()

#query_vendor_site('http://www.bancoprovincia.com.ar', 'debug')
#exit()

if __name__ == '__main__':
    from_csv('entidades.csv')
