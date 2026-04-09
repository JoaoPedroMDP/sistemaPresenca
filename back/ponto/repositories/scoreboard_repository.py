from ponto.models import Scoreboard


class ScoreboardRepository:
    @staticmethod
    def get_or_create(name: str) -> Scoreboard:
        scoreboard, _ = Scoreboard.objects.get_or_create(name=name)
        return scoreboard
