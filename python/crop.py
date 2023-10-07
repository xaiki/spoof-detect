import os
import argparse
import imtool
from progress.bar import ChargingBar
import concurrent.futures

PARALLEL = 30
print("🖼 croping augmented data")

parser = argparse.ArgumentParser(description='crop images to train YOLO on squares')
parser.add_argument('src', metavar='dir', type=str, nargs='+',
                    help='dir containing the images')
parser.add_argument('--dst', dest='dst', type=str, default='./data/squares',
                    help='dest dir')
parser.add_argument('--parallel', metavar='parallel', type=int,
                    default=PARALLEL,
                    help='number of concurrent jobs')

args = parser.parse_args()

def process(e):
    if e.name.endswith('.png') and e.is_file():
        # print(e.name)
        label = e.path.replace('images', 'labels').replace('.png', '.txt')
        try:
            id, boxes = imtool.read_centroids(label)
            imtool.crop(id, e.path, boxes, args.dst)

        except Exception as err:
            print(err)

for d in args.src:
    with os.scandir(d) as it:
        with concurrent.futures.ThreadPoolExecutor(max_workers = args.parallel) as executor:
            futures = {executor.submit(process, e): e for e in it}
            count = len(futures.keys())
            bar = ChargingBar('crop', max=count)

            print('waiting for futures')
            for f in concurrent.futures.as_completed(futures):
                e = futures[f]
                try:
                    f.result()
                except Exception as err:
                    print(f'{a}({e}) generated an exception: {err}')
                bar.next()
            bar.finish()
