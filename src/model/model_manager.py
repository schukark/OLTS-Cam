import time
from database.tables.ObjectItem import ObjectItem
from database.Objects import Objects
from model.model_runner import ModelRunner


class ModelManager:
    def __init__(self):
        self.model = ModelRunner()
        self.dbObject = Objects()
        self.error_msg = None
        self.image1 = None
        self.image2 = None

    def write_to_db(self):
        result = self.model.predict_boxes()

        if result is None:
            self.error_msg = "Failed to get predictions"
            return

        img, boxes, labels = result

        if boxes is None or labels is None:
            self.error_msg = "Failed to get boxes"
            return

        tn = time.now()

        assert len(boxes) == len(labels)
        objects = [
            ObjectItem(
                Name=label,
                Time=tn,
                PositionCoord=box,
                ContID=0,
                RecordID=0
            )
            for (label, box) in zip(labels, boxes)
        ]

        for object in objects:
            self.dbObject.create(item=object)

        self.image1, self.image2 = self.model.show_boxes(img, boxes, labels)

    def get_error(self) -> str:
        return self.error_msg

    def get_images(self) -> tuple:
        return self.image1, self.image2
