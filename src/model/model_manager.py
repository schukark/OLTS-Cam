import time
from database.tables.ObjectItem import ObjectItem
from database.Objects import Objects
from model.model_runner import ModelRunner


class ModelManager:
    def __init__(self):
        self.model = ModelRunner()
        self.dbObject = Objects()

    def write_to_db(self):
        result = self.model.predict_boxes()

        if result is None:
            return None

        img, boxes, labels = result

        if boxes is None or labels is None:
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

        return self.model.show_boxes(img, boxes, labels)
