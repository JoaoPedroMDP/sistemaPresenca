import logging
import random
from datetime import date, time, timedelta

from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.utils import timezone

from presenca.constants import DAY_END, DAY_START
from presenca.models import Event, Member, Scoreboard, TimeScoreRules


lgr = logging.getLogger(__name__)

DEFAULT_MEMBERS_COUNT = 50

# Metade dos membros criados aniversaria dentro dessa janela em torno de hoje,
# para que as telas de aniversariantes tenham dados em desenvolvimento.
BIRTHDAY_WINDOW_IN_DAYS = 5
UPCOMING_BIRTHDAY_RATIO = 0.5

FIRST_NAMES = [
    "João", "André", "Arthur", "Giovana", "Lucas",
    "Erica", "Mateus", "Beatriz", "Rafael", "Camila", "Pedro", "Larissa",
    "Gabriel", "Fernanda", "Thiago", "Amanda", "Vinícius", "Letícia",
    "Daniel", "Priscila", "Bruno", "Nathália", "Felipe", "Carolina",
    "Rodrigo", "Isabela", "Marcelo", "Renata",
]

LAST_NAMES = [
    "Silva", "Santos", "Oliveira", "Souza", "Lima", "Pereira", "Costa",
    "Ferreira", "Almeida", "Rodrigues", "Nascimento",
    "Carvalho", "Gomes", "Martins", "Araújo", "Ribeiro", "Barbosa",
    "Cardoso", "Teixeira",
]


class Command(BaseCommand):
    help = "Cria Scoreboards iniciais e as regras de pontuação"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            '--test',
            action='store_true',
            help='Indica que o comando está sendo executado em ambiente de teste'
        )
        parser.add_argument(
            '--members',
            type=int,
            default=DEFAULT_MEMBERS_COUNT,
            help=(
                'Quantidade de membros a serem criados no modo de teste. '
                f'Padrão: {DEFAULT_MEMBERS_COUNT}'
            )
        )
        return super().add_arguments(parser)

    def handle(self, *args, **options):
        if Scoreboard.objects.count() == 0:
            Scoreboard.objects.create(name="Escola Sabatina")
        
        es = Event.objects.filter(name="Escola Sabatina").first()
        if not es:
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

        quantity = options['members']
        if quantity < 0:
            raise CommandError("--members deve ser maior ou igual a zero")

        lgr.info("Criando dados para teste...")
        if Member.objects.count() == 0:
            lgr.info("Criando %s membros", quantity)
            self._create_members(quantity)

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

    def _create_members(self, quantity: int):
        names = self._generate_names(quantity)
        upcoming = round(quantity * UPCOMING_BIRTHDAY_RATIO)
        Member.objects.bulk_create([
            Member(name=name, birthday=self._random_birthday(near=index < upcoming))
            for index, name in enumerate(names)
        ])

    def _generate_names(self, quantity: int) -> list[str]:
        """
        Gera nomes distintos combinando FIRST_NAMES e LAST_NAMES. Quando a
        quantidade pedida excede as combinações possíveis, os excedentes
        recebem um sufixo numérico para continuarem distintos.
        """
        combinations = [
            f"{first} {last}"
            for first in FIRST_NAMES
            for last in LAST_NAMES
        ]
        random.shuffle(combinations)

        names = combinations[:quantity]
        for index in range(len(combinations), quantity):
            names.append(f"{random.choice(combinations)} {index + 1}")

        return names

    def _random_birthday(self, near: bool = False) -> date:
        """
        Sorteia uma data de nascimento com idade entre 10 e 70 anos. Com
        `near`, o dia e o mês caem dentro de BIRTHDAY_WINDOW_IN_DAYS em torno
        de hoje; caso contrário, a data é totalmente aleatória.
        """
        today = timezone.localdate()
        age = random.randint(10, 70)

        if not near:
            return today - timedelta(days=age * 365 + random.randint(0, 364))

        offset = random.randint(-BIRTHDAY_WINDOW_IN_DAYS, BIRTHDAY_WINDOW_IN_DAYS)
        anniversary = today + timedelta(days=offset)
        try:
            return anniversary.replace(year=anniversary.year - age)
        except ValueError:  # 29 de fevereiro em ano de nascimento não bissexto
            return anniversary.replace(year=anniversary.year - age, day=28)
