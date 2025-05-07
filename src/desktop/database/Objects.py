import sqlite3
from tables.ObjectItem import ObjectItem
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
                RecordID INTEGER NOT NULL,
                FOREIGN KEY (ContID) REFERENCES Containers(ContID),
                FOREIGN KEY (RecordID) REFERENCES Records(RecordID)
            )
        '''
        self.connection.execute(query)
        self.connection.commit()

    def create(self, item: ObjectItem) -> int:
        query = "INSERT INTO Objects (Name, PositionCoord, ContID, RecordID) VALUES (?, ?, ?, ?)"
        cursor = self.connection.cursor()
        cursor.execute(query, item)
        self.connection.commit()
        return cursor.lastrowid

    def read(self, obj_id: int) -> Optional[ObjectItem]:
        query = "SELECT * FROM Objects WHERE ObjrecID = ?"
        cursor = self.connection.cursor()
        cursor.execute(query, (obj_id,))
        row = cursor.fetchone()
        return ObjectItem(*row) if row else None

    def delete(self, obj_id: int) -> bool:
        query = "DELETE FROM Objects WHERE ObjrecID = ?"
        cursor = self.connection.cursor()
        cursor.execute(query, (obj_id,))
        self.connection.commit()
        return cursor.rowcount > 0