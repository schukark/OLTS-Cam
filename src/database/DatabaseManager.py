from threading import Lock
from time import sleep
from Container import Container
from Objects import Objects
from tables.ObjectItem import ObjectItem
import os
import sqlite3
from typing import List, Optional, Dict, Any


class DatabaseManager:
    """Класс для управления подключением к базе данных SQLite"""

    def __init__(self, db_path: str = "data_db/database.db"):
        self.db_path = db_path
        self.connections = {}

        if not os.path.exists('data_db'):
            os.mkdir('data_db')

        self.db = {
            "Container": Container(db_path),
            "Objects": Objects(db_path),
        }

        self.object_queue: List[ObjectItem] = []
        self.lock = Lock()
        self.is_running = False

    def get_latest_object_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Находит последнюю запись по имени в таблице Objects и возвращает объединенные данные
        с ContID в виде JSON.

        Args:
            name: Имя объекта для поиска.

        Returns:
            Словарь с данными в формате JSON или None, если запись не найдена.
        """
        try:
            # Подключаемся к базе данных Objects
            conn = sqlite3.connect(f"{self.db_path}/database.db")
            cursor = conn.cursor()

            # Находим последнюю запись по имени (с максимальным Time)
            query = """
                SELECT * FROM Objects
                WHERE Name = ?
                ORDER BY Time DESC
                LIMIT 1
            """
            cursor.execute(query, (name,))
            object_row = cursor.fetchone()

            if not object_row:
                return None

            # Создаем объект ObjectItem из строки
            object_item = ObjectItem(*object_row)

            # Получаем связанные данные из таблицы Containers
            container_item = self.db["Container"].read(object_item.ContID)

            # Формируем результат в виде словаря
            result = {
                "Object": {
                    "ObjrecID": object_item.ObjrecID,
                    "Name": object_item.Name,
                    "Time": object_item.Time,
                    "PositionCoord": object_item.PositionCoord,
                    "ContID": object_item.ContID,
                    "PhotoPath": object_item.PhotoPath,
                },
                "Container": {
                    "ContID": container_item.ContID if container_item else None,
                    "Name": container_item.Name if container_item else None,
                    "PositionCoords": container_item.PositionCoords if container_item else None,
                    "PhotoPath": container_item.PhotoPath if container_item else None,
                } if container_item else None,
            }

            return result

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def push_objects(self, item: ObjectItem):
        try:
            self.lock.acquire()
            self.object_queue.append(item)
        finally:
            self.lock.release()

    def connect_and_push(self):
        try:
            self.lock.acquire()
            if self.object_queue == []:
                return

            dbObjects = Objects(db_name=self.db_path)
            for object in self.object_queue:
                try:
                    dbObjects.create(object)
                except sqlite3.Error as e:
                    print(f"Database error: {e}")
                    return None

            self.object_queue = []
        finally:
            self.lock.release()

    def stop_thread(self):
        try:
            self.lock.acquire()
            self.is_running = False
        finally:
            self.lock.release()

    def run(self):
        self.is_running = True

        while self.is_running:
            self.connect_and_push()
            sleep(5)
