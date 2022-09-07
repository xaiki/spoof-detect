#!/usr/bin/env python3
#
import os
import math
import socket

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from common import selectors
from entity import Entity
from common import defaults,mkdir
from imtool import coord_dict_to_point

options = webdriver.FirefoxOptions()
options.add_argument("--headless")
options.add_argument("--window-size=1920x8000")
options.set_preference('WebglAllowWindowsNativeGl', True)

host = os.getenv('GECKO_HOST') or 'localhost'
port = os.getenv('GECKO_PORT') or '4444'
ip = socket.gethostbyname(host)

print(f'host: {host}->{ip}, port: {port}')

driver = webdriver.Remote(
    options=options,
    desired_capabilities=webdriver.DesiredCapabilities.FIREFOX,
    command_executor=f"http://{ip}:{port}"
)
def sc_entity(e: Entity):
    print(f'screenshoting: {e}')
    mkdir.make_dirs([
            defaults.IMAGES_PATH,
            defaults.LABELS_PATH,
    ])

    driver.implicitly_wait(10)
    driver.get(e.url)
    #driver.save_screenshot(f"{defaults.DATA_PATH}/{e.bco}.png")

    p = f"{defaults.IMAGES_PATH}/{e.bco}.full.png"
    html = driver.find_element(By.TAG_NAME, 'html')
    # driver.save_screenshot(p)
    html.screenshot(p)
    print(f'wrote: {p}')

    logos = driver.find_elements(By.CSS_SELECTOR, selectors.img_logo) or []
    logos.extend(driver.find_elements(By.CSS_SELECTOR, selectors.id_logo) or [])
    logos.extend(driver.find_elements(By.CSS_SELECTOR, selectors.cls_logo) or [])
    with open(f"{defaults.LABELS_PATH}/{e.bco}.full.txt", 'w') as f:
        for i in logos:
            f.write(f"{e.id} {coord_dict_to_point(i.rect)}\n")

if __name__ == '__main__':
    sc_entity(Entity.from_dict({'url': 'http://www.bbva.com.ar', 'bco': 'debug'}))
