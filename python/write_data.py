import csv
import entity
import argparse

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
    parser = argparse.ArgumentParser(description='creates a YOLOv5 data.yaml')
    parser.add_argument('csv', metavar='csv', type=str, 
                    help='csv file')
    args = parser.parse_args()
    bcos =  entity.read_entities(args.csv)
    print(gen_data_yaml(bcos))
