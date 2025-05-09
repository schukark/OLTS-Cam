# model_runner.py
import os
import cv2
import torch
from threading import Thread, Lock, Event
from PySide6.QtGui import QImage
from time import sleep

from torchvision.models.detection import \
    SSDLite320_MobileNet_V3_Large_Weights as SSDWeights
from torchvision.models.detection import ssdlite320_mobilenet_v3_large
from torchvision.utils import draw_bounding_boxes


class ModelRunner:
    def __init__(self, settings):
        self.weights = SSDWeights.COCO_V1
        self.settings = settings
        self.capture = None
        self.model = None
        self.error_msg = None
        self.is_running = False
        self.latest_frame = None
        self.frame_lock = Lock()
        self.frame_ready = Event()
        self._should_stop = False
        
        flag = self._init_model()
        if flag:
            try:    
                self.capture_thread = Thread(target=self._capture_frames, daemon=True)
                self.capture_thread.start()
            except Exception as e:
                print("Thread ended/failed")

    def _init_model(self):
        try:
            self.model = ssdlite320_mobilenet_v3_large(
                weights=self.weights,
                detections_per_img=self.settings["detections_per_image"],
                nms_thresh=self.settings["nms_thresh"],
                score_thresh=self.settings["score_thresh"]
            )
            self.model.eval()
            return self._init_capture()
        except Exception as e:
            self.error_msg = f"Model init error: {str(e)}"
            return False

    def _init_capture(self):
        if self.capture and self.capture.isOpened():
            self.capture.release()

        self.capture = cv2.VideoCapture(self.settings["rtsp_url"], cv2.CAP_FFMPEG)
        if self.capture.isOpened():
            print(self.settings["fps"])
            self.capture.set(cv2.CAP_PROP_FPS, self.settings["fps"])
            self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        else:
            self.error_msg = "Failed to open video capture"
            return False
        return True

    def _capture_frames(self):
        while not self._should_stop:
            if not self.capture or not self.capture.isOpened():
                if not self._init_capture():
                    sleep(0.1)
                    continue

            try:
                ret, frame = self.capture.read()
                if ret:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    with self.frame_lock:
                        self.latest_frame = frame_rgb
                        self.frame_ready.set()
                else:
                    self.error_msg = "Failed to read frame"
                    sleep(0.1)
            except Exception as e:
                print(f"Поток завершился {e}")

    def predict_boxes(self):
        if not self.frame_ready.wait(timeout=5.0):
            self.error_msg = "No frames available yet (timeout)"
            return None

        with self.frame_lock:
            if self.latest_frame is None:
                self.error_msg = "No frames available"
                return None

            frame = self.latest_frame.copy()

        try:
            img_tensor = torch.from_numpy(frame).permute(2, 0, 1).float() / 255.0
            prediction = self.model([img_tensor])[0]
            labels = [self.weights.meta["categories"][i] for i in prediction["labels"]]
            return img_tensor, prediction["boxes"].detach(), labels
        except Exception as e:
            self.error_msg = f"Prediction error: {str(e)}"
            return None

    def show_boxes(self, img_tensor, boxes, labels):
        try:
            img_np = (img_tensor.permute(1, 2, 0).detach().numpy() * 255).astype('uint8')
            
            if len(boxes) == 0:
                h, w, ch = img_np.shape
                img_qimage = QImage(img_np.data, w, h, 3 * w, QImage.Format_RGB888)
                return img_qimage.copy(), img_qimage.copy()
            
            box_img = draw_bounding_boxes(
                torch.from_numpy(img_np).permute(2, 0, 1),
                boxes=boxes,
                labels=labels,
                colors="red",
                width=4,
                font_size=30,
                font=os.path.join(os.path.dirname(__file__), "arial.ttf")
            )
            box_img = box_img.permute(1, 2, 0).numpy()

            h, w, ch = img_np.shape
            img_qimage = QImage(img_np.data, w, h, 3 * w, QImage.Format_RGB888)
            box_qimage = QImage(box_img.data, w, h, 3 * w, QImage.Format_RGB888)

            return img_qimage, box_qimage
        except Exception as e:
            self.error_msg = f"Box drawing error: {str(e)}"
            return None, None

    def release(self):
        """Корректно завершает работу runner"""
        
        self._should_stop = True
        if hasattr(self, 'capture') and self.capture and self.capture.isOpened():
            self.capture.release()
        self.capture = None
        self.model = None