# model_runner.py
import os
import cv2
import torch
from threading import Thread, Lock, Event
from PySide6.QtGui import QImage
from time import sleep

from torchvision.models.detection import (
    SSDLite320_MobileNet_V3_Large_Weights as ModelWeights,
    ssdlite320_mobilenet_v3_large as model_create
)
from torchvision.utils import draw_bounding_boxes

import logging
from utils.logger import setup_logger
setup_logger(__name__)


class ModelRunner:
    """
    Handles the initialization of the object detection model, frame capture from
    the camera, and running predictions. Manages its own background thread to keep
    the latest frame ready for processing.
    """

    def __init__(self, settings):
        """
        Initializes the ModelRunner.

        Args:
            settings (dict): Configuration settings including camera and model parameters.
        """
        self.weights = ModelWeights.COCO_V1
        self.settings = settings
        self.capture = None
        self.model = None
        self.error_msg = None
        self.latest_frame = None
        self.frame_lock = Lock()
        self.frame_ready = Event()
        self._stop_event = Event()

        if self._init_model():
            try:
                self.capture_thread = Thread(target=self._capture_frames, daemon=True)
                self.capture_thread.start()
            except Exception as e:
                self.error_msg = f"Thread start failed: {str(e)}"

    def _init_model(self):
        """Initializes the model and video capture."""
        try:
            self.model = model_create(
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
        """Initializes the video capture stream."""
        if self.capture and self.capture.isOpened():
            self.capture.release()

        try:
            self.capture = cv2.VideoCapture(self.settings["rtsp_url"], cv2.CAP_FFMPEG)
            if self.capture.isOpened():
                self.capture.set(cv2.CAP_PROP_FPS, self.settings["fps"])
                self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                logging.debug("cv2 Capture is opened successfully")
                return True
            else:
                self.error_msg = "Failed to open video capture"
                logging.debug("Failed to create cv2 capture")
                return False
        except Exception as e:
            self.error_msg = f"Capture init error: {str(e)}"
            return False

    def _capture_frames(self):
        """Background thread function to continuously capture frames."""
        while not self._stop_event.is_set():
            try:
                if not self.capture or not self.capture.isOpened():
                    if not self._reconnect_capture():
                        sleep(0.1)
                        continue

                ret, frame = self.capture.read()
                if ret:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    with self.frame_lock:
                        self.latest_frame = frame_rgb
                        self.frame_ready.set()
                else:
                    self.error_msg = "Failed to read frame"
                    if not self._reconnect_capture():
                        sleep(0.1)
            except Exception as e:
                logging.error(f"Capture error: {e}")
                self._reconnect_capture()

    def _reconnect_capture(self):
        """Attempts to reconnect the video capture stream."""
        if self.capture:
            self.capture.release()
        return self._init_capture()

    def predict_boxes(self):
        """
        Runs inference on the latest captured frame.

        Returns:
            tuple or None: (img_tensor, boxes, labels) if successful, None otherwise.
        """
        logging.info("Predicting boxes")
        if not self.frame_ready.wait(timeout=5.0):
            self.error_msg = "No frames available yet (timeout)"
            return None

        with self.frame_lock:
            if self.latest_frame is None:
                logging.debug("Latest frame is None")
                self.error_msg = "No frames available"
                return None

            frame = self.latest_frame.copy()
            self.frame_ready.clear()
            logging.debug("Consumed latest frame")

        try:
            img_tensor = torch.from_numpy(frame).permute(2, 0, 1).float() / 255.0
            prediction = self.model([img_tensor])[0]
            labels = [self.weights.meta["categories"][i] for i in prediction["labels"]]
            logging.debug("Computed predictions and labels")
            return img_tensor, prediction["boxes"].detach(), labels
        except Exception as e:
            self.error_msg = f"Prediction error: {str(e)}"
            return None

    def show_boxes(self, img_tensor, boxes, labels):
        """
        Draws bounding boxes and labels on the image.

        Args:
            img_tensor (torch.Tensor): The original image tensor.
            boxes (torch.Tensor): Bounding box coordinates.
            labels (list): List of label strings.

        Returns:
            tuple: (original QImage, annotated QImage)
        """
        logging.info("Called show_boxes")
        try:
            img_np = (img_tensor.permute(1, 2, 0).detach().numpy() * 255).astype('uint8')

            if len(boxes) == 0:
                logging.debug("Received image with no boxes")
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
            logging.debug("Computed output image")

            h, w, ch = img_np.shape
            img_qimage = QImage(img_np.data, w, h, ch * w, QImage.Format_RGB888)
            box_qimage = QImage(box_img.data, w, h, ch * w, QImage.Format_RGB888)

            return img_qimage, box_qimage
        except Exception as e:
            self.error_msg = f"Box drawing error: {str(e)}"
            return None, None

    def release(self):
        """Stops the capture thread and releases resources."""
        self._stop_event.set()

        if hasattr(self, 'capture_thread') and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=1.0)
            logging.debug("Waiting for the capture thread to join")

        if hasattr(self, 'capture') and self.capture:
            self.capture.release()
            self.capture = None
            logging.debug("Released capture")

        self.model = None
