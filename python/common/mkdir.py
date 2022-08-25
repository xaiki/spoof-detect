import pathlib

def make_dirs(dirs: [str]):
    for p in dirs:
        pathlib.Path(p).mkdir(parents=True, exist_ok=True)

