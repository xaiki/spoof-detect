import os
import inotify.adapters

import augment
from imtool import read_bounding_boxes, crop
from common import defaults, mkdir

def handle_png(event):
    (_, type_names, path, filename) = event

    bbs = read_bounding_boxes(os.path.join(path, filename.replace('.png', '.txt')))
    crop(os.path.join(path, filename), bbs)

def handle_csv(event):
    (_, type_names, path, filename) = event

    print('csv changed, will run vendor')
    import vendor
    vendor.from_csv(os.path.join(path, filename))
    augment.process()

handlers = {
    '.png': handle_png,
    '.csv': handle_csv
}

def watch(dirs):
    i = inotify.adapters.Inotify()
    [i.add_watch(d) for d in dirs]
    print(f'watching {dirs}')
    for event in i.event_gen(yield_nones=False):
        (_, type_names, path, filename) = event

        for k in handlers.keys():
            if filename.endswith(k) and type_names[0] in ['IN_CLOSE_WRITE']:
                print(f"PATH=[{path}] FILENAME=[{filename}] EVENT_TYPES={type_names}")
                try:
                    handlers[k](event)
                except Exception as e:
                    print(f'Error in {k} handler: {e}')

if __name__ == '__main__':
    dirs = ['./data', defaults.IMAGES_PATH, defaults.AUGMENTED_IMAGES_PATH]
    mkdir.make_dirs(dirs)
    watch(dirs)
