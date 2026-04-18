from presenca.models import Score
from presenca.repositories import Repository


class ScoreRepository(Repository[Score]):
    model = Score

    @staticmethod
    def get_or_create(scoreboard, member):
        score, _ = Score.objects.get_or_create(board=scoreboard, member=member)
        return score

    @staticmethod
    def add_points(score: Score, points: float):
        score.points += points
        score.save()
