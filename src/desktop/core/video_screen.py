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
    SETTINGS_PATH = Path(__file__).parent.parent.parent / "settings" / "camera_settings.json"
            
    def __init__(self, ui):        
        self.ui = ui
        self.signals = VideoSignals()
        self.cap = None
        self.is_running = False
        self.setup_ui()
        self.setup_connections()
        thread2 = Thread(target=self.start_opencv_capture, daemon=True)
        thread2.start()
    
    def setup_ui(self):
        """Инициализация интерфейса с исправлениями для правильного отображения"""
      
        # Создаем новый QLabel с правильными настройками
        
        #self.video_label = QLabel()
        #self.video_label.setAlignment(Qt.AlignCenter)
        #self.video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        #self.video_label.setMinimumSize(1000, 700)
        #self.video_label.setScaledContents(False)
        
        # Добавляем QLabel в layout и устанавливаем растягивание
        #self.ui.verticalLayout_5.addWidget(self.video_label, stretch=1)
        #self.ui.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        #self.ui.verticalLayout_5.setSpacing(0)
        
        # Установка обработчика изменения размера
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
            # Центрируем изображение с сохранением пропорций
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
        
    def start_opencv_capture(self):
        """Запуск захвата видео через OpenCV"""
        rtsp_url = self.load_rtsp_url_from_settings()
        if not rtsp_url:
            return
            
        try:
            # Установка параметров для лучшей работы с RTSP
            self.cap = cv2.VideoCapture(rtsp_url)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)  # Уменьшение буфера
            self.cap.set(cv2.CAP_PROP_FPS, 30)        # Установка FPS
            
            if not self.cap.isOpened():
                raise ValueError("Не удалось открыть RTSP поток")
                
            self.is_running = True
            # Запускаем отдельный поток для чтения кадров
            self.thread = Thread(target=self.capture_frames, daemon=True)
            self.thread.start()
            
        except Exception as e:
            self.signals.error_occurred.emit(f"Ошибка захвата видео: {str(e)}")
            
    def capture_frames(self):
        """Чтение и обработка кадров в отдельном потоке"""
        reconnect_attempts = 0
        max_reconnect_attempts = 5
        frame_counter = 0
        
        while self.is_running:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    reconnect_attempts += 1
                    if reconnect_attempts > max_reconnect_attempts:
                        self.signals.error_occurred.emit("Не удалось восстановить соединение с камерой")
                        break
                    
                    # Попробовать переподключиться
                    self.cap.release()
                    rtsp_url = self.load_rtsp_url_from_settings()
                    self.cap = cv2.VideoCapture(rtsp_url)
                    if not self.cap.isOpened():
                        continue
                    
                    reconnect_attempts = 0
                    continue
                
                # Сброс счетчика попыток переподключения при успешном чтении кадра
                reconnect_attempts = 0
                
                # Конвертируем кадр в QImage
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                
                # Отправляем кадр в основной поток (не чаще 30 FPS)
                frame_counter += 1
                if frame_counter % 2 == 0:  # Можно регулировать частоту обновления
                    self.signals.frame_ready.emit(qt_image)
                
                # Небольшая задержка для снижения нагрузки
                cv2.waitKey(1)
                
            except Exception as e:
                self.signals.error_occurred.emit(f"Ошибка обработки кадра: {str(e)}")
                break
            
        
    def load_rtsp_url_from_settings(self):
        """Загрузка RTSP URL из JSON-файла настроек"""
        try:
            if not self.SETTINGS_PATH.exists():
                raise FileNotFoundError(f"Файл настроек не найден: {self.SETTINGS_PATH}")
                
            with open(self.SETTINGS_PATH, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                
            rtsp_url = settings.get("rtsp_url", "")
            if not rtsp_url:
                raise ValueError("RTSP URL не указан в настройках")
                
            return rtsp_url
            
        except Exception as e:
            self.signals.error_occurred.emit(f"Не удалось загрузить настройки: {str(e)}")
            return None
            
    def stop_capture(self):
        """Остановка захвата видео"""
        self.is_running = False
        if self.cap and self.cap.isOpened():
            self.cap.release()
        if hasattr(self, 'thread') and self.thread.is_alive():
            self.thread.join(timeout=1.0)