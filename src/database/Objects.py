import sqlite3
from .tables.ObjectItem import ObjectItem
from typing import Optional


class Objects:

    def __init__(self, db_name: str = "data_db/objects.db"):
        self.connection = sqlite3.connect(db_name)
        query = '''
            CREATE TABLE IF NOT EXISTS Objects (
                ObjrecID INTEGER PRIMARY KEY AUTOINCREMENT,
                Name TEXT NOT NULL,
                Time TEXT,
                PositionCoord TEXT NOT NULL,
                ContID INTEGER NOT NULL,
                PhotoPath TEXT NOT NULL,
                FOREIGN KEY (ContID) REFERENCES Containers(ContID)
            )
        '''
        self.connection.execute(query)
        self.connection.commit()

    def create(self, item: ObjectItem) -> int:
        query = "INSERT INTO Objects (Name, Time, PositionCoord, ContID, PhotoPath) VALUES (?, ?, ?, ?, ?)"
        cursor = self.connection.cursor()
        cursor.execute(query, (item.Name, item.Time,
                       item.PositionCoord, item.ContID, item.PhotoPath))  # Исправлено здесь
        self.connection.commit()
        return cursor.lastrowid

    def read(self, obj_id: int) -> Optional[ObjectItem]:
        query = "SELECT * FROM Objects WHERE ObjrecID = ?"
        cursor = self.connection.cursor()
        cursor.execute(query, (obj_id,))
        row = cursor.fetchone()
        # Добавляем ObjrecID в создание ObjectItem
        return ObjectItem(
            Name=row[1],
            Time=row[2],
            PositionCoord=row[3],
            PhotoPath=row[5],
            ContID=row[4]
        ) if row else None

    def delete(self, obj_id: int) -> bool:
        query = "DELETE FROM Objects WHERE ObjrecID = ?"
        cursor = self.connection.cursor()
        cursor.execute(query, (obj_id,))
        self.connection.commit()
        return cursor.rowcount > 0