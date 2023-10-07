import re
import requests
import logging
from bs4 import BeautifulSoup

URL = 'http://www.bcra.gob.ar/SistemasFinancierosYdePagos/Entidades_financieras.asp'
page = requests.post(URL, data={'bco': '00331'}, stream=False)
soup = BeautifulSoup(page.content, 'html.parser')
for l in soup.select('.post-pagina-interior'):
    print(l)
    for a in l.select('a'):
        print(a)
