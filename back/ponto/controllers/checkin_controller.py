from ponto.controllers.ws_controller import WsController
from ponto.models import Member
from ponto.repositories.checkin_times_repository import TimeScoreRulesRepository
from ponto.controllers.scoreboard_controller import ScoreboardController
from ponto.repositories.checkin_repository import CheckinRepository

CHECKIN_BOARD = "Presença"
SABBATH_CLASS_EVENT = "Escola Sabatina"

class CheckinController:
    @staticmethod
    def checkin_sabbath(member: Member) -> float:
        checkin = CheckinRepository.create(member)
        WsController.sync_emit_member_checkin(member)

        points = TimeScoreRulesRepository.get_points_for_time_in_event(SABBATH_CLASS_EVENT, checkin.date.time())
        ScoreboardController.add_points(member=member, board_name=CHECKIN_BOARD, points=points)
        return points
