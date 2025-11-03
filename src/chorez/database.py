from collections.abc import Sequence
from typing import Any, final
from sqlalchemy.orm import InstrumentedAttribute, sessionmaker
from chorez import models
import sqlalchemy as sa


@final
class Database:
    def __init__(self, database: str, echo: bool = False):
        self.database: str = database
        self.engine: sa.Engine = sa.create_engine(
            f"sqlite:///{self.database}",
            echo=echo,
        )
        self.Session = sessionmaker(self.engine, expire_on_commit=False)

        models.Base.metadata.create_all(self.engine)

    def save_task(self, task: models.Task) -> None:
        with self.Session() as session:
            state = sa.inspect(task)
            if state.transient or task.id is not None:
                existing = session.scalars(
                    sa.select(models.Task)
                    .where(
                        sa.and_(
                            models.Task.name == task.name,
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

    def list_tasks(self, filter: str = "all") -> Sequence[models.Task]:
        tasks: Sequence[models.Task]
        with self.Session() as session:
            tasks = session.scalars(
                sa.select(models.Task).order_by(models.Task.id)
            ).all()
        return tasks

    def clear_tasks(self) -> int:
        with self.Session() as session:
            result = session.execute(sa.delete(models.Task).returning(models.Task.id))
            deleted = len(result.fetchall())
            session.commit()
            return deleted


def _eq(
    col: InstrumentedAttribute[Any] | sa.ColumnElement[Any],  # pyright: ignore[reportExplicitAny]
    val: Any,  # pyright: ignore[reportExplicitAny, reportAny]
) -> sa.ColumnElement[bool]:
    return col.is_(None) if val is None else col == val
