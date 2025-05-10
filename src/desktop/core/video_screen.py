from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QImage, QPixmap, QPainter, QColor, QFont
from PySide6.QtWidgets import QMessageBox
from pathlib import Path


class VideoSignals(QObject):
    """
    Signals for video operations.

    Attributes:
        error_occurred (Signal): Emitted when an error occurs, sends a string message.
        frame_ready (Signal): Emitted when a new frame is ready, sends two QImage objects.
    """
    error_occurred = Signal(str)
    frame_ready = Signal(QImage, QImage)


class VideoScreen:
    """
    A class to handle the display of video frames and errors within a QLabel.

    Attributes:
        SETTINGS_PATH (Path): Path to the camera settings file.
        ui: The UI object containing widgets (e.g., QLabel, CheckBoxModel).
        signals (VideoSignals): Object holding the PySide signals.
        cap: Placeholder for a future video capture object.
        is_running (bool): Flag indicating if video capture is running.
        current_image1 (QImage): Stores the primary video frame.
        current_image2 (QImage): Stores the processed/model video frame.
        current_pixmap (QPixmap): Current pixmap being displayed.
    """

    SETTINGS_PATH = Path(__file__).parent.parent.parent.parent / \
        "settings" / "camera_settings.json"

    def __init__(self, ui):
        """
        Initialize the VideoScreen with UI bindings and set up signals.

        Args:
            ui: The UI object with relevant widgets (video_label, CheckBoxModel, etc.).
        """
        self.ui = ui
        self.signals = VideoSignals()
        self.cap = None
        self.is_running = False
        self.current_image1 = None
        self.current_image2 = None
        self.current_pixmap = None
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """
        Initializes the UI components, applies styles, and sets resize behavior.
        """
        self.ui.video_label.resizeEvent = self.on_label_resize
        self.ui.video_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 20px;
                background-color: black;
                qproperty-alignment: AlignCenter;
            }
        """)

    def setup_connections(self):
        """
        Connects signals to their respective slots for frame updates and error handling.
        """
        self.signals.frame_ready.connect(self.update_frame)
        self.signals.error_occurred.connect(self.show_error)
        self.ui.CheckBoxModel.stateChanged.connect(
            self._update_displayed_image)

    def show_error(self, message):
        """
        Displays a critical error message box.

        Args:
            message (str): The error message to display.
        """
        QMessageBox.critical(self.ui.video_label, "Error", message)

    def on_label_resize(self, event):
        """
        Handles resizing of the video QLabel to maintain aspect ratio.

        Args:
            event: The resize event.
        """
        if self.current_pixmap:
            scaled_pixmap = self.current_pixmap.scaled(
                self.ui.video_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.ui.video_label.setPixmap(scaled_pixmap)
        event.accept()

    def update_frame(self, image1, image2, error_msg=None):
        """
        Updates the QLabel with new video frames or displays an error message.

        Args:
            image1 (QImage): The main frame image or None.
            image2 (QImage): The processed/model frame image or None.
            error_msg (str): An optional error message. If provided, overrides frame display.
        """
        if error_msg:
            self._show_error_message(error_msg)
            return

        self.current_image1 = image1
        self.current_image2 = image2
        self._update_displayed_image()

    def _show_error_message(self, message):
        """
        Displays an error message directly inside the QLabel as an overlay.

        Args:
            message (str): The error message to display.
        """
        pixmap = QPixmap(self.ui.video_label.size())
        pixmap.fill(Qt.black)

        painter = QPainter(pixmap)
        if message != "Loading video":
            painter.setPen(QColor(Qt.red))
        else:
            painter.setPen(QColor(Qt.white))
        painter.setFont(QFont("Arial", 16))
        painter.drawText(pixmap.rect(), Qt.AlignCenter, message)
        painter.end()

        self.ui.video_label.setPixmap(pixmap)

    def _update_displayed_image(self):
        """
        Internal method to decide which image to display based on the checkbox state.
        Displays either the original frame or the model-processed frame.
        """
        if self.current_image1 is None:
            return

        use_model_view = self.ui.CheckBoxModel.isChecked()
        image_to_show = self.current_image2 if (use_model_view and self.current_image2) else self.current_image1

        self.current_pixmap = QPixmap.fromImage(image_to_show)
        scaled_pixmap = self.current_pixmap.scaled(
            self.ui.video_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.ui.video_label.setPixmap(scaled_pixmap)
