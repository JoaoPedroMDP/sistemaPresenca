from datetime import time

from django.core.management.base import BaseCommand

from ponto.constants import DAY_END, DAY_START
from ponto.models import Event, Scoreboard, TimeScoreRules



class Command(BaseCommand):
    help = "Cria Scoreboards iniciais e as regras de pontuação"

    def handle(self, *args, **options):
        Scoreboard.objects.create(name="Escola Sabatina")
        es = Event.objects.create(
            name="Escola Sabatina", 
            description="Todos os sábados, das 9h às 10h."
        )

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