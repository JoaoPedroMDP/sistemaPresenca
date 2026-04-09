from django.db import models

class Base(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Member(Base):
    name = models.CharField(max_length=100)
    birthday = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.name

class Code(Base):
    code = models.CharField(max_length=100, unique=True)
    used = models.BooleanField(default=True)
    used_by = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.code

class CheckIn(Base):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.member.name} - {self.date}"

class Scoreboard(Base):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Score(Base):
    board = models.ForeignKey(Scoreboard, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    points = models.FloatField(default=0)

    def __str__(self):
        return f"{self.member.name} - {self.points} pontos"

class TimeScoreRules(Base):
    """
        Define a pontuação ganha por um check-in em diferentes horários do dia.
    """
    event = models.ForeignKey("Event", on_delete=models.CASCADE, related_name="checkin_score_times")
    start_time = models.TimeField()
    end_time = models.TimeField()
    points = models.FloatField(default=1)

    class Meta:  # type: ignore[misc]
        unique_together = [
            ("event", "start_time"),
            ("event", "end_time")
        ]

    def __str__(self):
        return f"{self.event.name} {self.start_time} - {self.end_time}: {self.points} pontos."

class Event(Base):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
