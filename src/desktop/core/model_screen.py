import json
import os
from pathlib import Path
from typing import Dict, Tuple
from PySide6.QtWidgets import QMessageBox, QFileDialog


class ModelSettingsValidator:
    def validate_resolution(self, resolution: str) -> Tuple[bool, str]:
        """Валидация разрешения видео (формат: WIDTHxHEIGHT)"""
        if not resolution:
            return False, "Разрешение не может быть пустым"
        
        if 'x' not in resolution:
            return False, "Используйте формат: ШИРИНАxВЫСОТА (например: 1920x1080)"
        
        try:
            width, height = map(int, resolution.split('x'))
            if width <= 0 or height <= 0:
                return False, "Разрешение должно быть положительным числом"
            return True, ""
        except ValueError:
            return False, "Разрешение должно содержать только числа (например: 1920x1080)"

    def validate_fps(self, fps: str) -> Tuple[bool, str]:
        """Валидация количества кадров в секунду"""
        if not fps:
            return False, "FPS не может быть пустым"
        
        try:
            fps_num = float(fps)
            if fps_num <= 0:
                return False, "FPS должен быть положительным числом"
            return True, ""
        except ValueError:
            return False, "FPS должен быть числом"

    def validate_threshold(self, threshold: str) -> Tuple[bool, str]:
        """Валидация порога идентификации объектов"""
        if not threshold:
            return False, "Порог не может быть пустым"
        
        try:
            threshold_num = float(threshold)
            if not 0 <= threshold_num <= 1:
                return False, "Порог должен быть между 0 и 1"
            return True, ""
        except ValueError:
            return False, "Порог должен быть числом"


class ModelScreen:
    SETTINGS_PATH = Path(__file__).parent.parent.parent.parent / "settings" / "model_settings.json"
    
    def __init__(self, ui, window):
        self.ui = ui
        self.window = window
        self.validator = ModelSettingsValidator()
        self.setup_connections()
        self.load_settings()

        tmp = Path(__file__).parent.parent.parent.parent / "camera"
        # Создаем файл с настройками по умолчанию, если его нет
        default_settings = {
            'resolution': '1920x1080',
            'fps': '30',
            'threshold': '0.5',
            'save_folder': str(tmp),
            'save_video': True
        }

        # Создаем папку, если её не существует
        save_folder = Path(default_settings["save_folder"])
        if not save_folder.exists():
            save_folder.mkdir(parents=True, exist_ok=True)

        if not self.SETTINGS_PATH.exists():
            with open(self.SETTINGS_PATH, 'w', encoding='utf-8') as f:
                json.dump(default_settings, f, ensure_ascii=False, indent=4)

        self.load_settings()

    def setup_connections(self):
        """Подключение сигналов"""
        self.ui.saveModelSettingsButton.clicked.connect(self.on_save_clicked)
        self.ui.browseFolderButton.clicked.connect(self.on_browse_folder)

    def on_browse_folder(self):
        """Обработчик кнопки выбора папки"""
        folder = QFileDialog.getExistingDirectory(
            None,
            "Выберите папку для сохранения",
            str(Path.home()),
            QFileDialog.ShowDirsOnly
        )
        if folder:
            self.ui.saveFolderInput.setText(folder)

    def get_all_settings(self) -> Dict:
        """Получает все настройки в виде словаря"""
        return {
            'resolution': self.ui.videoResolutionInput.text().strip(),
            'fps': self.ui.fpsInput.text().strip(),
            'threshold': self.ui.objectThresholdInput.text().strip(),
            'save_folder': self.ui.saveFolderInput.text().strip(),
            'save_video': self.ui.saveVideoCheckbox.isChecked()
        }

    def set_all_settings(self, settings: Dict):
        """Устанавливает все настройки из словаря"""
        self.ui.videoResolutionInput.setText(settings.get('resolution', ''))
        self.ui.fpsInput.setText(settings.get('fps', ''))
        self.ui.objectThresholdInput.setText(settings.get('threshold', ''))
        self.ui.saveFolderInput.setText(settings.get('save_folder', ''))
        self.ui.saveVideoCheckbox.setChecked(settings.get('save_video', True))

    def clear_highlight(self):
        """Убирает подсветку со всех полей"""
        for field in ['videoResolutionInput', 'fpsInput', 'objectThresholdInput', 'saveFolderInput']:
            getattr(self.ui, field).setStyleSheet("")

    def highlight_error_field(self, field_name: str):
        """Подсвечивает поле с ошибкой"""
        getattr(self.ui, field_name).setStyleSheet("border: 1px solid red;")

    def validate_all_fields(self) -> Tuple[bool, Dict]:
        """Валидация всех полей с подсветкой ошибок"""
        self.clear_highlight()
        settings = self.get_all_settings()
        has_errors = False
        error_messages = []

        # Проверка разрешения
        valid_res, res_error = self.validator.validate_resolution(settings['resolution'])
        if not valid_res:
            self.highlight_error_field('videoResolutionInput')
            error_messages.append(res_error)
            has_errors = True

        # Проверка FPS
        valid_fps, fps_error = self.validator.validate_fps(settings['fps'])
        if not valid_fps:
            self.highlight_error_field('fpsInput')
            error_messages.append(fps_error)
            has_errors = True

        # Проверка порога
        valid_thresh, thresh_error = self.validator.validate_threshold(settings['threshold'])
        if not valid_thresh:
            self.highlight_error_field('objectThresholdInput')
            error_messages.append(thresh_error)
            has_errors = True

        if has_errors:
            QMessageBox.warning(
                None, 
                "Ошибка валидации", 
                "\n".join(error_messages)
            )
            
        return not has_errors, settings

    def on_save_clicked(self):
        """Обработчик сохранения настроек модели"""
        is_valid, settings = self.validate_all_fields()
        
        if not is_valid:
            return

        try:
            self.save_settings(settings)
            QMessageBox.information(None, "Успех", "Настройки модели успешно сохранены!")
        except Exception as e:
            QMessageBox.critical(None, "Ошибка", f"Не удалось сохранить настройки: {str(e)}")

    def save_settings(self, settings: Dict):
        """Сохраняет настройки в файл"""
        os.makedirs(self.SETTINGS_PATH.parent, exist_ok=True)
        with open(self.SETTINGS_PATH, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)
        self.window.screens['video'].stop_capture()

    def load_settings(self):
        """Загружает настройки из файла"""
        try:
            if self.SETTINGS_PATH.exists():
                with open(self.SETTINGS_PATH, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.set_all_settings(settings)
        except Exception as e:
            QMessageBox.warning(
                None,
                "Ошибка загрузки",
                f"Не удалось загрузить настройки модели: {str(e)}\nБудут использованы значения по умолчанию."
            )