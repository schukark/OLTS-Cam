from typing import Optional
import sqlite3
from .tables.ContainerItem import ContainerItem


class Container:

    def __init__(self, db_name: str = "data_db/container.db"):
        self.connection = sqlite3.connect(db_name)
        query = '''
            CREATE TABLE IF NOT EXISTS Containers (
                ContID INTEGER PRIMARY KEY AUTOINCREMENT,
                Name TEXT NOT NULL,
                PositionCoords TEXT,
                PhotoPath TEXT
            )
        '''
        self.connection.execute(query)
        self.connection.commit()

    def create(self, item: ContainerItem) -> int:
        query = "INSERT INTO Containers (Name, PositionCoords, PhotoPath) VALUES (?, ?, ?)"
        cursor = self.connection.cursor()
        cursor.execute(
            query, (item.Name, item.PositionCoords, item.PositionCoords))
        self.connection.commit()
        return cursor.lastrowid

    def read(self, cont_id: int) -> Optional[ContainerItem]:
        query = "SELECT * FROM Containers WHERE ContID = ?"
        cursor = self.connection.cursor()
        cursor.execute(query, (cont_id,))
        row = cursor.fetchone()
        return ContainerItem(*row) if row else None

    def update(self, cont_id: int,
               name: Optional[str] = None,
               position: Optional[str] = None,
               photo_path: Optional[str] = None) -> bool:
        updates = []
        params = []
        if name:
            updates.append("Name = ?")
            params.append(name)
        if position:
            updates.append("PositionCoords = ?")
            params.append(position)
        if photo_path:
            updates.append("PhotoPath = ?")
            params.append(photo_path)

        if not updates:
            return False

        params.append(cont_id)
        query = f"UPDATE Containers SET {', '.join(updates)} WHERE ContID = ?"
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        self.connection.commit()
        return cursor.rowcount > 0

    def delete(self, cont_id: int) -> bool:
        query = "DELETE FROM Containers WHERE ContID = ?"
        cursor = self.connection.cursor()
        cursor.execute(query, (cont_id,))
        self.connection.commit()
        return cursor.rowcount > 0
