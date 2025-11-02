from tap import Tap
from chorez import models
from chorez.database import Database


class ArgParser(Tap):
    pass


def main() -> None:
    db = Database("test_sqlite.db")
    print("old", db.list_tasks())
    tbl = db.db["tasks"]
    tbl.drop()

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

    assert t["id"] == tasks[0]["id"]
    assert t["tags"] == tasks[0]["tags"]
    assert t["name"] == tasks[0]["name"]
    assert t["description"] == tasks[0]["description"]

    id = db.save_task(t)
    assert id == 1

    tasks = db.list_tasks()
    assert len(tasks) == 1

    t["id"] = None
    t["name"] = "second task"
    id = db.save_task(t)
    print("id 3", id)
    assert id == 2

    tasks = db.list_tasks()
    assert len(tasks) == 2
    assert tasks[1]["id"] == 2
    assert t["tags"] == tasks[1]["tags"]
    assert t["name"] == tasks[1]["name"]
    assert t["description"] == tasks[1]["description"]


if __name__ == "__main__":
    main()
