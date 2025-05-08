# model_runner.py
import json
import os
import cv2
import torch
import numpy as np
from threading import Thread, Lock, Event
from PySide6.QtGui import QImage
from time import time, sleep

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
        self.latest_frame = None
        self.frame_lock = Lock()
        self.frame_ready = Event()  # Событие для сигнализации о наличии кадра
        self.set_model()
        
        # Запускаем поток для непрерывного захвата кадров
        self.capture_thread = Thread(target=self._capture_frames, daemon=True)
        self.capture_thread.start()

    def _get_settings(self):
        try:
            # Получаем абсолютный путь к директории текущего файла (model.py)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Поднимаемся на три уровня вверх (из src/model/ в корень проекта)
            project_root = os.path.dirname(os.path.dirname(current_dir))
            # Формируем полный путь к файлу настроек
            settings_path = os.path.join(project_root, "settings", "camera_settings.json")
            
            print(f"Looking for settings at: {settings_path}")  # Для отладки

            if not os.path.exists(settings_path):
                print("Settings file not found, using defaults")
                return {
                    "rtsp_url": "rtsp://:8554/video",
                    "fps": 15,
                    "nms_thresh": 0.3,
                    "score_thresh": 0.7,
                    "detections_per_image": 5
                }

            with open(settings_path, "r") as f:
                settings = json.load(f)
                return {
                    "rtsp_url": settings.get("rtsp_url", "rtsp://:8554/video"),
                    "fps": settings.get("fps", 15),
                    "nms_thresh": settings.get("nms_thresh", 0.3),
                    "score_thresh": settings.get("score_thresh", 0.7),
                    "detections_per_image": settings.get("detections_per_image", 5)
                }
        except Exception as e:
            self.error_msg = f"Settings error: {str(e)}"
            print(f"Error loading settings: {e}")  # Для отладки
            return {
                "rtsp_url": "rtsp://:8554/video",
                "fps": 15,
                "nms_thresh": 0.3,
                "score_thresh": 0.7,
                "detections_per_image": 5
            }

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
        print(self.settings["fps"])
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        if not self.capture.isOpened():
            self.error_msg = "Failed to open video capture"
            return False
        return True

    def _capture_frames(self):
        while True:
            if not self.capture or not self.capture.isOpened():
                if not self._init_capture():
                    sleep(0.05)  # Небольшая задержка перед повторной попыткой
                    continue

            ret, frame = self.capture.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                with self.frame_lock:
                    self.latest_frame = frame_rgb
                    self.frame_ready.set()  # Сигнализируем, что кадр доступен
            else:
                self.error_msg = "Failed to read frame"
                sleep(0.05)  # Небольшая задержка перед повторной попыткой
                continue

    def predict_boxes(self):
        # Ждем первый кадр в течение 5 секунд
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