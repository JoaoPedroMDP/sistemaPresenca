from presenca.repositories.score_repository import ScoreRepository
from presenca.repositories.scoreboard_repository import ScoreboardRepository
from presenca.models import Member


class ScoreboardController:
    @staticmethod
    def add_points(member: Member, board_name: str, points: float):
        scoreboard = ScoreboardRepository.get_or_create(name=board_name)
        score = ScoreRepository.get_or_create(scoreboard=scoreboard, member=member)
        ScoreRepository.add_points(score, points)
        
        return scoreboard
