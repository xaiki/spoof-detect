import os
import argparse
import imtool

parser = argparse.ArgumentParser(description='crop images to train YOLO on squares')
parser.add_argument('src', metavar='dir', type=str, nargs='+',
                    help='dir containing the images')
parser.add_argument('--dst', dest='dst', type=str, default='./data/squares',
                    help='dest dir')

args = parser.parse_args()

for d in args.src:
    i = 0
    with os.scandir(d) as it:
        for e in it:
            if e.name.endswith('.png') and e.is_file():
                print(e.name)
                label = e.path.replace('images', 'labels').replace('.png', '.txt')
                try:
                    i+=1
                    bco, boxes = imtool.read_centroids(label)
                    imtool.crop(bco, e.path, boxes, args.dst)

                except Exception as err:
                    print(err)
