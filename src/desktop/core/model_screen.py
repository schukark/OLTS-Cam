import json
import os
import re
from pathlib import Path
from typing import Dict, Tuple
from PySide6.QtWidgets import QMessageBox, QFileDialog


class ModelSettingsValidator:
    def validate_object_count(self, count: str) -> Tuple[bool, str]:
        """Валидация количества объектов"""
        if not count:
            return False, "Количество объектов не может быть пустым"

        try:
            count_num = int(count)
            if not 3 <= count_num <= 15:
                return False, "Количество объектов должно быть от 3 до 15"
            return True, ""
        except ValueError:
            return False, "Количество объектов должно быть целым числом"

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
    SETTINGS_PATH = Path(__file__).parent.parent.parent.parent / \
        "settings" / "model_settings.json"
    ENV_PATH = Path(__file__).parent.parent.parent.parent / ".env"

    def __init__(self, ui, window):
        self.ui = ui
        self.window = window
        self.validator = ModelSettingsValidator()
        self.setup_connections()
        self.current_token = self.load_current_token()  # Загружаем текущий токен

        # Создаем файл с настройками по умолчанию, если его нет
        tmp = Path(__file__).parent.parent.parent.parent / "camera"
        default_settings = {
            'telegram_token': '',
            'object_count': '',
            'fps': '',
            'threshold': '0.5',
            'save_folder': str(tmp),
        }

        # Создаем папку, если её не существует
        save_folder = Path(default_settings["save_folder"])
        if not save_folder.exists():
            save_folder.mkdir(parents=True, exist_ok=True)

        if not self.SETTINGS_PATH.exists():
            with open(self.SETTINGS_PATH, 'w', encoding='utf-8') as f:
                json.dump(default_settings, f, ensure_ascii=False, indent=4)

        self.load_settings()

    def load_current_token(self) -> str:
        """Загружает текущий токен из .env файла"""
        if self.ENV_PATH.exists():
            with open(self.ENV_PATH, 'r', encoding='utf-8') as f:
                for line in f:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
            return os.getenv('TELOXIDE_TOKEN', '')
        return ''

    def save_token_to_env(self, token: str):
        """Сохраняет токен в .env файл"""
        env_lines = []
        token_found = False
        
        # Читаем существующий файл, если он есть
        if self.ENV_PATH.exists():
            with open(self.ENV_PATH, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('TELOXIDE_TOKEN='):
                        env_lines.append(f'TELOXIDE_TOKEN={token}\n')
                        token_found = True
                    else:
                        env_lines.append(line)
        
        # Если токен не найден, добавляем новую строку
        if not token_found:
            env_lines.append(f'TELOXIDE_TOKEN={token}\n')
        
        # Записываем обратно в файл
        with open(self.ENV_PATH, 'w', encoding='utf-8') as f:
            f.writelines(env_lines)
        
        # Обновляем текущий токен
        self.current_token = token

    def setup_connections(self):
        """Подключение сигналов"""
        self.ui.saveModelSettingsButton.clicked.connect(self.on_save_clicked)
        self.ui.browseFolderButton.clicked.connect(self.on_browse_folder)
        self.ui.horizontalSlider.valueChanged.connect(
            self.on_threshold_changed)

    def on_threshold_changed(self, value):
        """Обработчик изменения значения слайдера"""
        threshold = value / 100.0  # Преобразуем 2-9 в 0.2-0.9
        self.ui.objectThresholdInput.setText(f"{threshold:.2f}")

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
            'telegram_token': self.ui.token.text().strip(),
            'object_count': self.ui.videoObjectCount.text().strip(),
            'fps': self.ui.fpsInput.text().strip(),
            'threshold': self.ui.objectThresholdInput.text().strip(),
            'save_folder': self.ui.saveFolderInput.text().strip(),
        }

    def set_all_settings(self, settings: Dict):
        """Устанавливает все настройки из словаря"""
        self.ui.token.setText(settings.get('telegram_token', ''))
        self.ui.videoObjectCount.setText(settings.get('object_count', ''))
        self.ui.fpsInput.setText(settings.get('fps', ''))

        # Устанавливаем значение порога и синхронизируем слайдер
        threshold = settings.get('threshold', '0.5')
        self.ui.objectThresholdInput.setText(threshold)
        try:
            slider_value = int(float(threshold) * 100)
            self.ui.horizontalSlider.setValue(slider_value)
        except ValueError:
            self.ui.horizontalSlider.setValue(50)  # Значение по умолчанию 0.5

        self.ui.saveFolderInput.setText(settings.get('save_folder', ''))

    def clear_highlight(self):
        """Убирает подсветку со всех полей"""
        for field in ['token', 'videoObjectCount', 'fpsInput',
                      'objectThresholdInput', 'saveFolderInput']:
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

        # Проверка количества объектов
        valid_count, count_error = self.validator.validate_object_count(
            settings['object_count'])
        if not valid_count:
            self.highlight_error_field('videoObjectCount')
            error_messages.append(count_error)
            has_errors = True

        # Проверка FPS
        valid_fps, fps_error = self.validator.validate_fps(settings['fps'])
        if not valid_fps:
            self.highlight_error_field('fpsInput')
            error_messages.append(fps_error)
            has_errors = True

        # Проверка порога
        valid_thresh, thresh_error = self.validator.validate_threshold(
            settings['threshold'])
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
            # Проверяем, изменился ли токен
            new_token = settings['telegram_token']
            if new_token and new_token != self.current_token:
                self.save_token_to_env(new_token)
            
            self.save_settings(settings)
            QMessageBox.information(
                None, "Успех", "Настройки модели успешно сохранены!")
        except Exception as e:
            QMessageBox.critical(
                None, "Ошибка", f"Не удалось сохранить настройки: {str(e)}")

    def save_settings(self, settings: Dict):
        """Сохраняет настройки в файл"""
        self.window.update_frame(None, None, "Загрузка видео")
        os.makedirs(self.SETTINGS_PATH.parent, exist_ok=True)
        with open(self.SETTINGS_PATH, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)

    def load_settings(self):
        """Загружает настройки из файла"""
        try:
            if self.SETTINGS_PATH.exists():
                with open(self.SETTINGS_PATH, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.set_all_settings(settings)
                    # Обновляем текущий токен при загрузке
                    self.current_token = settings.get('telegram_token', '')
        except Exception as e:
            QMessageBox.warning(
                None,
                "Ошибка загрузки",
                f"Не удалось загрузить настройки модели: \
                    {str(e)}\nБудут использованы значения по умолчанию."
            )