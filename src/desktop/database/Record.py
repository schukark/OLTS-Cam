from typing import Optional
import sqlite3
from tables.RecordItem import RecordItem

class Record:

    def __init__(self, db_name: str = "data_db/record.db"):
        self.connection = sqlite3.connect(db_name)
        query = '''
            CREATE TABLE IF NOT EXISTS Records (
                RecordID INTEGER PRIMARY KEY AUTOINCREMENT,
                VideoID INTEGER,
                StartTime TEXT,
                EndTime TEXT,
                VideoPath TEXT
            )
        '''
        self.connection.execute(query)
        self.connection.commit()

    def create(self, item: RecordItem) -> int:
        query = "INSERT INTO Records (VideoID, StartTime, EndTime, VideoPath) VALUES (?, ?, ?, ?)"
        cursor = self.connection.cursor()
        cursor.execute(query, item)
        self.connection.commit()
        return cursor.lastrowid

    def read(self, record_id: int) -> Optional[RecordItem]:
        query = "SELECT * FROM Records WHERE RecordID = ?"
        cursor = self.connection.cursor()
        cursor.execute(query, (record_id,))
        row = cursor.fetchone()
        return RecordItem(*row) if row else None

    def delete(self, record_id: int) -> bool:
        query = "DELETE FROM Records WHERE RecordID = ?"
        cursor = self.connection.cursor()
        cursor.execute(query, (record_id,))
        self.connection.commit()
        return cursor.rowcount > 0