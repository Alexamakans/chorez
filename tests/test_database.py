from chorez import models
from chorez.database import Database


def test_insert_and_retrieve_tasks():
    db = Database("test_sqlite.db")
    t = models.Task(
        id=1,
        tags=["asdf", "foo"],
        name="test task",
        description="this task is just a test task",
    )

    id = db.save_task(t)
    assert id == 1

    tasks = db.list_tasks()
    assert len(tasks) == 1

    id = db.save_task(t)
    assert id == 1

    tasks = db.list_tasks()
    assert len(tasks) == 1
