from datetime import datetime, time, timedelta
import uuid

from django.contrib.auth.models import User
from django.db import models
from django.db.utils import IntegrityError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import unidecode


class Base(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Member(Base):
    """
        Representa um membro da comunidade.
    """
    name = models.CharField(max_length=100)
    birthday = models.DateField(blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    photo = models.FileField(upload_to="images/members/", blank=True, null=True)

    class Meta: # type: ignore[misc]
        verbose_name = _("Membro")

    def __str__(self):
        return self.name

    def slug(self):
        return unidecode.unidecode(self.name.split(' ')[0].lower().replace(" ", "_"))

    def to_checkin(self):
        return {
            "name": self.name,
            "photo": self.photo.url if self.photo else None,
            "birthday": self.birthday.isoformat() if self.birthday else None,
        }

    @classmethod
    def didnt_checkin_today(cls, event):
        today = timezone.localtime(timezone.now()).date()
        start = timezone.make_aware(datetime.combine(today, time.min))
        end = timezone.make_aware(datetime.combine(today, time.max))

        return cls.objects.all().exclude(
            checkins__event=event,
            checkins__date__range=(start, end)
        ).order_by("name")


class Event(Base):
    """
        Evento. Por exemplo: Escola Sabatina, Culto Jovem em um dia específico, etc.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    start = models.DateTimeField(default=timezone.now, null=True, blank=True)
    end = models.DateTimeField(default=timezone.now, null=True, blank=True)

    class Meta: # type: ignore[misc]
        verbose_name = _("Evento")

    def __str__(self):
        return self.name

    def as_websocket_group_name(self):
        return self.name.lower().replace(" ", "_")


class Code(Base):
    """
        Código de acesso para check-in em um evento.

        Um código é rotacionado a cada rotation_seconds() (Config
        CODE_ROTATION_SECONDS) e vale por validity_seconds(). Várias
        pessoas podem usar o mesmo código.
    """
    code = models.CharField(max_length=100, unique=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    class Meta: # type: ignore[misc]
        verbose_name = _("Código")

    def __str__(self):
        return self.code

    @classmethod
    def create_for_event(cls, event):
        return cls.objects.create(code=str(uuid.uuid4()), event=event)

    @classmethod
    def latest_for_event_newer_than(cls, event, max_age_seconds: int):
        threshold = timezone.now() - timedelta(seconds=max_age_seconds)
        return cls.objects.filter(
            event=event,
            created_at__gte=threshold
        ).order_by("-created_at").first()

    ROTATION_CONFIG_KEY = "CODE_ROTATION_SECONDS"
    # Folga além da rotação, para quem escaneia perto da troca
    VALIDITY_GRACE_SECONDS = 20

    @classmethod
    def rotation_seconds(cls) -> int:
        # get_or_create: se a linha for apagada no admin, renasce aqui
        config, _ = Config.objects.get_or_create(
            key=cls.ROTATION_CONFIG_KEY,
            defaults={"value": "60", "type": Config.Type.INTEGER},
        )
        return config.coerce()

    @classmethod
    def validity_seconds(cls) -> int:
        return cls.rotation_seconds() + cls.VALIDITY_GRACE_SECONDS

    def is_valid(self) -> bool:
        threshold = timezone.now() - timedelta(seconds=self.validity_seconds())
        return self.created_at >= threshold

    def expires_at(self) -> datetime:
        return self.created_at + timedelta(seconds=self.validity_seconds())

    def rotates_at(self) -> datetime:
        """
            Quando este código sai da tela. É o que o painel exibe como
            "expiração": a folga de validade além da rotação fica invisível.
        """
        return self.created_at + timedelta(seconds=self.rotation_seconds())


class CheckIn(Base):
    """
        Check-in de um membro em uma data e hora específicas.
    """
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="checkins")
    date = models.DateTimeField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    class Meta: # type: ignore[misc]
        verbose_name = _("Check-in")
        unique_together = ("member", "date", "event")

    def __str__(self):
        return f"{self.member.name} - {self.date}"

    @classmethod
    def create_idempotent(cls, member, event, checkin_time: datetime):
        try:
            return cls.objects.create(
                member=member,
                event=event,
                date=checkin_time
            )
        except IntegrityError:
            return cls.objects.get(member=member, event=event, date=checkin_time)


class Scoreboard(Base):
    """
        Define um quadro de pontuações para agrupar pontuações de membros.
    """
    name = models.CharField(max_length=100)

    class Meta: # type: ignore[misc]
        verbose_name = _("Quadro de Pontuação")
        verbose_name_plural = _("Quadros de Pontuação")

    def __str__(self):
        return self.name

    @classmethod
    def get_or_create_by_name(cls, name: str):
        scoreboard, _ = cls.objects.get_or_create(name=name)
        return scoreboard


class Score(Base):
    """
        Pontuação de um membro em um quadro de pontuações.
    """
    board = models.ForeignKey(Scoreboard, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    points = models.FloatField(default=0)

    class Meta: # type: ignore[misc]
        verbose_name = _("Score")
        unique_together = ("board", "member")

    def __str__(self):
        return f"{self.member.name} - {self.points} pontos"

    @classmethod
    def get_or_create_for_board_and_member(cls, scoreboard, member):
        score, _ = cls.objects.get_or_create(board=scoreboard, member=member)
        return score

    def add_points(self, points: float):
        self.points += points
        self.save()


class TimeScoreRules(Base):
    """
        Regras de pontuação baseadas no tempo de checkin de uma pessoa em um evento.

        Por exemplo, na Escola Sabatina:
            Quem chega até as 9h ganha 100 pontos
            Quem chega até as 9h05 ganha 70 pontos
            Quem chega até as 9h10 ganha 50 pontos

        Cada regra dessa acima vira:
            TimeScoreRules(event=escola_sabatina, start_time=00:00, end_time=09:00, points=100)
    """
    event = models.ForeignKey("Event", on_delete=models.CASCADE, related_name="checkin_score_times")
    start_time = models.TimeField()
    end_time = models.TimeField()
    points = models.FloatField(default=1)

    class Meta:  # type: ignore[misc]
        verbose_name = _("Regra de pontuação")
        verbose_name_plural = _("Regras de pontuação")
        unique_together = [
            ("event", "start_time"),
            ("event", "end_time")
        ]

    def __str__(self):
        return f"{self.event.name} {self.start_time} - {self.end_time}: {self.points} pontos."

    @classmethod
    def get_points_for_time_in_event(cls, event, checkin_time: datetime) -> float:
        # Evento sem regras de pontuação (ou checkin fora de todas as faixas)
        # vale 0 pontos: checkin puro, sem placar obrigatório
        tz_converted = checkin_time.astimezone(timezone.get_current_timezone())
        only_time = tz_converted.time()
        timescore = cls.objects.filter(
            event=event,
            start_time__lte=only_time,
            end_time__gte=only_time
        ).first()

        return timescore.points if timescore else 0.0


class Config(Base):
    """
        Variáveis de ambiente configuráveis em tempo de execução pelo admin.

        O valor é armazenado como texto e convertido para o tipo configurado
        na linha via coerce().
    """
    class Type(models.TextChoices):
        STRING = "str", _("Texto")
        INTEGER = "int", _("Inteiro")
        FLOAT = "float", _("Decimal")
        BOOLEAN = "bool", _("Booleano")

    key = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=500)
    type = models.CharField(max_length=10, choices=Type.choices, default=Type.STRING)

    class Meta: # type: ignore[misc]
        verbose_name = _("Configuração")
        verbose_name_plural = _("Configurações")

    def __str__(self):
        return f"{self.key}: {self.value}"

    def coerce(self):
        coercers = {
            self.Type.STRING: str,
            self.Type.INTEGER: int,
            self.Type.FLOAT: float,
            self.Type.BOOLEAN: lambda v: v.strip().lower() in ("true", "1", "sim", "yes"),
        }
        return coercers[self.Type(self.type)](self.value)

    @classmethod
    def get_value(cls, key: str, default=None):
        try:
            return cls.objects.get(key=key).coerce()
        except cls.DoesNotExist:
            return default
