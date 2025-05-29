import base64
from io import BytesIO
import cv2
import torch
from torchvision.utils import draw_bounding_boxes
from torchvision.transforms.functional import to_pil_image
from .models import ObjectPhoto

def show_boxes(
    names: list[str],
    photo_paths: list[str],
    position_coords: list[str],
    output_path: str = "image.jpg"
) -> ObjectPhoto:
    """
    Рисует bounding boxes на изображении, сохраняет результат в файл и возвращает ObjectPhoto.

    Args:
        names: Список меток для bounding boxes.
        photo_paths: Список путей к изображениям.
        position_coords: Координаты в формате 'x_min,y_min,x_max,y_max'.
        output_path: Путь для сохранения результата (по умолчанию 'image.jpg').

    Returns:
        ObjectPhoto: Объект с высотой, шириной и base64-изображением.
    """

    coord_list = []
    for position_coord in position_coords:
        coords = position_coord.split(",")
        if len(coords) != 4:
            raise ValueError("Координаты должны быть в формате 'x_min,y_min,x_max,y_max'.")
        coord_list.append([float(x) for x in coords])

    image = cv2.imread(photo_paths[0])
    if image is None:
        raise FileNotFoundError(f"Изображение не найдено: {photo_paths[0]}")
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    h, w, _ = image.shape

    for box in coord_list:
        x_min, y_min, x_max, y_max = box
        assert 0 <= x_min < x_max <= w, f"Некорректные X-координаты: {box}"
        assert 0 <= y_min < y_max <= h, f"Некорректные Y-координаты: {box}"


    image_tensor = torch.from_numpy(image).permute(2, 0, 1).contiguous()
    boxes_tensor = torch.tensor(coord_list, dtype=torch.float32)

    boxed_img = draw_bounding_boxes(
        image_tensor,
        boxes=boxes_tensor,
        labels=names,
        colors="red",
        width=4,
        font_size=20
    )

    boxed_img_pil = to_pil_image(boxed_img)
    boxed_img_pil.save(output_path)

    buffered = BytesIO()
    boxed_img_pil.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue())

    return ObjectPhoto(height=h, width=w, image=img_str)
