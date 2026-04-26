from datetime import datetime
import logging

from presenca.controllers.ws_controller import WsController
from presenca.repositories.event_repository import EventRepository
from presenca.models import CheckIn, Event, Member
from presenca.repositories.timescorerules_repository import TimeScoreRulesRepository
from presenca.controllers.scoreboard_controller import ScoreboardController
from presenca.repositories.checkin_repository import CheckinRepository

CHECKIN_BOARD = "Presença"
SABBATH_CLASS_EVENT = "Escola Sabatina"

lgr = logging.getLogger(__name__)

class CheckinController:
    @classmethod
    def checkin_sabbath(cls, member: Member, checkin_time: datetime) -> float:
        event = EventRepository.get(name=SABBATH_CLASS_EVENT)
        return cls.checkin(member, event, checkin_time)

    @staticmethod
    def get_member_history(member: Member):
        return CheckIn.objects.filter(member=member).order_by("-date").all()

    @staticmethod
    def checkin(member: Member, event: Event, checkin_time: datetime):
        checkin = CheckinRepository.create(member, event, checkin_time)
        WsController.send_member_checkin_for_event(member, event)

        points = TimeScoreRulesRepository.get_points_for_time_in_event(event, checkin_time)
        lgr.info(f"{member.name} ganhou {points}pts para checkin às {checkin_time} no evento {event.name}")
        ScoreboardController.add_points(member=member, board_name=CHECKIN_BOARD, points=points)
        return points