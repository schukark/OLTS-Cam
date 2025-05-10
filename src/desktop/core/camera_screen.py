import json
import os
import re
from pathlib import Path
from typing import Dict, Tuple
from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import QObject, Signal, QEvent
from utils.camera_settings_validator import CameraSettingsValidator

"""
Camera Settings Module

This module handles camera configuration, including IP, port, RTSP URL validation,
and persisting camera settings.

Classes:
    CameraSettingsValidator - Validates camera connection parameters.
    CameraScreen - Manages the camera settings UI and operations.
"""
class CameraScreen(QObject):
    """
    Manages camera settings UI and interactions, including saving/loading settings
    and validating user input.
    """
    SETTINGS_PATH = Path(__file__).parent.parent.parent.parent / "settings" / "camera_settings.json"

    def __init__(self, ui, window):
        super().__init__()
        self.ui = ui
        self.window = window
        self.validator = CameraSettingsValidator()
        self.setup_connections()

        default_settings = {
            'ip': '',
            'port': '',
            'login': '',
            'password': '',
            'rtsp_url': ''
        }

        settings_path = Path(__file__).parent.parent.parent.parent / "settings"
        settings_path.mkdir(parents=True, exist_ok=True)

        if not self.SETTINGS_PATH.exists():
            with open(self.SETTINGS_PATH, 'w', encoding='utf-8') as f:
                json.dump(default_settings, f, ensure_ascii=False, indent=4)

        self.load_settings()

    def setup_connections(self):
        """Connects UI signals to their respective handlers."""
        self.ui.saveCameraSettingsButton.clicked.connect(self.on_save_clicked)
        self.ui.cameraIPInput.textChanged.connect(self.update_rtsp_from_fields)
        self.ui.cameraPortInput.textChanged.connect(self.update_rtsp_from_fields)
        self.ui.cameraLoginInput.textChanged.connect(self.update_rtsp_from_fields)
        self.ui.cameraPasswordInput.textChanged.connect(self.update_rtsp_from_fields)
        self.ui.rtspUrlInput.textChanged.connect(self.update_fields_from_rtsp)

    def is_focus(self):
        """Check focus for input fields"""
        return self.ui.cameraIPInput.hasFocus() or \
            self.ui.cameraPortInput.hasFocus() or  \
            self.ui.cameraLoginInput.hasFocus() or  \
            self.ui.cameraPasswordInput.hasFocus() or \
            self.ui.rtspUrlInput.hasFocus() \

    def load_settings(self):
        """Loads settings from JSON file if not editing"""
        if self.SETTINGS_PATH.exists():
            try:
                with open(self.SETTINGS_PATH, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.set_all_settings(settings)
            except Exception as e:
                print(f"Error loading settings: {str(e)}")

    def update_rtsp_from_fields(self):
        """Updates RTSP URL based on individual field values using validator"""
        try:
            self.ui.rtspUrlInput.blockSignals(True)
            
            fields = {
                'ip': self.ui.cameraIPInput.text().strip(),
                'port': self.ui.cameraPortInput.text().strip(),
                'login': self.ui.cameraLoginInput.text().strip(),
                'password': self.ui.cameraPasswordInput.text().strip()
            }
            
            updated_fields = self.validator.update_rtsp_from_fields(fields)
            self.ui.rtspUrlInput.setText(updated_fields.get('rtsp_url', ''))
        finally:
            self.ui.rtspUrlInput.blockSignals(False)

    def update_fields_from_rtsp(self):
        """Parses RTSP URL and updates individual fields using validator"""
        try:
            self.ui.cameraIPInput.blockSignals(True)
            self.ui.cameraPortInput.blockSignals(True)
            self.ui.cameraLoginInput.blockSignals(True)
            self.ui.cameraPasswordInput.blockSignals(True)

            fields = {'rtsp_url': self.ui.rtspUrlInput.text().strip()}
            updated_fields = self.validator.update_fields_from_rtsp(fields)

            self.ui.cameraIPInput.setText(updated_fields.get('ip', ''))
            self.ui.cameraPortInput.setText(updated_fields.get('port', ''))
            self.ui.cameraLoginInput.setText(updated_fields.get('login', ''))
            self.ui.cameraPasswordInput.setText(updated_fields.get('password', ''))
        finally:
            self.ui.cameraIPInput.blockSignals(False)
            self.ui.cameraPortInput.blockSignals(False)
            self.ui.cameraLoginInput.blockSignals(False)
            self.ui.cameraPasswordInput.blockSignals(False)

    def get_all_settings(self) -> Dict[str, str]:
        """Returns all current settings as a dictionary"""
        return {
            'ip': self.ui.cameraIPInput.text().strip(),
            'port': self.ui.cameraPortInput.text().strip(),
            'login': self.ui.cameraLoginInput.text().strip(),
            'password': self.ui.cameraPasswordInput.text().strip(),
            'rtsp_url': self.ui.rtspUrlInput.text().strip()
        }

    def set_all_settings(self, settings: Dict[str, str]):
        """Applies settings from dictionary to UI fields"""
        if not self.is_focus():
            try:
                self.ui.cameraIPInput.blockSignals(True)
                self.ui.cameraPortInput.blockSignals(True)
                self.ui.cameraLoginInput.blockSignals(True)
                self.ui.cameraPasswordInput.blockSignals(True)
                self.ui.rtspUrlInput.blockSignals(True)

                self.ui.cameraIPInput.setText(settings.get('ip', ''))
                self.ui.cameraPortInput.setText(settings.get('port', ''))
                self.ui.cameraLoginInput.setText(settings.get('login', ''))
                self.ui.cameraPasswordInput.setText(settings.get('password', ''))
                self.ui.rtspUrlInput.setText(settings.get('rtsp_url', ''))
            finally:
                self.ui.cameraIPInput.blockSignals(False)
                self.ui.cameraPortInput.blockSignals(False)
                self.ui.cameraLoginInput.blockSignals(False)
                self.ui.cameraPasswordInput.blockSignals(False)
                self.ui.rtspUrlInput.blockSignals(False)

    def clear_highlight(self):
        """Removes error highlighting from all input fields"""
        for field in ['cameraIPInput', 'cameraPortInput', 'cameraLoginInput', 'rtspUrlInput']:
            getattr(self.ui, field).setStyleSheet("")

    def highlight_error_field(self, field_name: str):
        """Highlights the specified input field to indicate an error"""
        getattr(self.ui, field_name).setStyleSheet("border: 1px solid red;")

    def validate_all_fields(self):
        """
        Validates all fields and highlights any with errors.

        Returns:
            Tuple[bool, Dict[str, str]]: (is_valid, settings)
        """
        self.clear_highlight()
        fields = self.get_all_settings()
        has_errors = False
        error = ""

        valid_ip, ip_error = self.validator.validate_ip(fields['ip'])
        if not valid_ip:
            self.highlight_error_field('cameraIPInput')
            error += ip_error + "\n"
            has_errors = True

        valid_port, port_error = self.validator.validate_port(fields['port'])
        if not valid_port:
            self.highlight_error_field('cameraPortInput')
            error += port_error + "\n"
            has_errors = True

        valid_rtsp, rtsp_error = self.validator.validate_rtsp_url(fields['rtsp_url'])
        if not valid_rtsp:
            self.highlight_error_field('rtspUrlInput')
            error += rtsp_error + "\n"
            has_errors = True

        if has_errors:
            QMessageBox.warning(None, "Error", error)

        return not has_errors, fields

    def on_save_clicked(self):
        """Handles saving the settings after validation"""
        is_valid, settings = self.validate_all_fields()
        if not is_valid:
            return

        try:
            self.save_settings(settings)
            self.set_all_settings(settings)  # Явно обновляем UI
            QMessageBox.information(None, "Success", "Settings saved successfully!")
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to save settings: {str(e)}")

    def save_settings(self, settings: Dict[str, str]):
        """Saves the settings to a JSON file"""
        self.window.update_frame(None, None, "Loading video")
        os.makedirs(self.SETTINGS_PATH.parent, exist_ok=True)
        with open(self.SETTINGS_PATH, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)