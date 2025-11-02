import dataset
from chorez import models
import sqlalchemy as sa


class Database:
    def __init__(self, database: str):
        self.database: str = database
        self.db: dataset.Database = dataset.connect(f"sqlite:///{self.database}")

    # returns true when upserted
    def save_task(self, task: models.Task) -> int:
        tbl = self.db["tasks"]
        res = tbl.upsert(task, keys=["id"], ensure=True, types={"tags": sa.JSON()})  # pyright: ignore[reportUnknownMemberType]
        if res is True:
            print("res was true")
            return task["id"]
        print("returning raw res")
        return res  # primary key value

    def list_tasks(self) -> list[models.Task]:
        tbl = self.db["tasks"]
        results: list[models.Task] = []
        for e in tbl.find():
            results.append(models.Task(**e))
        return results
