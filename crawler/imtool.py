#!/usr/bin/env python3

import os
import math
import cv2
import pathlib
from typing import NamedTuple

from entity import Entity

TILE_SIZE = 800
TILE_OVERLAP = 0.2

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
        lines = f.readlines()
        for l in lines:
            (x,y,w,h) = [float(i) for i in l.split(' ')[1:]]
            if x < 0 or y < 0 or w < 10 or h < 10:
                print(f"dropping logo, it has inconsistent size: {w}x{h}+{x}x{y}")
                continue
            boxes.append(BoundingBox(x,y,w,h))
    return boxes

def floor_point(x, y):
    return (math.floor(x), math.floor(y))

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
    img_out = f"./data/squares/images"
    txt_out = f"./data/squares/labels"
    debug_out = f"./data/debug"
    pathlib.Path(debug_out).mkdir(parents=True, exist_ok=True)
    pathlib.Path(img_out).mkdir(parents=True, exist_ok=True)
    pathlib.Path(txt_out).mkdir(parents=True, exist_ok=True)

    im = cv2.imread(fn)

    (h, w, c) = im.shape
    (tw, th) = (min(w, TILE_SIZE), min(h, TILE_SIZE))
    (tx, ty)= (
        math.ceil(w/(tw*TILE_OVERLAP)),
        math.ceil(h/(th*TILE_OVERLAP))
    )

    print('shape', basename, tx, ty, w, h, logos)
    for x in range(tx):
        for y in range(ty):
            color = (0,x*(255/tx),y*(255/ty))


            if tx < 2:
                xs = 0
            else:
                xs = (w - tw)*x/(tx - 1)
            if ty < 2:
                ys = 0
            else:
                ys = (h - th)*y/(ty - 1)

            f = BoundingBox(xs, ys, tw, th)

            start = floor_point(f.x, f.y)
            end = floor_point(f.x + f.w, f.y + f.h)

            im = cv2.rectangle(im, start, end, color, 10)
            li = []
            for l in logos:
                def intersect():
                    six = l.x - f.x
                    siy = l.y - f.y
                    eix = six + l.w
                    eiy = siy + l.h

                    print('intersect', (six, siy), (eix, eiy), f, l)

                    if six < 0:
                        if six + l.w < 0:
                            return None
                        six = 0
                    if siy < 0:
                        if siy + l.h < 0:
                            return None
                        siy = 0
                    if eix > tw:
                        if eix - l.w > tw:
                            return None
                        eix = tw
                    if eiy > th:
                        if eiy - l.h > th:
                            return None
                        eiy = th

                    return BoundingBox(six, siy, eix - six, eiy - siy)

                p = intersect()
                if p:
                    li.append(p)

            c = (255, 0, 0)

            print(start, end)
            nim = im[start[1]:end[1], start[0]:end[0]]
            img_name =f"{img_out}/{basename}-x{x}y{y}.jpg"
            txt_name =f"{txt_out}/{basename}-x{x}y{y}.txt"

            cv2.imwrite(img_name, nim)
            if len(li):
                with open(txt_name, 'w') as f:
                    for p in li:
                        print(p)
                        dim = cv2.rectangle(nim,
                                           floor_point(p.x - p.w/2, p.y - p.h/2),
                                           floor_point(p.x + p.w/2, p.y + p.h/2),
                                           c,
                                           5)
                        cx = p.w/2 + p.x
                        cy = p.h/2 + p.y

                        a = f"{basename} {cx/TILE_SIZE} {cy/TILE_SIZE} {p.w/TILE_SIZE} {p.h/TILE_SIZE}"
                        f.write(a)
                        print(a)
                        cv2.imwrite(f'{debug_out}/{basename}{x}{y}.debug.png', dim)

    cv2.imwrite(f'{debug_out}/{basename}.debug.png', im)

if __name__ == '__main__':
    with os.scandir('./data/') as it:
        for e in it:
            if e.name.endswith('.txt') and e.is_file():
                print(e.name)
                try:
                    boxes = read_bounding_boxes(e.path)
                    crop(e.path.replace('.txt', '.png'), boxes)
                except Exception as err:
                    print(err)

