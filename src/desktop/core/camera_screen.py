import json
import os
import re
from pathlib import Path
from typing import Dict, Tuple
from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import QObject, Signal


class CameraSettingsValidator:
    def validate_ip(self, ip: str) -> Tuple[bool, str]:
        """Валидация IP-адреса с обработкой всех возможных ошибок"""
        if not ip or ip == "":
            return False, "IP-адрес не может быть пустым"

        ip = ip.strip()

        # Проверка на строку "aaa" или другие нечисловые значения
        if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
            return False, "Неверный формат IP-адреса. Пример: 192.168.1.1"

        octets = ip.split('.')
        if len(octets) != 4:
            return False, "IP-адрес должен содержать 4 октета"

        for octet in octets:
            if not octet.isdigit():
                return False, "Каждый октет должен быть числом"

            num = int(octet)
            if not 0 <= num <= 255:
                return False, "Каждый октет должен быть от 0 до 255"

            if len(octet) > 1 and octet[0] == '0':
                return False, "Октет не должен содержать ведущих нулей"

        return True, ""

    def validate_port(self, port: str) -> Tuple[bool, str]:
        """Валидация порта (может быть пустым)"""
        if not port:
            return True, ""

        if not port.isdigit():
            return False, "Порт должен быть числом"

        port_num = int(port)
        if not 1 <= port_num <= 65535:
            return False, "Порт должен быть в диапазоне 1-65535"

        return True, ""

    def validate_rtsp_url(self, url: str) -> Tuple[bool, str]:
        """Валидация RTSP URL"""
        if not url:
            return False, "RTSP URL не может быть пустым"

        rtsp_pattern = r'^rtsp://(?:[^:@/]+(?::[^@/]+)?@)?[^:/]+(?::\d+)?(?:/.*)?$'
        if not re.match(rtsp_pattern, url, re.IGNORECASE):
            return False, "Неверный формат RTSP URL. Пример: rtsp://admin:12345@8.8.8.8:554/stream"

        return True, ""

    def validate_login(self, login: str) -> Tuple[bool, str]:
        """Валидация логина (может быть пустым)"""
        return True, ""


