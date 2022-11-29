import warnings
warnings.filterwarnings('ignore')
from utils.general import check_img_size, non_max_suppression, scale_coords
from models.experimental import attempt_load
from utils.torch_utils import select_device
from utils.detections import Detections
from utils.datasets import letterbox
import numpy as np
import torch
import yaml


class YOLOv7:
    def __init__(self):
        self.settings = {
            'conf_thres':0.25,
            'iou_thres':0.45,
            'img_size':640
        }

    def load(self, weights_path, classes, device='cpu'):
        with torch.no_grad():
            self.device = select_device(device)
            print('DEVICE:', self.device)
            self.model = attempt_load(weights_path, device=self.device)
            if self.device != 'cpu':
                self.model.half()
                self.model.to(self.device).eval()
            stride = int(self.model.stride.max())
            self.imgsz = check_img_size(self.settings['img_size'], s=stride)
            self.classes = yaml.load(open(classes), Loader=yaml.SafeLoader)['classes']

    def unload(self):
        if self.device.type != 'cpu':
            torch.cuda.empty_cache()

    def set(self, **config):
        for key in config.keys():
            if key in self.settings.keys():
                self.settings[key] = config[key]
            else:
                raise Exception(f'{key} is not a valid inference setting')

    def __parse_image(self, img):
        im0 = img.copy()
        img = letterbox(im0, self.imgsz, auto=self.imgsz != 1280)[0]
        img = img[:, :, ::-1].transpose(2, 0, 1)
        img = np.ascontiguousarray(img)
        img = torch.from_numpy(img).to(self.device)
        img = img.half() if self.device.type != 'cpu' else img.float()
        img /= 255.0

        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        return im0, img

    def detect(self, img):
        with torch.no_grad():
            im0, img = self.__parse_image(img)
            pred = self.model(img)[0]
            pred = non_max_suppression(pred, self.settings['conf_thres'], self.settings['iou_thres'])
            raw_detection = np.empty((0,6), float)

            for det in pred:
                if len(det) > 0:
                    det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

                    for *xyxy, conf, cls in reversed(det):
                        raw_detection = np.concatenate((raw_detection, [[int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3]), round(float(conf), 2), int(cls)]]))

            detections = Detections(raw_detection, self.classes)
            return detections.to_dict()