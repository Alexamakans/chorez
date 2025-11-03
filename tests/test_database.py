import os
from chorez import models
from chorez.database import Database
import pytest


def test_insert_and_retrieve_tasks():
    if os.path.exists("test_sqlite.db"):
        os.remove("test_sqlite.db")
    db = Database("test_sqlite.db")
    num_deleted = db.clear_tasks()
    print(f"deleted {num_deleted} old tasks")

    t = models.Task(
        tags=["asdf", "foo"],
        name="test task",
        desc="this task is just a test task",
    )

    print(t)
    db.save_task(t)
    print(t)
    assert t.id == 1

    tasks = db.list_tasks()
    assert len(tasks) == 1
    assert tasks[0].id == t.id
    assert tasks[0].tags == t.tags
    assert tasks[0].name == t.name
    assert tasks[0].desc == t.desc

    t.name = "changed name"
    db.save_task(t)
    assert t.id == 1

    tasks = db.list_tasks()
    assert len(tasks) == 1
    assert tasks[0].id == t.id
    assert tasks[0].tags == t.tags
    assert tasks[0].name == t.name
    assert tasks[0].desc == t.desc

    t2 = models.Task(
        tags=["some tag"],
        name="second task",
        desc="quite the desc",
    )
    db.save_task(t2)
    assert t2.id == 2

    tasks = db.list_tasks()
    assert len(tasks) == 2
    assert tasks[1].id == 2
    assert tasks[1].tags == t2.tags
    assert tasks[1].name == t2.name
    assert tasks[1].desc == t2.desc

    t2.id = 3
    with pytest.raises(ValueError, match="ID mismatch"):
        db.save_task(t2)
