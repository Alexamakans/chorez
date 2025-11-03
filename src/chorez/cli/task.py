from typing import Self, override

from tap import Tap

from chorez.chorez import Chorez
from chorez.models import Difficulty, Priority, Task


class TaskShow(Tap):
    filter: str = "all"

    @override
    def configure(self) -> None:
        self.add_argument("--filter", dest="filter")  # pyright: ignore[reportUnknownMemberType]
        self.set_defaults(run=self.run)

    def run(self, args: Self, chorez: Chorez) -> None:
        tasks = chorez.db.list_tasks(args.filter)
        print(f"Found {len(tasks)} tasks:")
        for task in tasks:
            print(f"\t{task!r}")


class TaskAdd(Tap):
    name: str  # pyright: ignore[reportUninitializedInstanceVariable]
    priority: Priority = Priority.MEDIUM
    difficulty: Difficulty = Difficulty.MEDIUM
    tags: list[str] = []
    desc: str = ""

    @override
    def configure(self) -> None:
        self.add_argument("name", nargs="?", help="Task title/name")  # pyright: ignore[reportUnknownMemberType]
        self.add_argument("--name", "-n", dest="name", help="Task title/name")  # pyright: ignore[reportUnknownMemberType]
        self.add_argument(  # pyright: ignore[reportUnknownMemberType]
            "--priority",
            "-p",
            choices=[m.value for m in Priority],
            dest="priority",
            help=f"Priority ({', '.join(m.value for m in Priority)})",
        )
        self.add_argument(  # pyright: ignore[reportUnknownMemberType]
            "--difficulty",
            "-d",
            choices=[m.value for m in Difficulty],
            dest="difficulty",
            help=f"Difficulty ({', '.join(m.value for m in Difficulty)})",
        )
        self.add_argument(  # pyright: ignore[reportUnknownMemberType]
            "--tags",
            "-t",
            nargs="+",
            dest="tags",
            help="One or more tags (space-separated)",
        )

        self.add_argument(  # pyright: ignore[reportUnknownMemberType]
            "--desc",
            "-D",
            dest="desc",
            help="Description",
        )

        self.set_defaults(run=self.run)

    def run(self, args: Self, chorez: Chorez) -> None:
        print("running task.add")
        task = Task(
            name=args.name,
            priority=args.priority,
            difficulty=args.difficulty,
            tags=args.tags,
        )
        chorez.db.save_task(task)
        print("done")


class TaskCLI(Tap):
    def configure(self) -> None:
        self.add_subparsers(dest="subcommand", required=True, help="task subparsers")
        self.add_subparser("show", TaskShow)
        self.add_subparser("add", TaskAdd)
