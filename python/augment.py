import os
import time
import math
import random
import csv

from io import BytesIO
import numpy as np
from cairosvg import svg2png
import cv2

import filetype
from filetype.match import image_matchers

from progress.bar import ChargingBar

import imgaug as ia
from imgaug import augmenters as iaa
from imgaug.augmentables.batches import UnnormalizedBatch

from entity import Entity
from common import defaults, mkdir
import imtool
import pipelines

BATCH_SIZE = 16
PARALLEL = 20
MIN_BACKGROUND_SIZE = 500

def process_bg(b):

        imw = cv2.imread(b.path)
        im, bb = imtool.remove_white(imw)
        annot = None
        label = b.path.replace('png', 'txt')
        if os.path.exists(label):
            # rewrite label with new coordinates
            [ww, wh, _] = imw.shape
            [iw, ih, _] = im.shape
            es = imtool.read_centroids(label)
            l = ''
            for e in es:
                [i, p, c] = e.values()
                [x,y,w,h] = [
                    max((c.x*ww - bb.x)/iw, 0),
                    max((c.y*wh - bb.y)/ih, 0),
                    (c.w*ww)/iw,
                    (c.h*wh)/ih
                ]

                l += f'{int(i)} {x} {y} {w} {h}\n'
            annot = l

        if im.shape[0] > args.minbgsize and im.shape[1]> args.minbgsize:
            return im, annot
        else:
            raise Exception(f'droping {b.path} after remove_white => {im.shape}')

def filter_bgs(bgs):
    ret = []
    for b in bgs:
        if b.path.endswith('txt'): continue
        try:
            img, annot = process_bg(b)
        except Exception as e:
            print(f'drop: {e}')
            continue
        ret.append((b, img, annot))
    return ret

