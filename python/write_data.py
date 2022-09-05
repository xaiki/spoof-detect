import csv
import entity
import argparse

from common import defaults

def gen_data_yaml(bcos, datapath='../data'):
    names = [f"{d['name']}" for d in bcos.values()]
    return f'''
# this file is autogenerated by write_data.py

train: {datapath}/squares
val: {datapath}/squares

nc: {len(bcos.keys())}
names: {names}
'''

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='creates a YOLOv5 data.yaml')
    parser.add_argument('csv', metavar='csv', type=str, 
                    help='csv file')
    parser.add_argument('--data', metavar='data', type=str,
                        help='data path', default='../data')
    args = parser.parse_args()
    bcos =  entity.read_entities(args.csv)
    print(gen_data_yaml(bcos, args.data))
