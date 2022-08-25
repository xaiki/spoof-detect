#!/usr/bin/env python3
#

import math

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from common import selectors
from entity import Entity
from common import defaults,mkdir

options = webdriver.FirefoxOptions()
options.add_argument("--headless")
options.add_argument("--window-size=1920x8000")

def coord_to_point(c):
    x = math.floor(c['x'] + c['width']/2)
    y = math.floor(c['y'] + c['height']/2)
    return f"{x} {y} {math.ceil(c['width'])} {math.ceil(c['height'])}"

driver = webdriver.Firefox(options=options)
def sc_entity(e: Entity):
    print(f'screenshoting: {e}')
    mkdir.make_dirs([
            defaults.IMAGES_PATH,
            defaults.LABELS_PATH,
    ])

    driver.implicitly_wait(10)
    driver.get(e.url)
    #driver.save_screenshot(f"{defaults.DATA_PATH}/{e.bco}.png")
    driver.save_full_page_screenshot(f"{defaults.IMAGES_PATH}/{e.bco}.full.png")

    logos = driver.find_elements(By.CSS_SELECTOR, selectors.img_logo) or []
    logos.extend(driver.find_elements(By.CSS_SELECTOR, selectors.id_logo) or [])
    logos.extend(driver.find_elements(By.CSS_SELECTOR, selectors.cls_logo) or [])
    with open(f"{defaults.LABELS_PATH}/{e.bco}.full.txt", 'w') as f:
        for i in logos:
            f.write(f"{e.id} {coord_to_point(i.rect)}\n")

if __name__ == '__main__':
    sc_entity(Entity.from_dict({'url': 'http://www.bbva.com.ar', 'bco': 'debug'}))
