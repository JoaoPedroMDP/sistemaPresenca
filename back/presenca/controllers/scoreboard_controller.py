from presenca.models import Member, Score, Scoreboard


class ScoreboardController:
    @staticmethod
    def add_points(member: Member, board_name: str, points: float):
        scoreboard = Scoreboard.get_or_create_by_name(name=board_name)
        score = Score.get_or_create_for_board_and_member(scoreboard=scoreboard, member=member)
        score.add_points(points)
        
        return scoreboard
