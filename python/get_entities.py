#!/usr/bin/env python
import csv
import requests
import shutil
import re

from bs4 import BeautifulSoup
from progress.bar import ChargingBar
import concurrent.futures

import web
from entity import Entity
from common import selectors, defaults, mkdir

URL = 'http://www.bcra.gob.ar/SistemasFinancierosYdePagos/Entidades_financieras.asp'
page = requests.get(URL)
soup = BeautifulSoup(page.content, 'html.parser')

options = soup.find(class_='form-control').find_all('option')
mkdir.make_dirs([defaults.DATA_PATH, defaults.LOGOS_DATA_PATH])

def get_links(soup):
    for l in soup.select('.post-pagina-interior'):
        for a in l.select('a'):
            if 'href' in a.attrs and a.attrs['href'].startswith('http'):
                return a.attrs['href']


with open(f'{defaults.MAIN_CSV_PATH}.tmp', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(Entity.row_names())

    bar = ChargingBar('get entities', max=len(options))
    def get_bco(o, i):
        (name, bco)= (o.text, o.attrs['value'])

        page = requests.post(URL, data={'bco': bco}, stream=False)
        soup = BeautifulSoup(page.content, 'html.parser')
        img = f'https://www.bcra.gob.ar/Imagenes/logosbancos/{bco}.jpg'
        e = Entity(name, id=i, bco=bco, logo=str(img), url=str(get_links(soup)))
        writer.writerow(e.to_row())
        i+=1
    with concurrent.futures.ThreadPoolExecutor(max_workers = 20) as executor:
        futures = {executor.submit(get_bco, o, i): o for (i, o) in enumerate(options[1:])}
        for f in concurrent.futures.as_completed(futures):
            o = futures[f]
            try:
                f.result()
            except Exception as err:
                print(f'({o}) generated an exception: {err}')
        bar.next()
    bar.finish()

shutil.move(f'{defaults.MAIN_CSV_PATH}.tmp', defaults.MAIN_CSV_PATH)
print(f'scrape finished, found {len(options[1:])} entities, dumped to {defaults.MAIN_CSV_PATH}')
