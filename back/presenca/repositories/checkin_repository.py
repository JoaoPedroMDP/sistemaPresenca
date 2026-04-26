from datetime import datetime
import logging

from django.db.utils import IntegrityError

from presenca.models import CheckIn, Member, Event
from presenca.repositories import Repository


lgr = logging.getLogger(__name__)


class CheckinRepository(Repository[CheckIn]):
    model = CheckIn

    @staticmethod
    def create(member: Member, event: Event, checkin_time: datetime) -> CheckIn:
        try:
            checkin = CheckIn.objects.create(
                member=member,
                event=event,
                date=checkin_time
            )

            return checkin
        except IntegrityError as e:
            lgr.warning(F"Checkin {event.name} {member.name} {checkin_time} já existia. Não será recriado.")
            return CheckIn.objects.get(member=member, event=event, date=checkin_time)
