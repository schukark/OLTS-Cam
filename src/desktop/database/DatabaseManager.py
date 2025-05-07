from Container import Container
from Record import Record
from Objects import Objects
from tables.ObjectItem import ObjectItem
import os
import json
import sqlite3
from typing import Optional, Dict, Any

class DatabaseManager:
    """Класс для управления подключением к базе данных SQLite"""
    
    def __init__(self, db_path: str = "data_db/database.db"):
        self.db_path = db_path
        self.connections = {}
        
        if not os.path.exists('data_db'):
            os.mkdir('data_db')
            
        self.db = {
            "Container": Container(db_path),
            "Record": Record(db_path),
            "Objects": Objects(db_path),
        }

    def get_latest_object_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Находит последнюю запись по имени в таблице Objects и возвращает объединенные данные
        с ContID и RecordID в виде JSON.
        
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
            
            # Получаем связанные данные из таблицы Records
            record_item = self.db["Record"].read(object_item.RecordID)
            
            # Формируем результат в виде словаря
            result = {
                "Object": {
                    "ObjrecID": object_item.ObjrecID,
                    "Name": object_item.Name,
                    "Time": object_item.Time,
                    "PositionCoord": object_item.PositionCoord,
                    "ContID": object_item.ContID,
                    "RecordID": object_item.RecordID,
                },
                "Container": {
                    "ContID": container_item.ContID if container_item else None,
                    "Name": container_item.Name if container_item else None,
                    "Position": container_item.Position if container_item else None,
                    "PhotoPath": container_item.PhotoPath if container_item else None,
                } if container_item else None,
                "Record": {
                    "RecordID": record_item.RecordID if record_item else None,
                    "VideoID": record_item.VideoID if record_item else None,
                    "StartTime": record_item.StartTime if record_item else None,
                    "EndTime": record_item.EndTime if record_item else None,
                    "VideoPath": record_item.VideoPath if record_item else None,
                } if record_item else None,
            }
            
            return result
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            if conn:
                conn.close()