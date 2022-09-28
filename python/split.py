#!/usr/bin/python
import os
import math
from common import defaults, mkdir

PATHS = {
    6: {
        'images': lambda dest, d: os.path.join(dest, 'images', d ),
        'labels': lambda dest, d: os.path.join(dest, 'labels', d )
    },
    5: {
        'images': lambda desd, d: os.path.join(dest, d, 'images'),
        'labels': lambda desd, d: os.path.join(dest, d, 'labels'),
    }
}

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='splits a yolo dataset between different data partitions')
    parser.add_argument('datapath', metavar='datapath', type=str, 
                        help='csv file', default=defaults.SQUARES_DATA_PATH)
    parser.add_argument('--partitions', metavar='partitions', type=str, nargs='+',
                        help='data path', default=['train:0.8', 'val:0.1', 'test:0.1'])
    parser.add_argument('--dest', metavar='dest', type=str,
                        help='dest path', default=defaults.SPLIT_DATA_PATH)
    parser.add_argument('--yolo', metavar='yolo', type=int,
                        help='yolo version', default=6)

    args = parser.parse_args()
    assert(PATHS[args.yolo])

    def image_to_label(i):
        l = i.replace('images', 'labels').replace('.png', '.txt').replace('.jpg', '.txt')
        if os.path.exists(l):
            return l
        return None

    images = [d for d in os.scandir(os.path.join(args.datapath, 'images'))]

    np = -1
    for d,r in [a.split(':') for a in args.partitions]:
        p = np + 1
        np = min(p + math.floor(len(images)*float(r)), len(images))

        cpi = PATHS[args.yolo]['images'](args.dest, d)
        cpl = PATHS[args.yolo]['labels'](args.dest, d)
        rpi = os.path.relpath(os.path.join(args.datapath, 'images'), cpi)
        rpl = os.path.relpath(os.path.join(args.datapath, 'labels'), cpl)

        mkdir.make_dirs([cpi, cpl])
        print( f'{d:6s} [ {p:6d}, {np:6d} ] ({np-p:6d}:{(np-p)/len(images):0.2f} )')
        for si in images[p:np]:
            l = image_to_label(si.path)
            os.symlink(os.path.join(rpi, si.name), os.path.join(cpi, si.name))
            if l:
                nl = os.path.basename(l)
                os.symlink(os.path.join(rpl, nl), os.path.join(cpl, nl))
