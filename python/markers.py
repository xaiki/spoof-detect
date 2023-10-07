import os
import cv2
import argparse
import imtool

parser = argparse.ArgumentParser(description='shows YOLO markers')
parser.add_argument('pngs', metavar='img.png', type=str, nargs='+',
                    help='images to debug')
args = parser.parse_args()

if len(args.pngs) and os.path.isdir(args.pngs[0]):
    args.pngs = [d.path for d in os.scandir(args.pngs[0])]

def process():
    for i in args.pngs:
        if i.endswith('txt'): continue
        im = cv2.imread(i)

        try:
            assert(im.shape)
        except AttributeError:
            print(f'couldnt parse {i}')
            continue

        label = i.replace('images', 'labels').replace('.png', '.txt').replace('.jpg', '.txt')
        print(i)
        try:
            results = imtool.read_centroids(label)
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f'error handeling {i}', e)
            continue
        bbs = [r["box"].to_bounding_box(im.shape) for r in results]
        for i,b in enumerate(bbs):
            print(b)
            c = (100, 255*i/len(bbs), 255*(1 - i/len(bbs)))
            cv2.rectangle(im, b.start, b.end, c, 5)

        cv2.imshow('result', im)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

process()
