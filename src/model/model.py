import cv2
import torch
from torchvision.models.detection import \
    SSDLite320_MobileNet_V3_Large_Weights as SSDWeights
from torchvision.models.detection import ssdlite320_mobilenet_v3_large
from torchvision.utils import draw_bounding_boxes


class ModelRunner:
    model: ...
    capture: ...
    preprocess: ...
    weights: ...

    def __init__(self, rtsp_url: str):
        self.weights = SSDWeights.COCO_V1
        self.model = ssdlite320_mobilenet_v3_large(
            self.weights,
            detections_per_img=5,
            nms_thresh=0.3,
            score_thresh=0.7)
        self.model.eval()
        self.capture = cv2.VideoCapture(rtsp_url)
        self.capture.set(cv2.CAP_PROP_FPS, 10)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 3)

        if self.capture is None:
            raise ValueError("Can't open capture")

        self.preprocess = self.weights.transforms()

    def change_url(self, new_rtsp_url):
        self.capture = cv2.VideoCapture(new_rtsp_url)
        self.capture.set(cv2.CAP_PROP_FPS, 10)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 3)

    def predict(self):
        img = torch.from_numpy(self.__get_last_frame()).permute(2, 0, 1)

        batch = [self.preprocess(img)]

        prediction = self.model(batch)[0]
        labels = [self.weights.meta["categories"][i]
                  for i in prediction["labels"]]
        box = draw_bounding_boxes(img, boxes=prediction["boxes"],
                                  labels=labels,
                                  colors="red",
                                  width=4, font_size=30)
        im = box.detach().permute(1, 2, 0).numpy()

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
    cv2.imwrite("test.png", im)

    mr.exit()
