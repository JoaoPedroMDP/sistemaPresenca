from datetime import time
import logging

from django.core.management.base import BaseCommand, CommandParser

from ponto.constants import DAY_END, DAY_START
from ponto.models import Event, Member, Scoreboard, TimeScoreRules


lgr = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Cria Scoreboards iniciais e as regras de pontuação"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            '--test',
            action='store_true',
            help='Indica que o comando está sendo executado em ambiente de teste'
        )
        return super().add_arguments(parser)

    def handle(self, *args, **options):
        Scoreboard.objects.create(name="Escola Sabatina")
        es = Event.objects.create(
            name="Escola Sabatina", 
            description="Todos os sábados, das 9h às 10h."
        )
        if TimeScoreRules.objects.count() == 0:
            lgr.info("Criando regras de pontuação para o evento Escola Sabatina...")
            self._create_timescore_rules(es)
        
        testing = options['test']
        if not testing:
            return

        lgr.info("Criando dados para teste...")
        if Member.objects.count() == 0:
            lgr.info("Criando membros")
            self._create_members()

    def _create_timescore_rules(self, es: Event):
        TimeScoreRules.objects.bulk_create(
            [
                TimeScoreRules(
                    event=es, points=100.0,
                    start_time=DAY_START,
                    end_time=time(9, 0),
                ),
                TimeScoreRules(
                    event=es, points=70.0,
                    start_time=time(9, 0, 1),
                    end_time=time(9, 5),
                ),
                TimeScoreRules(
                    event=es, points=50.0,
                    start_time=time(9, 5, 1),
                    end_time=time(9, 10),
                ),
                TimeScoreRules(
                    event=es, points=00.0,
                    start_time=time(9, 10, 1),
                    end_time=DAY_END,
                ),
            ]
        )

    def _create_members(self):
        Member.objects.bulk_create([
            Member(name="João"),
            Member(name="Juliana"),
            Member(name="Andrezin"),
            Member(name="Wemerson"),
            Member(name="Arthur"),
            Member(name="Gi Damielewski"),
            Member(name="Lucas"),
            Member(name="Erica"),
        ])