import sqlite3
import dataset
from chorez import settings
from chorez.models import Task



class Database:
    def __init__(self):
        self.database: str = settings.DatabaseSettings.sqlite.database
        self.db: dataset.Database = dataset.connect(f"sqlite:///{self.database}")


    def insert_task(self, task: Task) -> None:
        self.db["tasks"]

    def list_tasks(self) -> list[Task]:
        c = self.conn.cursor()
        c.fetchall(
            # TODO
