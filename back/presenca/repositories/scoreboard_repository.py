from presenca.models import Scoreboard
from presenca.repositories import Repository


class ScoreboardRepository(Repository[Scoreboard]):
    model = Scoreboard

    @staticmethod
    def get_or_create(name: str) -> Scoreboard:
        scoreboard, _ = Scoreboard.objects.get_or_create(name=name)
        return scoreboard
