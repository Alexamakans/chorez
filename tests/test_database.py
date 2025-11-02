from chorez import models
from chorez.database import Database


def test_insert_and_retrieve_tasks():
    db = Database("test_sqlite.db")
    num_deleted = db.clear_tasks()
    print(f"deleted {num_deleted} old tasks")

    t = models.Task(
        tags=["asdf", "foo"],
        name="test task",
        description="this task is just a test task",
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
    assert tasks[0].description == t.description

    t.name = "changed name"
    db.save_task(t)
    assert t.id == 1

    tasks = db.list_tasks()
    assert len(tasks) == 1
    assert tasks[0].id == t.id
    assert tasks[0].tags == t.tags
    assert tasks[0].name == t.name
    assert tasks[0].description == t.description

    t2 = models.Task(
        tags=["some tag"],
        name="second task",
        description="quite the desc",
    )
    db.save_task(t2)
    assert t2.id == 2

    tasks = db.list_tasks()
    assert len(tasks) == 2
    assert tasks[1].id == 2
    assert tasks[1].tags == t2.tags
    assert tasks[1].name == t2.name
    assert tasks[1].description == t2.description
