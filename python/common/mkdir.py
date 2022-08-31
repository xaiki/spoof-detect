import pathlib
from typing import List

def make_dirs(dirs: List[str]):
    for p in dirs:
        pathlib.Path(p).mkdir(parents=True, exist_ok=True)

