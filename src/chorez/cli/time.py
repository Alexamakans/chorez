from tap import Tap

from chorez.chorez import Chorez


class TimeCLI(Tap):
    def run(self, chorez: Chorez) -> None:
        print("ran time cli")
