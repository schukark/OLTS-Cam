# model_manager.py
from PySide6.QtGui import QImage
from model.model_runner import ModelRunner


class ModelManager:
    def __init__(self):
        self.model = ModelRunner()
        self.error_msg = None
        self.image1 = None  # QImage with boxes
        self.image2 = None  # QImage original

    def write_to_db(self):
        result = self.model.predict_boxes()
        
        if self.model.error_msg is not None:
            self.error_msg = self.model.error_msg
            return

        if result is None:
            self.error_msg = "Prediction failed"
            return

        img, boxes, labels = result
        
        if boxes is None or labels is None:
            self.error_msg = "No boxes detected"
            return

        self.image1, self.image2 = self.model.show_boxes(img, boxes, labels)
        if self.image1 is None or self.image2 is None:
            self.error_msg = "Failed to draw boxes"
        else:
            self.error_msg = None

    def get_error(self) -> str:
        return self.error_msg

    def get_images(self) -> tuple[QImage, QImage]:
        return self.image1, self.image2