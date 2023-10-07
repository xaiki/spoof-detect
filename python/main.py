import csv
import requests
import shutil

from bs4 import BeautifulSoup
from progress.bar import ChargingBar

from entity import Entity
from common import selectors, defaults, mkdir

URL = 'http://www.bcra.gob.ar/SistemasFinancierosYdePagos/Entidades_financieras.asp'
page = requests.get(URL)
soup = BeautifulSoup(page.content, 'html.parser')

options = soup.find(class_='form-control').find_all('option')
mkdir.make_dirs([defaults.DATA_PATH])

with open(f'{defaults.MAIN_CSV_PATH}.tmp', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(Entity.row_names())

    i = 0
    bar = ChargingBar('Processing', max=len(options))
    for o in options[1:]:
        (name, bco)= (o.text, o.attrs['value'])
        page = requests.post(URL, data={'bco': bco})
        soup = BeautifulSoup(page.content, 'html.parser')
        try:
            img = soup.select_one(selectors.logosbancos).attrs['src']
            img = img.replace('../', 'https://www.bcra.gob.ar/')
        except AttributeError as err:
            print('img', name, err)
            img = None

        a = soup.select_one(selectors.entity_http)
        try:
            a = a.attrs['href']
        except AttributeError:
            a = soup.select_one(selectors.entity_mailto)
            try:
                a = 'http://' + a.attrs['href'].split('@')[1]

            except TypeError:
                print('ERROR', a)

        e = Entity(name, id=i, bco=bco, logo=str(img), url=str(a))
        writer.writerow(e.to_row())
        i+=1
        bar.next()
    bar.finish()

shutil.move(f'{defaults.MAIN_CSV_PATH}.tmp', defaults.MAIN_CSV_PATH)
print('scrape finished')
