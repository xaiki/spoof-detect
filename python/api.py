import os

from fastapi import FastAPI, WebSocket
from YOLOv6.yolov6.core.inferer import Inferer

import cv2

import yaml as YAML
import json
import csv

import ssl
import hashlib

from entity import read_entities
import imtool

app = FastAPI()

weights = './runs/train/exp27/weights/best_stop_aug_ckpt.pt'
device = 'cpu'
yaml = './data.yaml'
img_size = [640, 640]
half = False
conf_thres = 0.5
iou_thres = 0.45
classes = None
agnostic_nms = None
max_det = 1000
try:
    with open(yaml, 'r') as f:
        classes_data = YAML.safe_load(f.read())

    entities = read_entities('../data/entities.csv')

    certs = {}
    with os.scandir('../data/certs') as it:
        for entry in it:
            bco, ext = entry.name.split('.')
            if ext == 'cert':
                try:
                    cert_dict = ssl._ssl._test_decode_cert(entry.path)
                    with open(entry.path, 'r') as f:
                        cert_dict.update({
                            'fingerprint': hashlib.sha1(
                                ssl.PEM_cert_to_DER_cert(f.read())
                            ).hexdigest()
                        })
                except Exception as e:
                    print("Error decoding certificate: {:}".format(e))
                else:
                    name = entities[bco].name
                    certs.update({name: cert_dict})


    print(f'loaded {len(certs.keys())} certs, got {len(classes_data["names"])} classes')
    inferer = Inferer(weights, device, yaml, img_size, half)
except Exception as e:
    print('error', e)


@app.get("/")
async def root():
    return {"message": "API is working"}

@app.websocket("/ws")
async def websockets_cb(websocket: WebSocket):
    try:
        await websocket.accept()
        while True:
            data = await websocket.receive_text()
            img = imtool.read_base64(data)
            cv2.imwrite("debug.png", img)
            try:
                os.remove("debug.txt")
            except:
                pass

            inferer.load(img)
            ret = inferer.infer(conf_thres, iou_thres, classes, agnostic_nms, max_det)
            print(ret)
            await websocket.send_text(ret  + '@@@@' + '[%d,%d,%d]'%img.shape)
    except Exception as e:
        print("got: ", e)

@app.websocket("/bgws")
async def send_classes(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(json.dumps({
        'classes': classes_data,
        'certs': certs
}))
    await websocket.close()

if __name__ == "__main__":
    import uvicorn
    config = uvicorn.Config("api:app", port=5000, log_level="info")
    server = uvicorn.Server(config)
    server.run()
