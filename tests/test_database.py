from datetime import datetime, timedelta
import os
from chorez import models
from chorez.database import Database
import pytest


def test_insert_and_retrieve_tasks():
    db_file = "test_sqlite.db"
    try:
        if os.path.exists(db_file):
            os.remove(db_file)
        db = Database(db_file)
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
        # order is id desc
        assert tasks[0].id == 2
        assert tasks[0].tags == t2.tags
        assert tasks[0].name == t2.name
        assert tasks[0].desc == t2.desc

        t2.id = 3
        with pytest.raises(ValueError, match="ID mismatch"):
            db.save_task(t2)
    finally:
        if os.path.exists(db_file):
            os.remove(db_file)


def test_insert_task_and_time_entry():
    db_file = "test2_sqlite.db"
    try:
        if os.path.exists(db_file):
            os.remove(db_file)
        db = Database(db_file)
        t = models.Task(
            tags=["asdf", "foo"],
            name="test task",
            desc="this task is just a test task",
        )
        db.save_task(t)
        assert t.id == 1

        e = models.TimeEntry(
            task_id=t.id,
            start=datetime.now(),
        )
        db.save_time_entry(e)
        time_entries = db.list_time_entries()
        assert len(time_entries) == 1

        active_time_entries = db.list_time_entries("end IS NULL")
        assert len(active_time_entries) == 1

        inactive_time_entries = db.list_time_entries("end IS NOT NULL")
        assert len(inactive_time_entries) == 0

        e.end = e.start + timedelta(minutes=1)
        db.save_time_entry(e)

        active_time_entries = db.list_time_entries("end IS NULL")
        assert len(active_time_entries) == 0

        inactive_time_entries = db.list_time_entries("end IS NOT NULL")
        assert len(time_entries) == 1

        assert inactive_time_entries[0].duration() == timedelta(minutes=1)
    finally:
        if os.path.exists(db_file):
            os.remove(db_file)


def test_eager_loaded_time_entries_on_task():
    db_file = "test3_sqlite.db"
    try:
        if os.path.exists(db_file):
            os.remove(db_file)
        db = Database(db_file)
        t = models.Task(
            tags=[],
            name="ihavetimeentries",
            desc="",
        )
        db.save_task(t)
        assert t.id == 1

        e = models.TimeEntry(
            task_id=t.id,
            start=datetime.now(),
        )
        db.save_time_entry(e)

        time_entries = db.list_time_entries()
        assert len(time_entries) == 1

        task = db.list_tasks()[0]
        assert len(task.time_entries) == 1
        assert task.time_entries[0].id == 1
        assert task.time_entries[0].task_id == task.id

        e = models.TimeEntry(
            task_id=t.id,
            start=datetime.now(),
        )
        db.save_time_entry(e)
        task = db.list_tasks()[0]
        assert len(task.time_entries) == 2
        assert task.time_entries[0].task_id == task.id
        assert task.time_entries[1].task_id == task.id
    finally:
        if os.path.exists(db_file):
            os.remove(db_file)


def test_eager_loaded_task_on_time_entry():
    db_file = "test4_sqlite.db"
    try:
        if os.path.exists(db_file):
            os.remove(db_file)
        db = Database(db_file)
        t = models.Task(
            tags=[],
            name="ihavetimeentries",
            desc="",
        )
        db.save_task(t)
        assert t.id == 1

        e = models.TimeEntry(
            task_id=t.id,
            start=datetime.now(),
        )
        db.save_time_entry(e)
        time_entries = db.list_time_entries()
        assert len(time_entries) == 1
        assert time_entries[0].task is not None
        assert time_entries[0].task.id == time_entries[0].task_id
    finally:
        if os.path.exists(db_file):
            os.remove(db_file)
