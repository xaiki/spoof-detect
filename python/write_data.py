import csv
import entity
from common import defaults

def gen_data_yaml(bcos):
    names = [f"{d.name}" for d in bcos.values()]
    return f'''
train: ../data/squares
val: ../data/squares

nc: {len(bcos.keys())}
names: [{names}]
'''

if __name__ == '__main__':
    bcos =  entity.read_entities(defaults.MAIN_CSV_PATH)
    print(gen_data_yaml(bcos))
