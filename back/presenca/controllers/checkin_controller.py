from presenca.controllers.ws_controller import WsController
from presenca.repositories.event_repository import EventRepository
from presenca.models import CheckIn, Member
from presenca.repositories.checkin_times_repository import TimeScoreRulesRepository
from presenca.controllers.scoreboard_controller import ScoreboardController
from presenca.repositories.checkin_repository import CheckinRepository

CHECKIN_BOARD = "Presença"
SABBATH_CLASS_EVENT = "Escola Sabatina"

class CheckinController:
    @staticmethod
    def checkin_sabbath(member: Member) -> float:
        checkin = CheckinRepository.create(member)
        event = EventRepository.get(name=SABBATH_CLASS_EVENT)
        WsController.send_member_checkin_for_event(member, event)

        points = TimeScoreRulesRepository.get_points_for_time_in_event(SABBATH_CLASS_EVENT, checkin.date.time())
        ScoreboardController.add_points(member=member, board_name=CHECKIN_BOARD, points=points)
        return points

    @staticmethod
    def get_member_history(member: Member):
        return CheckIn.objects.filter(member=member).order_by("-date").all()
