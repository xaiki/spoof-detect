#!/usr/bin/env python3
#
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from common import selectors
from entity import Entity

options = webdriver.FirefoxOptions()
options.add_argument("--headless")
options.add_argument("--window-size=1920x8000")

driver = webdriver.Firefox(options=options)
def sc_entity(e: Entity):
    print(e)
    driver.get(e.url)
    driver.save_screenshot(f"{e.DATA_PATH}/screenshot.png")
    driver.save_full_page_screenshot(f"{e.DATA_PATH}/screenshot.full.png")

    logos = driver.find_elements(By.CSS_SELECTOR, selectors.logo)
    with open(f"{e.DATA_PATH}/logo.pos", 'w') as f:
        for i in logos:
            f.write(repr(i.rect))
            print(i.get_attribute('src'), i.rect)

if __name__ == '__main__':
    sc_entity(Entity.from_dict({'url': 'http://www.bbva.com.ar', 'bco': 'debug'}))
