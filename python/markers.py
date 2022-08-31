import cv2
import argparse
import imtool

parser = argparse.ArgumentParser(description='shows YOLO markers')
parser.add_argument('pngs', metavar='img.png', type=str, nargs='+',
                    help='images to debug')
args = parser.parse_args()

for i in args.pngs:
    im = cv2.imread(i)
    label = i.replace('images', 'labels').replace('.png', '.txt').replace('.jpg', '.txt')
    bco, ccs = imtool.read_centroids(label)
    bbs = [c.to_bounding_box(im.shape) for c in ccs]
    for i,b in enumerate(bbs):
        c = (100, 255*i/len(bbs), 255*(1 - i/len(bbs)))
        cv2.rectangle(im, b.start, b.end, c, 5)

cv2.imshow('result', im)
cv2.waitKey(0)
cv2.destroyAllWindows()
