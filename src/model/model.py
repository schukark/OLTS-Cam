import cv2
from torchvision.io.image import decode_image
from torchvision.models.detection import \
    SSDLite320_MobileNet_V3_Large_Weights as SSDWeights
from torchvision.models.detection import ssdlite320_mobilenet_v3_large
from torchvision.transforms.functional import to_pil_image
from torchvision.utils import draw_bounding_boxes


class ModelRunner:
    model: ...
    capture: ...
    preprocess: ...
    weights: ...

    def __init__(self, rtsp_url: str):
        self.weights = SSDWeights.COCO_V1
        self.model = ssdlite320_mobilenet_v3_large(
            self.weights)
        self.capture = cv2.VideoCapture(rtsp_url)

        if self.capture is None:
            raise ValueError("Can't open capture")

        self.preprocess = self.weights.transforms()

    def change_url(self, new_rtsp_url):
        self.capture = cv2.VideoCapture(new_rtsp_url)

    def predict(self):
        last_frame = self.__get_last_frame()
        # img = decode_image(last_frame)

        # batch = [self.preprocess(img)]

        # prediction = self.model(batch)[0]
        # labels = [self.weights.meta["categories"][i]
        #           for i in prediction["labels"]]
        # box = draw_bounding_boxes(img, boxes=prediction["boxes"],
        #                           labels=labels,
        #                           colors="red",
        #                           width=4, font_size=30)
        # im = to_pil_image(box.detach())

        # return im

    def __get_last_frame(self):
        if not self.capture.isOpened():
            return None

        _ret, frame = self.capture.read()
        cv2.imshow('frame', frame)
        return frame

    def exit(self):
        self.capture.release()
        self.capture.destroyAllWindows()


if __name__ == "__main__":
    mr = ModelRunner("rtsp://:8554/video")
    im = mr.predict()

    # im.show()
