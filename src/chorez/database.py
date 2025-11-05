from collections.abc import Sequence
from typing import Any, final

import sqlalchemy as sa
from sqlalchemy import event
from sqlalchemy.orm import InstrumentedAttribute, sessionmaker

from chorez import models


@final
class Database:
    def __init__(self, database: str, echo: bool = False):
        self.database: str = database
        self.engine: sa.Engine = sa.create_engine(
            f"sqlite:///{self.database}",
            echo=echo,
        )

        @event.listens_for(self.engine, "connect")
        def _set_sqlite_pragma(dbapi_conn, connection_record) -> None:  # pyright: ignore[reportUnknownParameterType, reportMissingParameterType]
            cursor = dbapi_conn.cursor()  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
            cursor.execute("PRAGMA foreign_keys=ON")  # pyright: ignore[reportUnknownMemberType]
            cursor.close()  # pyright: ignore[reportUnknownMemberType]

        self.Session = sessionmaker(self.engine, expire_on_commit=False)

        models.Base.metadata.create_all(self.engine)

    def save_task(self, task: models.Task) -> None:
        """
        Saves a task in the database.
        If the ID is specified and the task already exists, update it.

        The task's tags will be converted to lowercase and then sorted
        alphabetically in ascending order.
        """

        for i, tag in enumerate(task.tags):
            task.tags[i] = tag.lower()
        task.tags.sort()

        with self.Session() as session:
            state = sa.inspect(task)
            if state.transient or task.id is not None:
                existing = session.scalars(
                    sa.select(models.Task)
                    .where(
                        sa.and_(
                            _eq(models.Task.name, task.name),
                            _eq(models.Task.source_id, task.source_id),
                            _eq(models.Task.source_url, task.source_url),
                        )
                    )
                    .limit(1)
                ).first()

                if existing is not None:
                    if task.id is not None and task.id != existing.id:
                        raise ValueError("ID mismatch")
                    task.id = existing.id
                    _ = session.merge(task)
                else:
                    session.add(task)
            else:
                _ = session.merge(task)
            session.commit()

    def list_tasks(
        self,
        filter: str = "",
    ) -> Sequence[models.Task]:
        stmt = sa.select(models.Task)
        if filter:
            stmt = stmt.where(sa.text(filter))
        stmt = stmt.order_by(models.Task.id.desc())
        with self.Session() as session:
            return session.scalars(stmt).all()

    def clear_tasks(self, filter: str = "") -> int:
        with self.Session() as session:
            result = session.execute(
                sa.delete(models.Task).where(sa.text(filter)).returning(models.Task.id)
            )
            deleted = len(result.fetchall())
            session.commit()
            return deleted

    def save_time_entry(self, time_entry: models.TimeEntry) -> None:
        """
        Saves a time entry in the database.

        If the ID is specified and the time entry already exists, update it.
        """

        with self.Session() as session:
            state = sa.inspect(time_entry)
            if state.transient or time_entry.id is not None:
                existing = session.scalars(
                    sa.select(models.TimeEntry)
                    .where(
                        sa.or_(
                            _eq(models.TimeEntry.id, time_entry.id),
                            sa.and_(
                                _eq(models.TimeEntry.task_id, time_entry.task_id),
                                _eq(models.TimeEntry.start, time_entry.start),
                            ),
                        )
                    )
                    .limit(1)
                ).first()

                if existing is not None:
                    if time_entry.id is not None and time_entry.id != existing.id:
                        raise ValueError("ID mismatch")
                    time_entry.id = existing.id
                    _ = session.merge(time_entry)
                else:
                    session.add(time_entry)
            else:
                _ = session.merge(time_entry)
            session.commit()

    def list_time_entries(
        self,
        filter: str = "",
    ) -> Sequence[models.TimeEntry]:
        stmt = sa.select(models.TimeEntry)
        if filter:
            stmt = stmt.where(sa.text(filter))
        stmt = stmt.order_by(models.TimeEntry.start.desc())
        with self.Session() as session:
            return session.scalars(stmt).all()


def _eq(
    col: InstrumentedAttribute[Any] | sa.ColumnElement[Any],  # pyright: ignore[reportExplicitAny]
    val: Any,  # pyright: ignore[reportExplicitAny, reportAny]
) -> sa.ColumnElement[bool]:
    return col.is_(None) if val is None else col == val
