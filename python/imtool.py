#!/usr/bin/env python3

import os
import math
import cv2
import numpy as np
from typing import NamedTuple

from entity import Entity
from common import mkdir

TILE_SIZE = 416
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
    bco = None
    with open(filename, 'r') as f:
        lines = f.readlines()
        for l in lines:
            (b, x,y,w,h) = [float(i) for i in l.split(' ')]
            bco = b
            if x < 0 or y < 0 or w < 10 or h < 10:
                print(f"dropping logo, it has inconsistent size: {w}x{h}@{x}x{y}")
                continue
            boxes.append(BoundingBox(x,y,w,h))
    return bco, boxes

def coord_dict_to_point(c):
    return coord_to_point(c['x'], c['y'], c['width'], c['heigh'])

def coord_to_point(cx, cy, cw, ch):
    x = math.floor(cx + cw/2)
    y = math.floor(cy + ch/2)
    return f"{x} {y} {math.ceil(cw)} {math.ceil(ch)}"

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

def add_alpha(img):
    b, g, r = cv2.split(img)
    a = np.ones(b.shape, dtype=b.dtype) * 50
    return cv2.merge((b,g,r,a))

def remove_white(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
    gray = 255*(gray<128)
    coords = cv2.findNonZero(gray)
    x, y, w, h = cv2.boundingRect(coords) # Find minimum spanning bounding box
    rect = img[y:y+h, x:x+w] # Crop the image - note we do this on the original image

    return rect

def mix(a, b, fx, fy):
    (ah, aw, ac) = a.shape
    (bh, bw, bc) = b.shape

    assert(aw > bw)
    assert(ah > bh)

    x = math.floor(fx*(aw - bw))
    y = math.floor(fy*(ah - bh))

    mat = a[y:y+bh,x:x+bw]
    cols = b[:, :, :3]
    alpha = b[:, :, 3]/255
    mask = np.dstack((alpha, alpha, alpha))

    a[y:y+bh,x:x+bw] = mat * (1 - mask) + cols * mask

    return a, BoundingBox(x, y, bw, bh), (aw, ah)

def crop(id, fn, logos):
    basename = os.path.basename(fn).replace('.png', '')
    img_out = f"./data/squares/images"
    txt_out = f"./data/squares/labels"
    debug_out = f"./data/debug"
    mkdir.make_dirs[debug_out, img_out, txt_out]

    im = cv2.imread(fn)
    rim = cv2.imread(fn)

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
            logo_color = (255, 0, 0)

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

            rim = cv2.rectangle(rim, start, end, color, 10)
            li = []
            for l in logos:
                rim = cv2.rectangle(rim,
                                    floor_point(l.x, l.y),
                                    floor_point(l.x + l.w, l.y + l.h),
                                    logo_color, 5)
                def intersect():
                    six = l.x - f.x
                    siy = l.y - f.y
                    eix = six + l.w
                    eiy = siy + l.h

                    #print('intersect', (six, siy), (eix, eiy), f, l)

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

            nim = im[start[1]:end[1], start[0]:end[0]]
            rnim = rim[start[1]:end[1], start[0]:end[0]]
            img_name =f"{img_out}/{basename}-x{x}y{y}.jpg"
            txt_name =f"{txt_out}/{basename}-x{x}y{y}.txt"

            cv2.imwrite(img_name, nim)
            if len(li):
                with open(txt_name, 'w') as f:
                    for p in li:
                        cx = p.x
                        cy = p.y

                        dim = cv2.rectangle(rnim,
                                           floor_point(cx - p.w/2, cy - p.h/2),
                                           floor_point(cx + p.w/2, cy + p.h/2),
                                           logo_color,
                                           5)

                        a = f"{int(id)} {cx/TILE_SIZE} {cy/TILE_SIZE} {p.w/TILE_SIZE} {p.h/TILE_SIZE}\n"
                        f.write(a)
                        print(a)
                        cv2.imwrite(f'{debug_out}/{basename}{x}{y}.debug.png', dim)

    cv2.imwrite(f'{debug_out}/{basename}.debug.png', rim)

if __name__ == '__main__':
    i = 0
    with os.scandir('./data/') as it:
        for e in it:
            if e.name.endswith('.txt') and e.is_file():
                print(e.name)
                try:
                    i+=1
                    bco, boxes = read_bounding_boxes(e.path)
                    crop(i, e.path.replace('.txt', '.png'), boxes)
                except Exception as err:
                    print(err)

