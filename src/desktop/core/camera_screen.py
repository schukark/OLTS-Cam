import json
import os
import re
from pathlib import Path
from typing import Dict, Tuple, Optional
from PySide6.QtWidgets import QMessageBox

class CameraSettingsValidator:
    @staticmethod
    def validate_ip(ip: str) -> Tuple[bool, str]:
        """Валидация IP-адреса с обработкой всех возможных ошибок"""
        if not ip:
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

    @staticmethod
    def validate_port(port: str) -> Tuple[bool, str]:
        """Валидация порта"""
        if not port:
            return False, "Порт не может быть пустым"
        
        if not port.isdigit():
            return False, "Порт должен быть числом"
        
        port_num = int(port)
        if not 1 <= port_num <= 65535:
            return False, "Порт должен быть в диапазоне 1-65535"
        
        return True, ""

    @staticmethod
    def validate_rtsp_url(url: str) -> Tuple[bool, str]:
        """Валидация RTSP URL"""
        if not url:
            return False, "RTSP URL не может быть пустым"
        
        rtsp_pattern = r'^rtsp://[^\s/$.?#].[^\s]*$'
        if not re.match(rtsp_pattern, url, re.IGNORECASE):
            return False, "Неверный формат RTSP URL. Пример: rtsp://192.168.1.100:554/stream"
        
        return True, ""

    @staticmethod
    def validate_login(login: str) -> Tuple[bool, str]:
        """Валидация логина"""
        if not login:
            return False, "Логин не может быть пустым"
        return True, ""

class CameraScreen:
    SETTINGS_PATH = Path(__file__).parent.parent.parent / "settings" / "camera_settings.json"
    
    def __init__(self, ui):
        self.ui = ui
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
        
        if not self.SETTINGS_PATH.exists():
            with open(self.SETTINGS_PATH, 'w', encoding='utf-8') as f:
                json.dump(default_settings, f, ensure_ascii=False, indent=4)

    def setup_connections(self):
        """Подключение сигналов"""
        self.ui.saveCameraSettingsButton.clicked.connect(self.on_save_clicked)

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
        valid_rtsp, rtsp_error = self.validator.validate_rtsp_url(fields['rtsp_url'])
        if not valid_rtsp:
            self.highlight_error_field('rtspUrlInput')
            error += rtsp_error + "\n"
            has_errors = True

        # Проверка логина
        valid_login, login_error = self.validator.validate_login(fields['login'])
        if not valid_login:
            self.highlight_error_field('cameraLoginInput')
            error += login_error + "\n"
            has_errors = True

        if (has_errors):
            QMessageBox.warning(None, "Ошибка", error)
        
        
        return not has_errors, fields

    def on_save_clicked(self):
        """Обработчик сохранения с валидацией"""
        is_valid, settings = self.validate_all_fields()
        
        if not is_valid:
            return

        try:
            self.save_settings(settings)
            QMessageBox.information(None, "Успех", "Настройки успешно сохранены!")
        except Exception as e:
            QMessageBox.critical(None, "Ошибка", f"Ошибка сохранения: {str(e)}")

    def save_settings(self, settings: Dict[str, str]):
        """Сохраняет настройки в файл"""
        os.makedirs(self.SETTINGS_PATH.parent, exist_ok=True)
        with open(self.SETTINGS_PATH, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)

    def load_settings(self):
        """Загружает настройки из файла"""
        try:
            if self.SETTINGS_PATH.exists():
                with open(self.SETTINGS_PATH, 'r', encoding='utf-8') as f:
                    self.set_all_settings(json.load(f))
        except Exception as e:
            QMessageBox.warning(None, "Ошибка", f"Не удалось загрузить настройки: {str(e)}")