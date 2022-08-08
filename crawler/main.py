import csv

import requests
from bs4 import BeautifulSoup
from progress.bar import ChargingBar

from entity import Entity
from common import selectors

URL = "http://www.bcra.gob.ar/SistemasFinancierosYdePagos/Entidades_financieras.asp"
page = requests.get(URL)

soup = BeautifulSoup(page.content, "html.parser")

options = soup.find(class_="form-control").find_all('option')
with open('entidades.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(Entity.row_names())

    bar = ChargingBar('Processing', max=len(options))
    for o in options[1:]:
        e = Entity(
            name = o.text,
            bco = o.attrs['value']
        )
        page = requests.post(URL, data={'bco': e.bco})
        soup = BeautifulSoup(page.content, "html.parser")
        try:
            img = soup.select_one(selectors.logosbancos).attrs['src']
            img = img.replace("../", "https://www.bcra.gob.ar/")
        except AttributeError as err:
            print('img', e.name, err)
            img = None
        e.logo = img

        a = soup.select_one(selectors.entity_http)
        try:
            a = a.attrs['href']
        except AttributeError:
            a = soup.select_one(selectors.entity_mailto)
            try:
                a = 'http://' + a.attrs['href'].split('@')[1]

            except TypeError:
                print('ERROR', a)

        e.url = a
        writer.writerow(e.to_row())
        bar.next()
    bar.finish()
