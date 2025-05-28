import json
import os
from pathlib import Path
from typing import Dict, Tuple
from PySide6.QtWidgets import QMessageBox, QFileDialog

from utils.model_settings_validator import ModelSettingsValidator


class ModelScreen:
    """
    UI logic for the model settings screen.

    Manages user interaction, validation, saving/loading of model settings,
    and environment token management.
    """

    SETTINGS_PATH = Path(__file__).parent.parent.parent.parent / "settings" / "model_settings.json"
    ENV_PATH = Path(__file__).parent.parent.parent.parent / ".env"

    def __init__(self, ui, window):
        """
        Initializes the model settings screen.

        Args:
            ui: The UI object with widgets.
            window: The main application window.
        """
        self.ui = ui
        self.window = window
        self.validator = ModelSettingsValidator()
        self.folder_update = False
        self.setup_connections()
        self.current_token = self.load_current_token()  # Load the current token

        # Create default settings file if it doesn't exist
        default_folder = Path(__file__).parent.parent.parent.parent / "camera"
        default_settings = {
            'telegram_token': '',
            'object_count': '',
            'fps': '',
            'threshold': '0.5',
            'save_folder': str(default_folder),
        }

        # Ensure the default save folder exists
        save_folder = Path(default_settings["save_folder"])
        if not save_folder.exists():
            save_folder.mkdir(parents=True, exist_ok=True)

        if not self.SETTINGS_PATH.exists():
            with open(self.SETTINGS_PATH, 'w', encoding='utf-8') as f:
                json.dump(default_settings, f, ensure_ascii=False, indent=4)

        self.load_settings()

    def load_current_token(self) -> str:
        """
        Loads the current token from the .env file.

        Returns:
            str: The loaded token or an empty string if not found.
        """
        if self.ENV_PATH.exists():
            with open(self.ENV_PATH, 'r', encoding='utf-8') as f:
                for line in f:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
            return os.getenv('TELOXIDE_TOKEN', '')
        return ''

    def save_token_to_env(self, token: str):
        """
        Saves the token to the .env file.

        Args:
            token (str): The new token to save.
        """
        env_lines = []
        token_found = False

        if self.ENV_PATH.exists():
            with open(self.ENV_PATH, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('TELOXIDE_TOKEN='):
                        env_lines.append(f'TELOXIDE_TOKEN={token}\n')
                        token_found = True
                    else:
                        env_lines.append(line)

        if not token_found:
            env_lines.append(f'TELOXIDE_TOKEN={token}\n')

        with open(self.ENV_PATH, 'w', encoding='utf-8') as f:
            f.writelines(env_lines)

        self.current_token = token

    def setup_connections(self):
        """
        Sets up signal-slot connections for UI interactions.
        """
        self.ui.saveModelSettingsButton.clicked.connect(self.on_save_clicked)
        self.ui.browseFolderButton.clicked.connect(self.on_browse_folder)
        self.ui.horizontalSlider.valueChanged.connect(self.on_threshold_changed)

    def on_threshold_changed(self, value):
        """
        Handles slider value changes.

        Args:
            value (int): Slider value (0-100).
        """
        threshold = value / 100.0
        self.ui.objectThresholdInput.setText(f"{threshold:.2f}")

    def on_browse_folder(self):
        """
        Opens a folder selection dialog to choose the save folder.
        """
        folder = QFileDialog.getExistingDirectory(
            None,
            "Select a folder for saving",
            str(Path.home()),
            QFileDialog.ShowDirsOnly
        )
        self.folder_update = True
        self.ui.saveFolderInput.setText(folder)

    def get_all_settings(self) -> Dict:
        """
        Retrieves all settings from the UI.

        Returns:
            Dict: A dictionary of all settings.
        """
        return {
            'telegram_token': self.ui.token.text().strip(),
            'object_count': self.ui.videoObjectCount.text().strip(),
            'fps': self.ui.fpsInput.text().strip(),
            'threshold': self.ui.objectThresholdInput.text().strip(),
            'save_folder': self.ui.saveFolderInput.text().strip(),
        }

    def is_focus(self):
        """Check focus for input fields"""
        return self.ui.videoObjectCount.hasFocus() or \
            self.ui.fpsInput.hasFocus() or  \
            self.ui.horizontalSlider.hasFocus() or  \
            self.folder_update or \
            self.ui.token.hasFocus()

    def set_all_settings(self, settings: Dict):
        """
        Populates the UI fields with settings.

        Args:
            settings (Dict): A dictionary of settings to apply.
        """
        
        # Не обновлять поля, если они в фокусе или была изменена папка
        if not self.is_focus():
            try:
                self.ui.videoObjectCount.blockSignals(True)
                self.ui.fpsInput.blockSignals(True)
                self.ui.horizontalSlider.blockSignals(True)
                self.ui.token.blockSignals(True)
                
                self.ui.token.setText(settings.get('telegram_token', ''))
                self.ui.videoObjectCount.setText(settings.get('object_count', ''))
                self.ui.fpsInput.setText(settings.get('fps', ''))
                threshold = settings.get('threshold', '0.5')
                self.ui.objectThresholdInput.setText(threshold)
                try:
                    slider_value = int(float(threshold) * 100)
                    self.ui.horizontalSlider.setValue(slider_value)
                except ValueError:
                    self.ui.horizontalSlider.setValue(50)  # Default to 0.5
                self.ui.saveFolderInput.setText(settings.get('save_folder', ''))
            finally:
                self.ui.videoObjectCount.blockSignals(False)
                self.ui.fpsInput.blockSignals(False)
                self.ui.horizontalSlider.blockSignals(False)
                self.ui.token.blockSignals(False)

    def clear_highlight(self):
        """
        Clears the red border highlight from all fields.
        """
        for field in ['token', 'videoObjectCount', 'fpsInput',
                      'objectThresholdInput', 'saveFolderInput']:
            getattr(self.ui, field).setStyleSheet("")

    def highlight_error_field(self, field_name: str):
        """
        Highlights a field with a red border.

        Args:
            field_name (str): The field name (UI element) to highlight.
        """
        getattr(self.ui, field_name).setStyleSheet("border: 1px solid red;")

    def validate_all_fields(self) -> Tuple[bool, Dict]:
        """
        Validates all fields and highlights any errors.

        Returns:
            Tuple[bool, Dict]: A tuple where the first element is True if all fields are valid,
                               False otherwise, and the second is the settings dictionary.
        """
        self.clear_highlight()
        settings = self.get_all_settings()
        has_errors = False
        error_messages = []

        valid_count, count_error = self.validator.validate_object_count(settings['object_count'])
        if not valid_count:
            self.highlight_error_field('videoObjectCount')
            error_messages.append(count_error)
            has_errors = True

        valid_fps, fps_error = self.validator.validate_fps(settings['fps'])
        if not valid_fps:
            self.highlight_error_field('fpsInput')
            error_messages.append(fps_error)
            has_errors = True

        valid_thresh, thresh_error = self.validator.validate_threshold(settings['threshold'])
        if not valid_thresh:
            self.highlight_error_field('objectThresholdInput')
            error_messages.append(thresh_error)
            has_errors = True

        if has_errors:
            QMessageBox.warning(
                None,
                "Validation Error",
                "\n".join(error_messages)
            )

        return not has_errors, settings

    def on_save_clicked(self):
        """
        Handles the save button click, validates fields, and saves settings if valid.
        """
        self.folder_update = False
        is_valid, settings = self.validate_all_fields()

        if not is_valid:
            return

        try:
            new_token = settings['telegram_token']
            if new_token and new_token != self.current_token:
                self.save_token_to_env(new_token)

            self.save_settings(settings)
            QMessageBox.information(
                None, "Success", "Model settings have been saved successfully!")
        except Exception as e:
            QMessageBox.critical(
                None, "Error", f"Failed to save settings: {str(e)}")

    def save_settings(self, settings: Dict):
        """
        Saves settings to a JSON file.

        Args:
            settings (Dict): The settings to save.
        """
        self.window.update_frame(None, None, "Loading video")
        os.makedirs(self.SETTINGS_PATH.parent, exist_ok=True)
        with open(self.SETTINGS_PATH, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)

    def load_settings(self):
        """
        Loads settings from the JSON file and applies them to the UI.
        """
        try:
            if self.SETTINGS_PATH.exists():
                with open(self.SETTINGS_PATH, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.set_all_settings(settings)
                    self.current_token = settings.get('telegram_token', '')
        except Exception as e:
            QMessageBox.warning(
                None,
                "Load Error",
                f"Failed to load model settings: {str(e)}\nDefault values will be used."
            )
