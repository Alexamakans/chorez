import sys
from chorez.chorez import Chorez
from chorez.cli.root_cli import RootCLI


def main(argv: list[str], *, chorez: Chorez) -> None:
    parsed = RootCLI().parse_args(argv)
    if hasattr(parsed, "run"):
        sys.exit(parsed.run(parsed, chorez))  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType, reportUnknownArgumentType]
    else:
        print(parsed)


if __name__ == "__main__":

    def mainlet() -> None:
        chorez = Chorez()
        main(sys.argv[1:], chorez=chorez)

    mainlet()
