from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QMessageBox
import json
from pathlib import Path
import cv2
from threading import Thread


class VideoSignals(QObject):
    error_occurred = Signal(str)
    frame_ready = Signal(QImage)

class VideoScreen:
    SETTINGS_PATH = Path(__file__).parent.parent.parent.parent / "settings" / "camera_settings.json"
            
    def __init__(self, ui):        
        self.ui = ui
        self.signals = VideoSignals()
        self.cap = None
        self.is_running = False
        self.setup_ui()
        self.setup_connections()
        # Убрали автоматический запуск захвата
        
    def setup_ui(self):
        """Инициализация интерфейса"""
        self.ui.video_label.resizeEvent = self.on_label_resize
        
    def setup_connections(self):
        """Подключение сигналов к слотам"""
        self.signals.frame_ready.connect(self.update_frame)
        self.signals.error_occurred.connect(self.show_error)
        
    def show_error(self, message):
        """Отображение ошибки"""
        QMessageBox.critical(self.ui.video_label, "Ошибка", message)
        
    def on_label_resize(self, event):
        """Обработчик изменения размера QLabel"""
        if hasattr(self, 'current_pixmap') and self.current_pixmap:
            scaled_pixmap = self.current_pixmap.scaled(
                self.ui.video_label.size(), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.ui.video_label.setPixmap(scaled_pixmap)
            self.ui.video_label.setAlignment(Qt.AlignCenter)
        event.accept()
        
    def update_frame(self, image):
        """Обновление изображения в QLabel с центрированием"""
        self.current_pixmap = QPixmap.fromImage(image)
        scaled_pixmap = self.current_pixmap.scaled(
            self.ui.video_label.size(), 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        self.ui.video_label.setPixmap(scaled_pixmap)
        self.ui.video_label.setAlignment(Qt.AlignCenter)
        
    def start_capture(self):
        """Запуск захвата видео (вызывается при переходе на экран)"""
        if not self.is_running:
            self.is_running = True
            thread = Thread(target=self.start_opencv_capture, daemon=True)
            thread.start()
        
    def stop_capture(self):
        """Остановка захвата видео (вызывается при уходе с экрана)"""
        self.is_running = False
        if self.cap and self.cap.isOpened():
            self.cap.release()
        if hasattr(self, 'thread') and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        
    def start_opencv_capture(self):
        """Запуск захвата видео через OpenCV"""
        rtsp_url = self.load_rtsp_url_from_settings()
        if not rtsp_url:
            return
            
        try:
            self.cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            if not self.cap.isOpened():
                raise ValueError("Не удалось открыть RTSP поток")
                
            self.thread = Thread(target=self.capture_frames, daemon=True)
            self.thread.start()
            
        except Exception as e:
            self.ui.video_label.setText(f"Ошибка захвата видео: {str(e)}")
            #self.signals.error_occurred.emit(f"Ошибка захвата видео: {str(e)}")
            
    def capture_frames(self):
        """Чтение и обработка кадров в отдельном потоке"""
        reconnect_attempts = 0
        max_reconnect_attempts = 5
        
        while self.is_running:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    reconnect_attempts += 1
                    if reconnect_attempts > max_reconnect_attempts:
                        self.signals.error_occurred.emit("Не удалось восстановить соединение с камерой")
                        break
                    
                    self.cap.release()
                    rtsp_url = self.load_rtsp_url_from_settings()
                    self.cap = cv2.VideoCapture(rtsp_url)
                    if not self.cap.isOpened():
                        continue
                    
                    reconnect_attempts = 0
                    continue
                
                reconnect_attempts = 0
                
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                qt_image = QImage(rgb_image.data, w, h, QImage.Format_RGB888)
                self.signals.frame_ready.emit(qt_image)
                cv2.waitKey(1)
                
            except Exception as e:
                #self.signals.error_occurred.emit(f"Ошибка обработки кадра: {str(e)}")
                break
            
    def load_rtsp_url_from_settings(self):
        """Загрузка RTSP URL из JSON-файла настроек"""
        self.ui.video_label.setText("Загрузка")
        try:
            if not self.SETTINGS_PATH.exists():
                error_msg = f"Файл настроек не найден: {self.SETTINGS_PATH}"
                self.ui.video_label.setText(error_msg)
                raise FileNotFoundError(error_msg)
                
            with open(self.SETTINGS_PATH, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                
            rtsp_url = settings.get("rtsp_url", "")
            print(f"Загружен RTSP URL: {rtsp_url}")  # Для отладки
            
            if not rtsp_url:
                error_msg = "RTSP URL не указан в настройках"
                self.ui.video_label.setText(error_msg)
                raise ValueError(error_msg)
                
            return rtsp_url
            
        except json.JSONDecodeError as e:
            error_msg = f"Ошибка чтения JSON: {str(e)}"
            self.ui.video_label.setText(error_msg)
            return None
        except Exception as e:
            error_msg = f"Не удалось загрузить настройки: {str(e)}"
            self.ui.video_label.setText(error_msg)
            return None
        