#!/usr/bin/env python3
import ssl
import shutil
import requests
from bs4 import BeautifulSoup

from entity import Entity
from common import selectors, defaults

def get_page(e: Entity):
    try:
        page = requests.get(e.url)
    except Exception:
        url = e.url.replace('http', 'https')
        page = requests.get(url)
    return page

def get_cert(e: Entity):
    ssl_url = e.url.split("/")[2]
    try:
        cert = ssl.get_server_certificate((ssl_url, 443), ca_certs=None)
        fn = f"{defaults.DATA_PATH}/{e.bco}.cert"
        with open(fn, 'w') as f:
            f.write(cert)
    except Exception as err:
        with open(f"{fn}.error.log", 'w+') as f:
            f.write(str(err))
    return fn

def get_img_logo(src: str, fn):
        res = requests.get(src, stream=True)
        with open(fn, "wb") as f:
            shutil.copyfileobj(res.raw, f)
        return fn

def get_logos(e: Entity, page):
    soup = BeautifulSoup(page.content, "html.parser")
    logos = soup.select(selectors.img_logo)
    logos.extend(soup.select(selectors.id_logo))
    logos.extend(soup.select(selectors.cls_logo))

    i = 0
    lfn = []
    for l in logos:
        if 'src' in l.attrs:
            src = l.attrs['src']
            ext = src.split('.')[-1].split('/')[-1]
            if not src.startswith('http'): src = e.url + src
            fn = f"{defaults.DATA_PATH}/logos/{e.bco}.{i}.{ext}"
            lfn.append(get_img_logo(src, fn))
        i+=1
    return lfn
