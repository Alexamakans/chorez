from typing import override
from tap import Tap
from chorez.cli.task import TaskCLI
from chorez.cli.time import TimeCLI


class RootCLI(Tap):
    @override
    def configure(self) -> None:
        self.add_subparsers(dest="cmd", required=True, help="subcommands")  # pyright: ignore[reportUnknownMemberType]
        self.add_subparser("task", TaskCLI)  # pyright: ignore[reportUnknownMemberType]
        self.add_subparser("time", TimeCLI)  # pyright: ignore[reportUnknownMemberType]
