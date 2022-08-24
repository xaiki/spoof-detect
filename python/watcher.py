import os
import inotify.adapters
from imtool import read_bounding_boxes, crop

def watch(dir):
    seen = 0
    i = inotify.adapters.Inotify()
    i.add_watch(dir)
    for event in i.event_gen(yield_nones=False):
        (_, type_names, path, filename) = event

        if filename.endswith(".png") and type_names[0] in ['IN_CLOSE_WRITE']:
            seen += 1
            print(f"{seen} PATH=[{path}] FILENAME=[{filename}] EVENT_TYPES={type_names}")
            try:
                bbs = read_bounding_boxes(os.path.join(path, filename.replace('.png', '.txt')))
                crop(os.path.join(path, filename), bbs)
            except Exception as e:
                print(f"error: {e}")

if __name__ == '__main__':
    watch('./data')