def process(args):
    dest_images_path = os.path.join(args.dest, 'images')
    dest_labels_path = os.path.join(args.dest, 'labels')

    mkdir.make_dirs([dest_images_path, dest_labels_path])
    logo_images = []
    logo_alphas = []
    logo_labels = {}

    db = {}
    with open(defaults.MAIN_CSV_PATH, 'r') as f:
        reader = csv.DictReader(f)
        db = {e.bco: e for e in [Entity.from_dict(d) for d in reader]}

    background_images = []
    for d in args.background:
        background_images.extend(os.scandir(d))

    print(f'filtering {len(background_images)} background images from {args.background}')
    background_images = filter_bgs(background_images)
    assert(len(background_images))
    stats = {
        'failed': 0,
        'ok': 0
    }

    for d in os.scandir(args.logos):
        img = None
        if not d.is_file():
            stats['failed'] += 1
            continue

        try:
            if filetype.match(d.path, matchers=image_matchers):
                img = cv2.imread(d.path, cv2.IMREAD_UNCHANGED)
            else:
                png = svg2png(url=d.path)
                img = cv2.imdecode(np.asarray(bytearray(png), dtype=np.uint8), cv2.IMREAD_UNCHANGED)
            label = db[d.name.split('.')[0]].id

            (h, w, c) = img.shape
            if c == 3:
                img = imtool.add_alpha(img)

            if img.ndim < 3:
                print(f'very bad dim: {img.ndim}')

            (h, w, c) = img.shape

            assert(w > 10)
            assert(h > 10)

            stats['ok'] += 1

            (b, g, r, _) = cv2.split(img)
            alpha = img[:, :, 3]/255
            d = cv2.merge([b, g, r])

            logo_images.append(d)
            # tried id() tried __array_interface__, tried tagging, nothing works
            logo_labels.update({d.tobytes(): label})

            # XXX(xaiki): we pass alpha as a float32 heatmap,
            # because imgaug is pretty strict about what data it will process
            # and that we want the alpha layer to pass the same transformations as the orig
            logo_alphas.append(np.dstack((alpha, alpha, alpha)).astype('float32'))

        except Exception as e:
            stats['failed'] += 1
            print(f'error loading: {d.path}: {e}')

    print(stats)

    assert(len(logo_alphas) == len(logo_images))
    print(f"will process {len(logo_images)} images on {len(background_images)} backgrounds")

    # so that we don't get a lot of the same logos on the same page.
    zipped = list(zip(logo_images, logo_alphas))
    random.shuffle(zipped)
    logo_images, logo_alphas = zip(*zipped)

    n = len(logo_images)
    batches = []
    for i in range(math.floor(n*2/BATCH_SIZE)):
        s = (i*BATCH_SIZE)%n
        e = min(s + BATCH_SIZE, n)
        le = max(0, BATCH_SIZE - (e - s))

        a = logo_images[0:le] + logo_images[s:e]
        h = logo_alphas[0:le] + logo_alphas[s:e]

        assert(len(a) == BATCH_SIZE)

        batches.append(UnnormalizedBatch(images=a,heatmaps=h))

    bar = ChargingBar(f'augment ({len(logo_images)} logos {len(background_images)} bgs)', max=(len(batches)**2)/3*len(background_images))
    # We use a single, very fast augmenter here to show that batches
    # are only loaded once there is space again in the buffer.
    pipeline = pipelines.HUGE

    def create_generator(lst):
        for b in lst:
            print(f"Loading next unaugmented batch...")
            yield b

    batches_generator = create_generator(batches)

    batch = 0
    with pipeline.pool(processes=args.parallel, seed=1) as pool:
        batches_aug = pool.imap_batches(batches_generator, output_buffer_size=5)

        print(f"Requesting next augmented batch...{batch}/{len(batches)}")
        for i, batch_aug in enumerate(batches_aug):
            idx = list(range(len(batch_aug.images_aug)))
            random.shuffle(idx)
            for j, (d, img, annot) in enumerate(background_images):
                basename = d.name.replace('.png', f'.{i}.{j}')
                annotations = []
                try:
                    annotations.append(annot.rstrip())
                except:
                    pass

                for k in range(math.floor(len(batch_aug.images_aug)/3)):
                    bar.next()
                    logo_idx = (j+k*4)%len(batch_aug.images_aug)

                    orig = batch_aug.images_unaug[logo_idx]
                    label = logo_labels[orig.tobytes()]
                    logo = batch_aug.images_aug[logo_idx]

                    assert(logo.shape == orig.shape)

                    # XXX(xaiki): we get alpha from heatmap, but will only use one channel
                    # we could make mix_alpha into mix_mask and pass all 3 chanels
                    alpha = cv2.split(batch_aug.heatmaps_aug[logo_idx])

                    try:
                        bb = imtool.mix_alpha(img, logo, alpha[0],
                                              random.random(), random.random())
                        c = bb.to_centroid(img.shape)
                        annotations.append(c.to_annotation(label))
                    except AssertionError as err:
                        print(f'couldnt process {i}, {j}: {err}')
                    except Exception as err:
                        print(f'error in mix pipeline: {err}')

                try:
                    cv2.imwrite(f'{dest_images_path}/{basename}.png', img)
                    label_path = f"{dest_labels_path}/{basename}.txt"
                    with open(label_path, 'a') as f:
                        f.write('\n'.join(annotations))
                except Exception:
                    print(f'couldnt write image {basename}')

            if i < len(batches)-1:
                print(f"Requesting next augmented batch...{batch}/{len(batches)}")
                batch += 1
        bar.finish()

if __name__ == '__main__':
    import argparse
    print("✨ augmenting data")
    parser = argparse.ArgumentParser(description='mix backgrounds and logos into augmented data for YOLO')
    parser.add_argument('--logos', metavar='logos', type=str,
                        default=defaults.LOGOS_DATA_PATH,
                        help='dir containing logos')
    parser.add_argument('--background', metavar='backgrounds', type=str,
                        nargs='+',
                        default=[defaults.SCREENSHOT_PATH, defaults.FISH_PATH],
                        help='dir containing background plates')
    parser.add_argument('--dst', dest='dest', type=str,
                        default=defaults.AUGMENTED_DATA_PATH,
                        help='dest dir')
    parser.add_argument('--parallel', metavar='parallel', type=int,
                        default=PARALLEL,
                        help='number of concurrent jobs')
    parser.add_argument('--min-background-size', dest='minbgsize', type=int,
                        default=MIN_BACKGROUND_SIZE, help='minimum background size')
    args = parser.parse_args()
    process(args)
