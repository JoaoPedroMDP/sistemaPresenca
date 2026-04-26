from datetime import datetime
import csv
import logging

from django.core.management.base import BaseCommand

from presenca.controllers.checkin_controller import CheckinController
from presenca.controllers.event_controller import EventController
from presenca.controllers.member_controller import MemberController
from presenca.models import CheckIn, Event, Member

lgr = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Importa os check-ins a partir de um arquivo CSV"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="Caminho para o arquivo CSV com os check-ins")

    def handle(self, *args, **options):
        csv_file = options["csv_file"]

        with open(csv_file, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                event_name, member_name, date_str = row
                event: Event = EventController.get_or_create(name=event_name)
                member: Member = MemberController.get_or_create(name=member_name)
                date: datetime = datetime.fromisoformat(date_str)
                CheckinController.checkin(member, event, date)
