from ponto.repositories.checkin_times_repository import TimeScoreRulesRepository
from ponto.controllers.scoreboard_controller import ScoreboardController
from ponto.repositories.checkin_repository import CheckinRepository

CHECKIN_BOARD = "Presença"
SABBATH_CLASS_EVENT = "Escola Sabatina"

class CheckinController:
    @staticmethod
    def checkin_sabbath(member):
        checkin = CheckinRepository.create(member)
        points = TimeScoreRulesRepository.get_points_for_time_in_event(SABBATH_CLASS_EVENT, checkin.date.time())
        ScoreboardController.add_points(member=member, board_name=CHECKIN_BOARD, points=points)
