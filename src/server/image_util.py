import base64
from io import BytesIO
import cv2

import torch
from torchvision.utils import draw_bounding_boxes
from torchvision.transforms.functional import to_pil_image
from .models import ObjectPhoto


def show_boxes(names: list[str],
               photo_paths: list[str],
               position_coords: list[str]) -> ObjectPhoto:
    coord_list = []

    for position_coord in position_coords:
        coords = position_coord.split(",")

        if len(coords) != 4:
            return "There should be 4 numbers"

        coords_num = []

        for i in coords:
            try:
                coords_num.append(float(i))
            except Exception as e:
                return "There was an error parsing coords: " +\
                    e

        coord_list.append(coords_num)

    image = cv2.imread(photo_paths[0])
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    h, w, _ = image.shape

    print(torch.tensor(coord_list).shape)
    boxed_img = draw_bounding_boxes(torch.from_numpy(image).permute(2, 0, 1),
                                    boxes=torch.tensor(coord_list),
                                    labels=names,
                                    colors="red",
                                    width=4, font_size=30)

    image = to_pil_image(boxed_img, mode="RGB")

    buffered = BytesIO()

    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue())

    return ObjectPhoto(height=h, width=w, image=img_str)
