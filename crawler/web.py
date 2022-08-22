#!/usr/bin/env python3
import ssl
from bs4 import BeautifulSoup

from entity import Entity
from common import selectors
def get_page(e: Entity):
    try:
        page = requests.get(e.url)
    except Exception:
        e.url = e.url.replace('http', 'https')
        page = requests.get(e.url)
    return page

def get_cert(e: Entity):
    ssl_url = e.url.split("/")[2]
    try:
        cert = ssl.get_server_certificate((ssl_url, 443), ca_certs=None)
        fn = f"{e.DATA_PATH}/{e.bco}.cert"
        with open(fn, 'w') as f:
            f.write(cert)
    except Exception as err:
        with open(f"{fn}.error.log", 'w+') as f:
            f.write(str(err))
    return fn

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

        fn = f"{e.DATA_PATH}/logos/{e.bco}.{i}.{ext}"
        with open(fn, "wb") as f:
            shutil.copyfileobj(res.raw, f)
        lfn.append(fn)
        i+=1
    return lfn
