from django.contrib.auth.models import User
from django.db import models
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


class Event(Base):
    """
        Evento. Por exemplo: Escola Sabatina, Culto Jovem em um dia específico, etc.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    class Meta: # type: ignore[misc]
        verbose_name = _("Evento")
    
    def __str__(self):
        return self.name
    
    def as_websocket_group_name(self):
        return self.name.lower().replace(" ", "_")


class Code(Base):
    """
        Código de acesso para check-in em um evento.
    """
    code = models.CharField(max_length=100, unique=True)
    used = models.BooleanField(default=False)
    used_by = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    
    class Meta: # type: ignore[misc]
        verbose_name = _("Código")
    
    def __str__(self):
        return self.code


class CheckIn(Base):
    """
        Check-in de um membro em uma data e hora específicas.
    """
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="checkins")
    date = models.DateTimeField(default=timezone.now)
    
    class Meta: # type: ignore[misc]
        verbose_name = _("Check-in")
    
    def __str__(self):
        return f"{self.member.name} - {self.date}"


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