class CameraScreen:
    SETTINGS_PATH = Path(__file__).parent.parent.parent.parent / \
        "settings" / "camera_settings.json"

    def __init__(self, ui, window):
        self.ui = ui
        self.window = window
        self.validator = CameraSettingsValidator()
        self.setup_connections()
        self.load_settings()

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

    def setup_connections(self):
        """Подключение сигналов"""
        self.ui.saveCameraSettingsButton.clicked.connect(self.on_save_clicked)
        
        # Подключаем обработчики изменений полей
        self.ui.cameraIPInput.textChanged.connect(self.update_rtsp_from_fields)
        self.ui.cameraPortInput.textChanged.connect(self.update_rtsp_from_fields)
        self.ui.cameraLoginInput.textChanged.connect(self.update_rtsp_from_fields)
        self.ui.cameraPasswordInput.textChanged.connect(self.update_rtsp_from_fields)
        self.ui.rtspUrlInput.textChanged.connect(self.update_fields_from_rtsp)

    def update_rtsp_from_fields(self):
        """Обновляет RTSP URL на основе отдельных полей"""
        # Временно отключаем обработчик, чтобы избежать рекурсии
        self.ui.rtspUrlInput.blockSignals(True)
        
        ip = self.ui.cameraIPInput.text().strip()
        port = self.ui.cameraPortInput.text().strip()
        login = self.ui.cameraLoginInput.text().strip()
        password = self.ui.cameraPasswordInput.text().strip()
        
        if ip:
            # Формируем базовую часть URL
            if login and (not password or password == ""):
                rtsp_url = f"rtsp://{login}@{ip}"
            if login and password:
                rtsp_url = f"rtsp://{login}:{password}@{ip}"
            else:
                rtsp_url = f"rtsp://{ip}"
            
            # Добавляем порт, если он указан
            if port:
                rtsp_url += f":{port}"
            
            # Добавляем путь к потоку
            rtsp_url += "/stream"
            self.ui.rtspUrlInput.setText(rtsp_url)
        else:
            self.ui.rtspUrlInput.setText("")
        
        # Включаем обработчик обратно
        self.ui.rtspUrlInput.blockSignals(False)

    def update_fields_from_rtsp(self):
        """Извлекает значения из RTSP URL в отдельные поля"""
        # Временно отключаем обработчики, чтобы избежать рекурсии
        self.ui.cameraIPInput.blockSignals(True)
        self.ui.cameraPortInput.blockSignals(True)
        self.ui.cameraLoginInput.blockSignals(True)
        self.ui.cameraPasswordInput.blockSignals(True)
        
        rtsp_url = self.ui.rtspUrlInput.text().strip()
        
        # Очищаем поля перед заполнением
        self.ui.cameraLoginInput.setText("")
        self.ui.cameraPasswordInput.setText("")
        self.ui.cameraPortInput.setText("")
        self.ui.cameraIPInput.setText("")
        
        # Улучшенный парсинг RTSP URL
        pattern = r'^rtsp://(?:([^:]+)(?::([^@]+))?@)?([^:/]+)(?::(\d+))?(?:/(.*))?$'
        match = re.match(pattern, rtsp_url)
        
        if match:
            login, password, ip, port, path = match.groups()
            
            if ip:
                self.ui.cameraIPInput.setText(ip)
            if port:
                self.ui.cameraPortInput.setText(port)
            if login:
                self.ui.cameraLoginInput.setText(login)
            if password:
                self.ui.cameraPasswordInput.setText(password)
        
        # Включаем обработчики обратно
        self.ui.cameraIPInput.blockSignals(False)
        self.ui.cameraPortInput.blockSignals(False)
        self.ui.cameraLoginInput.blockSignals(False)
        self.ui.cameraPasswordInput.blockSignals(False)

    def get_all_settings(self) -> Dict[str, str]:
        """Получает все настройки в виде словаря"""
        return {
            'ip': self.ui.cameraIPInput.text().strip(),
            'port': self.ui.cameraPortInput.text().strip(),
            'login': self.ui.cameraLoginInput.text().strip(),
            'password': self.ui.cameraPasswordInput.text().strip(),
            'rtsp_url': self.ui.rtspUrlInput.text().strip()
        }

    def set_all_settings(self, settings: Dict[str, str]):
        """Устанавливает все настройки из словаря"""
        self.ui.cameraIPInput.setText(settings.get('ip', ''))
        self.ui.cameraPortInput.setText(settings.get('port', ''))
        self.ui.cameraLoginInput.setText(settings.get('login', ''))
        self.ui.cameraPasswordInput.setText(settings.get('password', ''))
        self.ui.rtspUrlInput.setText(settings.get('rtsp_url', ''))

    def clear_highlight(self):
        """Убирает подсветку со всех полей"""
        for field in ['cameraIPInput', 'cameraPortInput',
                      'cameraLoginInput', 'rtspUrlInput']:
            getattr(self.ui, field).setStyleSheet("")

    def highlight_error_field(self, field_name: str):
        """Подсвечивает поле с ошибкой"""
        getattr(self.ui, field_name).setStyleSheet("border: 1px solid red;")

    def validate_all_fields(self):
        """Валидация всех полей с подсветкой ошибок"""
        self.clear_highlight()
        fields = self.get_all_settings()
        has_errors = False
        error = ""

        # Проверка IP (теперь с обработкой всех ошибок)
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

        # Проверка RTSP URL
        valid_rtsp, rtsp_error = self.validator.validate_rtsp_url(
            fields['rtsp_url'])
        if not valid_rtsp:
            self.highlight_error_field('rtspUrlInput')
            error += rtsp_error + "\n"
            has_errors = True

        if has_errors:
            QMessageBox.warning(None, "Ошибка", error)

        return not has_errors, fields

    def on_save_clicked(self):
        """Обработчик сохранения с валидацией"""
        is_valid, settings = self.validate_all_fields()

        if not is_valid:
            return

        try:
            self.save_settings(settings)
            QMessageBox.information(
                None, "Успех", "Настройки успешно сохранены!")
        except Exception as e:
            QMessageBox.critical(
                None, "Ошибка", f"Ошибка сохранения: {str(e)}")

    def save_settings(self, settings: Dict[str, str]):
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
                    self.set_all_settings(json.load(f))
        except Exception:
            pass