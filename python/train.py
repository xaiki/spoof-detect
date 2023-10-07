import yaml
from entities import read_entities

entities = read_entities()

with open(r'/content/yolov5/data.yaml') as file:
    # The FullLoader parameter handles the conversion from YAML
    # scalar values to Python the dictionary format
    labels_list = yaml.load(file, Loader=yaml.FullLoader)

    label_names = labels_list['names']

print("Number of Classes are {}, whose labels are {} for this Object Detection project".format(num_classes,label_names))
