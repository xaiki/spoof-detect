#!/usr/bin/env python3
import csv
from typing import NamedTuple

from common import defaults

def read_entities(fn = defaults.MAIN_CSV_PATH):
    with open(fn, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        bcos = { d['bco']:Entity.from_dict(d) for d in reader}
    return bcos

class Entity(NamedTuple):
    name: str
    id: int = 0
    bco: str = "debug"
    url: str = ''
    logo: str = ''

    def __repr__(self):
        return f"""
Entity {self.id}:
        name: {self.name}
        bco:  {self.bco}
        url:  {self.url}
        logo: {self.logo}
        """

    @classmethod
    def from_list(cls, l):
        self = apply(cls, l)
        return self

    # this now looks horrible…
    @classmethod
    def from_dict(cls, d):
        o = {'name': None, 'id': 0, 'bco': None, 'url': None, 'logo': None}
        o.update(d)
        self = cls(o['name'], o['id'], o['bco'], o['url'], o['logo'])
        return self

    @classmethod
    def row_names(cls):
        return ['id', 'name', 'bco', 'url', 'logo']

    def to_row(self):
        return [self.id, self.name, self.bco, self.url, self.logo]

if __name__ == '__main__':
    e = Entity.from_dict({'name': 'test', 'url': 'blah'})
    assert(e.url == 'blah')
    print(e)
