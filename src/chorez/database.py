from collections.abc import Sequence
from typing import final
from sqlalchemy.orm import sessionmaker
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
            if state.transient:
                session.add(task)
            else:
                _ = session.merge(task)
            session.commit()

    def list_tasks(self) -> Sequence[models.Task]:
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
