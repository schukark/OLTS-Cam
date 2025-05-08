import json
import os
import time
import cv2
import torch

from torchvision.models.detection import \
    SSDLite320_MobileNet_V3_Large_Weights as SSDWeights
from torchvision.models.detection import ssdlite320_mobilenet_v3_large
from torchvision.utils import draw_bounding_boxes
from torchvision.transforms.functional import to_pil_image

from ..database.Objects import Objects
from ..database.tables.ObjectItem import ObjectItem


def _get_settings():
    if not os.path.exists("../../settings/camera_settings.json"):
        settings = {}
    else:
        with open("../../setings/camera_settings.json", "r") as settings_file:
            settings = json.load(settings_file)

    return {
        "rtsp_url": settings.get("rtsp_url", "rtsp://:8554/video"),
        "fps": settings.get("fps", 30),
        "nms_thresh": settings.get("nms_thresh", 0.3),
        "score_thresh": settings.get("score_thresh", 0.7),
        "detections_per_image": settings.get("detections_per_image", 5)
    }


class ModelRunner:
    model: ...
    capture: ...
    preprocess: ...
    weights: ...
    dbObject: ...
    settings: ...

    def __init__(self, rtsp_url: str):
        self.weights = SSDWeights.COCO_V1
        self.settings = _get_settings()

        self.set_model()

        self.capture = cv2.VideoCapture(rtsp_url)
        self.capture.set(cv2.CAP_PROP_FPS, 10)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 3)

        self.dbObject = Objects()

        if self.capture is None:
            raise ValueError("Can't open capture")

        self.preprocess = self.weights.transforms()

    def set_model(self):
        self.model = ssdlite320_mobilenet_v3_large(
            self.weights,
            detections_per_img=self.settings["detections_per_image"],
            nms_thresh=self.settings["nms_thresh"],
            score_thresh=self.settings["score_thresh"])
        self.model.eval()

        self.capture = cv2.VideoCapture(self.settings["rtsp_url"])
        self.capture.set(cv2.CAP_PROP_FPS, self.settings["fps"])
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 3)

    def predict_boxes(self):
        self.set_model

        img = torch.from_numpy(self.__get_last_frame()).permute(2, 0, 1)

        batch = [self.preprocess(img)]

        prediction = self.model(batch)[0]
        labels = [self.weights.meta["categories"][i]
                  for i in prediction["labels"]]

        return img, prediction["boxes"].detach(), labels

    def predict_and_push(self):
        _img, boxes, labels = self.predict_boxes()

        if boxes is None or labels is None:
            return

        assert len(boxes) == len(labels)

        time_now = time.now()

        objects = [
            ObjectItem(
                ObjrecID=0,
                Name=label,
                Time=time_now,
                PositionCoord=box,
                ContID=0,
                RecordID=0,
            )

            for (label, box) in zip(labels, boxes)
        ]

        for object in objects:
            self.dbObject.create(item=object)

    def show_boxes(self):
        img, boxes, labels = self.predict_boxes()
        img = img.permute(1, 2, 0)

        box = draw_bounding_boxes(img, boxes=boxes,
                                  labels=labels,
                                  colors="red",
                                  width=4, font_size=30)

        im = to_pil_image(box.detach())
        return im

    def __get_last_frame(self):
        # return read_image("dog_bike_car.jpg")
        if not self.capture.isOpened():
            return None

        _ret, frame = self.capture.read()
        return frame

    def exit(self):
        self.capture.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    mr = ModelRunner("rtsp://:8554/video")
    im = mr.predict()
    # cv2.imwrite("test.png", im)
    print(im)

    mr.exit()
