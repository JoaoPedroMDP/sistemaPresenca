from datetime import datetime
import logging
from typing import Dict, List

from django.utils import timezone
from django.db.models import QuerySet

from presenca.controllers.event_controller import EventController
from presenca.controllers.ws_controller import WsController
from presenca.repositories.event_repository import EventRepository
from presenca.models import CheckIn, Event, Member
from presenca.repositories.timescorerules_repository import TimeScoreRulesRepository
from presenca.repositories.checkin_repository import CheckinRepository

CHECKIN_BOARD = "Presença"
SABBATH_CLASS_EVENT = "Escola Sabatina"

lgr = logging.getLogger(__name__)

class CheckinController:
    @classmethod
    def checkin_sabbath(cls, member: Member, checkin_time: datetime) -> float:
        event = EventRepository.get(name=SABBATH_CLASS_EVENT)
        return cls.checkin(member, event, checkin_time)

    @classmethod
    def get_member_history(cls, member: Member) -> Dict[str, List[CheckIn]]:
        events_member_participated = EventController.get_events_member_participated(member)
        by_event = {}
        for e in events_member_participated:
            if e.name not in by_event:
                by_event[e.name] = []

            by_event[e.name] = cls.get_checkins_for_event_member(e, member, limit=6)

        return by_event

    @staticmethod
    def checkin(member: Member, event: Event, checkin_time: datetime):
        checkin = CheckinRepository.create(member, event, checkin_time)
        WsController.send_member_checkin_for_event(member, event)

        points = TimeScoreRulesRepository.get_points_for_time_in_event(event, checkin_time)
        lgr.info(f"{member.name} ganhou {points}pts para checkin às {checkin_time} no evento {event.name}")
        return points

    @staticmethod
    def get_checkins_for_event_member(event: Event, member: Member, limit=None):
        checkins = CheckIn.objects.filter(
            event=event, member=member,
            date__range=(event.start, event.end)
        ).order_by("-date")

        if limit is not None:
            checkins = checkins[:limit].all()

        return checkins

    @staticmethod
    def get_checkins_today_for_event(event: Event) -> QuerySet[CheckIn]:
        checkins = CheckIn.objects.filter(
            event=event,
            datetime__date=timezone.now().date(),
        )

        return checkins
