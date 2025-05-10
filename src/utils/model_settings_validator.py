import re
from typing import Tuple

class ModelSettingsValidator:
    """
    A validator class for model settings fields.
    
    Provides validation methods for object count, FPS, and threshold values.
    """

    def validate_object_count(self, count: str) -> Tuple[bool, str]:
        """
        Validates the object count.

        Args:
            count (str): The number of objects as a string.

        Returns:
            Tuple[bool, str]: A tuple where the first element is True if valid,
                              False otherwise, and the second element is the error message.
        """
        if not count:
            return False, "The number of objects cannot be empty."

        try:
            count_num = int(count)
            if not 3 <= count_num <= 15:
                return False, "The number of objects must be between 3 and 15."
            return True, ""
        except ValueError:
            return False, "The number of objects must be an integer."

    def validate_fps(self, fps: str) -> Tuple[bool, str]:
        """
        Validates the FPS value.

        Args:
            fps (str): Frames per second as a string.

        Returns:
            Tuple[bool, str]: A tuple where the first element is True if valid,
                              False otherwise, and the second element is the error message.
        """
        if not fps:
            return False, "FPS cannot be empty."

        try:
            fps_num = float(fps)
            if fps_num <= 0:
                return False, "FPS must be a positive number."
            return True, ""
        except ValueError:
            return False, "FPS must be a number."

    def validate_threshold(self, threshold: str) -> Tuple[bool, str]:
        """
        Validates the object identification threshold.

        Args:
            threshold (str): Threshold value as a string.

        Returns:
            Tuple[bool, str]: A tuple where the first element is True if valid,
                              False otherwise, and the second element is the error message.
        """
        if not threshold:
            return False, "Threshold cannot be empty."

        try:
            threshold_num = float(threshold)
            if not 0 <= threshold_num <= 1:
                return False, "Threshold must be between 0 and 1."
            return True, ""
        except ValueError:
            return False, "Threshold must be a number."