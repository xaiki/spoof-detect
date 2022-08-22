#!/usr/bin/env python3

import os
import math
import cv2
import pathlib
from typing import NamedTuple

from entity import Entity

TILE_SIZE = 800
TILE_OVERLAP = 0.8

class BoundingBox(NamedTuple):
    x: float = 0.0
    y: float = 0.0
    w: float = 0.0
    h: float = 0.0

    @classmethod
    def from_centroid(cls, c):
        x = math.floor(c.x + c.w/2)
        y = math.floor(c.y + c.h/2)
        self = cls(x=x, y=y, w=math.ceil(c.w), h=math.ceil(c.h))
        return self

    @classmethod
    def from_dict(cls, d):
        self = cls(x=d['x'], y=d['y'], w=d['width'], h=d['height'])
        return self

class Centroid(BoundingBox):
    @classmethod
    def from_bounding_box(cls, b):
        x = math.floor(b.x - c.w/2)
        y = math.floor(b.y - c.h/2)
        self = cls(x=x, y=y, w=math.ceil(c.w), h=math.ceil(c.h))

def read_bounding_boxes(filename):
    boxes = []
    with open(filename, 'r') as f:
        (x,y,w,h) = [float(i) for i in f.readline().split(' ')[1:]]
        boxes.append(BoundingBox(x,y,w,h))
    return boxes

def floor_point(a, b):
    return (math.floor(a), math.floor(b))

def cut_img(im, s, e):
    x = s[0]
    y = s[1]
    w = e[0] - x
    h = e[1] - y

    print("DEBUG", im.shape, x, y, w, h)
    return im[y:h, x:w]

def cut_logo(im, l):
    (x, y, w, h) = floor_logo(l)
    return im[x:w, y:h]

def crop(fn, logos):
    basename = os.path.basename(fn).replace('.png', '')
    img_out = f"./data/squares/labels"
    txt_out = f"./data/squares/labels"
    pathlib.Path(img_out).mkdir(parents=True, exist_ok=True)
    pathlib.Path(txt_out).mkdir(parents=True, exist_ok=True)

    im = cv2.imread(fn)

    (h, w, c) = im.shape
    (tx, ty)= (
        math.ceil(w/(TILE_SIZE*TILE_OVERLAP)),
        math.ceil(h/(TILE_SIZE*TILE_OVERLAP))
    )

    print('shape', basename, tx, ty, h, w, logos)
    for x in range(tx):
        for y in range(ty):
            color = (0,x*(255/tx),y*(255/ty))

            fx = math.floor(x*(w - TILE_SIZE)/(tx))
            fy = math.floor(y*(h - TILE_SIZE)/(ty))

            start = (fx, fy)
            end = (fx + TILE_SIZE, fy + TILE_SIZE)

            #im = cv2.rectangle(im, start, end, color, 10)
            li = []
            for l in logos:
                def intersect():
                    six = l.x - fx
                    siy = l.y - fy
                    eix = six + l.w
                    eiy = siy + l.h

                    if six < 0:
                        if six + l.w < 0:
                            return None
                        six = 0
                    if siy < 0:
                        if siy + l.h < 0:
                            return None
                        siy = 0
                    if eix > TILE_SIZE:
                        if eix - l.w > TILE_SIZE:
                            return None
                        eix = TILE_SIZE
                    if eiy > TILE_SIZE:
                        if eiy - l.h > TILE_SIZE:
                            return None
                        eiy = TILE_SIZE

                    return BoundingBox(six, siy, eix - six, eiy - siy)

                p = intersect()
                if p:
                    li.append(p)

            c = (255, 0, 0)
            nim = im[fy:fy+TILE_SIZE, fx:fx+TILE_SIZE]
            img_name =f"{img_out}/{basename}.{x}.{y}.png"
            txt_name =f"{txt_out}/{basename}.{x}.{y}.txt"
            cv2.imwrite(img_name, nim)
            if len(li):
                with open(txt_name, 'w') as f:
                    for p in li:
                        cx = cw/2 + p.x
                        cy = ch/2 + p.y

                        a = f"{basename} {cx/TILE_SIZE} {cy/TILE_SIZE} {p.w/TILE_SIZE} {p.h/TILE_SIZE}"
                        f.write(a)
                        print(a)

if __name__ == '__main__':
    boxes = read_bounding_boxes("./data/debug.full.txt")
    print(boxes)
    crop("./data/debug.full.png", boxes)

