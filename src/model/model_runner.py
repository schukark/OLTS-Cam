# model_runner.py
import json
import os
import cv2
import torch
import numpy as np
from threading import Thread
from PySide6.QtGui import QImage

from torchvision.models.detection import \
    SSDLite320_MobileNet_V3_Large_Weights as SSDWeights
from torchvision.models.detection import ssdlite320_mobilenet_v3_large
from torchvision.utils import draw_bounding_boxes


class ModelRunner:
    def __init__(self):
        self.weights = SSDWeights.COCO_V1
        self.settings = self._get_settings()
        self.capture = None
        self.model = None
        self.error_msg = None
        self.is_running = False
        self.set_model()

    def _get_settings(self):
        try:
            if not os.path.exists("../../settings/camera_settings.json"):
                return {
                    "rtsp_url": "rtsp://:8554/video",
                    "fps": 30,
                    "nms_thresh": 0.3,
                    "score_thresh": 0.7,
                    "detections_per_image": 5
                }

            with open("../../settings/camera_settings.json", "r") as f:
                settings = json.load(f)
                return {
                    "rtsp_url": settings.get("rtsp_url", "rtsp://:8554/video"),
                    "fps": settings.get("fps", 30),
                    "nms_thresh": settings.get("nms_thresh", 0.3),
                    "score_thresh": settings.get("score_thresh", 0.7),
                    "detections_per_image": settings.get("detections_per_image", 5)
                }
        except Exception as e:
            self.error_msg = f"Settings error: {str(e)}"
            return {}

    def set_model(self):
        try:
            self.model = ssdlite320_mobilenet_v3_large(
                weights=self.weights,
                detections_per_img=self.settings["detections_per_image"],
                nms_thresh=self.settings["nms_thresh"],
                score_thresh=self.settings["score_thresh"]
            )
            self.model.eval()
            self._init_capture()
        except Exception as e:
            self.error_msg = f"Model init error: {str(e)}"

    def _init_capture(self):
        if self.capture and self.capture.isOpened():
            self.capture.release()

        self.capture = cv2.VideoCapture(self.settings["rtsp_url"], cv2.CAP_FFMPEG)
        self.capture.set(cv2.CAP_PROP_FPS, self.settings["fps"])
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 3)

        if not self.capture.isOpened():
            self.error_msg = "Failed to open video capture"
            return False
        return True

    def predict_boxes(self):
        frame = self._get_frame()
        if frame is None:
            self.error_msg = "Failed to get frame"
            return None

        try:
            img_tensor = torch.from_numpy(frame).permute(2, 0, 1).float() / 255.0
            prediction = self.model([img_tensor])[0]
            labels = [self.weights.meta["categories"][i] for i in prediction["labels"]]
            return img_tensor, prediction["boxes"].detach(), labels
        except Exception as e:
            self.error_msg = f"Prediction error: {str(e)}"
            return None

    def _get_frame(self):
        if not self.capture or not self.capture.isOpened():
            if not self._init_capture():
                return None

        ret, frame = self.capture.read()
        if not ret:
            self.error_msg = "Failed to read frame"
            return None

        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def show_boxes(self, img_tensor, boxes, labels):
        try:
            # Convert tensor to numpy and scale to 0-255
            img_np = (img_tensor.permute(1, 2, 0).detach().numpy() * 255).astype('uint8')
            
            # Skip drawing if no boxes
            if len(boxes) == 0:
                h, w, ch = img_np.shape
                img_qimage = QImage(img_np.data, w, h, 3 * w, QImage.Format_RGB888)
                return img_qimage.copy(), img_qimage.copy()  # Return same image twice if no boxes
            
            # Draw bounding boxes
            box_img = draw_bounding_boxes(
                torch.from_numpy(img_np).permute(2, 0, 1),
                boxes=boxes,
                labels=labels,
                colors="red",
                width=4,
                font_size=30,
                font=os.path.join(os.path.dirname(__file__), "arial.ttf")  # Path to font file
            )
            box_img = box_img.permute(1, 2, 0).numpy()

            # Convert to QImage
            h, w, ch = img_np.shape
            img_qimage = QImage(img_np.data, w, h, 3 * w, QImage.Format_RGB888)
            box_qimage = QImage(box_img.data, w, h, 3 * w, QImage.Format_RGB888)

            return img_qimage, box_qimage
        except Exception as e:
            self.error_msg = f"Box drawing error: {str(e)}"
            return None, None

    def release(self):
        if self.capture and self.capture.isOpened():
            self.capture.release()