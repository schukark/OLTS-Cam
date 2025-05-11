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
    """
    This function reads an image, draws bounding boxes based on provided coordinates, 
    and returns the image as a base64-encoded JPEG. The function assumes that the coordinates
    are provided in the format: 'x_min,y_min,x_max,y_max'.

    Args:
        names (list[str]): A list of labels to assign to each bounding box.
        photo_paths (list[str]): A list of file paths to the images where bounding boxes are to be drawn.
        position_coords (list[str]): A list of bounding box coordinates in the format 'x_min,y_min,x_max,y_max'.

    Returns:
        ObjectPhoto: An ObjectPhoto instance containing the height, width, and base64-encoded image.
        
    Raises:
        ValueError: If there is an issue with parsing the coordinates.
    """
    coord_list = []

    # Parse the bounding box coordinates from the position_coords list
    for position_coord in position_coords:
        coords = position_coord.split(",")

        # Ensure that there are exactly 4 coordinates
        if len(coords) != 4:
            raise ValueError("There should be exactly 4 coordinates for each bounding box.")

        coords_num = []

        # Attempt to convert each coordinate to a float
        for i in coords:
            try:
                coords_num.append(float(i))
            except ValueError as e:
                raise ValueError(f"There was an error parsing coordinates: {e}")

        coord_list.append(coords_num)

    # Read the first image from the given paths
    image = cv2.imread(photo_paths[0])
    if image is None:
        raise FileNotFoundError(f"Could not load the image at {photo_paths[0]}")

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    h, w, _ = image.shape

    # Convert the image to a tensor and draw bounding boxes
    image_tensor = torch.from_numpy(image).permute(2, 0, 1).float()  # Convert to float tensor
    boxes_tensor = torch.tensor(coord_list)

    # Draw bounding boxes on the image tensor
    boxed_img = draw_bounding_boxes(image_tensor, 
                                    boxes=boxes_tensor, 
                                    labels=names, 
                                    colors="red", 
                                    width=4, 
                                    font_size=30)

    # Convert the result back to a PIL image
    image = to_pil_image(boxed_img, mode="RGB")

    # Convert the PIL image to a base64-encoded string
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue())

    # Return an ObjectPhoto instance containing the height, width, and the base64 image
    return ObjectPhoto(height=h, width=w, image=img_str)
