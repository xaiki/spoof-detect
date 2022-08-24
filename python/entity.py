#!/usr/bin/env python3

class Entity():
    _DATA_PATH = './data'
    def __init__(self, name, bco, url=None, logo=None):
        self.name = name
        self.bco = bco
        self.url = url
        self.logo = logo

    def __repr__(self):
        return f"""
Entity:
        name: {self.name}
        bco:  {self.bco}
        url:  {self.url}
        logo: {self.logo}
        """

    @classmethod
    def from_list(cls, l):
        self = apply(cls, l)
        return self

    @classmethod
    def from_dict(cls, d):
        self = cls(None, None)
        
        for f in d.keys():
            setattr(self, f, d[f])
        return self

    @classmethod
    def row_names(cls):
        return ['name', 'bco', 'url', 'logo']

    @property
    def DATA_PATH(self):
        return self._DATA_PATH

    def to_row(self):
        return [self.name, self.bco, self.url, self.logo]

if __name__ == '__main__':
    e = Entity.from_dict({'url': 'blah'})
    assert(e.url == 'blah')
    print(e)
