import logging
from csv import writer

from django.core.management.base import BaseCommand
from django.db.models import QuerySet

from presenca.models import Event, Member, CheckIn

lgr = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Exporta os check-ins para que possam ser inseridos posteriormente"

    def handle(self, *args, **options):
        events: QuerySet[Event] = Event.objects.all()
        checkins = []

        for e in events:
            checkins.extend(self.handle_event(e))

        with open("checkins.csv", "w", newline="") as f:
            csv_writer = writer(f)
            csv_writer.writerows(checkins)

    def handle_event(self, event: Event):
        checkins: QuerySet[CheckIn] = CheckIn.objects.filter(event=event).order_by("member__name", "date").all()
        data = []
        for ci in checkins:
            data.append(
                [ci.event.name, ci.member.name, ci.date.isoformat()]
            )

        return data