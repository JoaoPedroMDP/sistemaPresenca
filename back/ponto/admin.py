from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ponto.utils import is_today
from ponto.models import CheckIn, Code, Event, TimeScoreRules, Member, Score, Scoreboard


class CheckInAdmin(admin.ModelAdmin):
    list_display = ("Nome", "Data", "Horário")
    list_filter = ("date",)
    search_fields = ("member__name", "date")

    @admin.display(description="Data")
    def Data(self, obj):
        if is_today(obj.date):
            return "Hoje"

        return obj.date.strftime("%d/%m/%Y")

    @admin.display(description="Horário")
    def Horário(self, obj):
        return obj.date.strftime("%H:%M:%S")

    @admin.display(description="Nome")
    def Nome(self, obj):
        return obj.member.name


class TimeScoreRulesAdmin(admin.ModelAdmin):
    list_display = ('event', 'Inicio', 'Fim', 'points')
    list_filter = ('event',)
    search_fields = ('event__name',)

    @admin.display(description="Inicio")
    def Inicio(self, obj):
        return obj.start_time.strftime("%H:%M:%S")

    @admin.display(description="Fim")
    def Fim(self, obj):
        return obj.end_time.strftime("%H:%M:%S")


class CodeAdmin(admin.ModelAdmin):
    list_display = ("code", "used", "created_at")
    search_fields = ("code",)


class ScoreAdmin(admin.ModelAdmin):
    list_display = ("member", "points")
    list_filter = ("board",)
    search_fields = ("member__name", "board__name", "points")

admin.site.site_title = _("Painel - Presença Jovens")
admin.site.register(Code, CodeAdmin)
admin.site.register(Member)
admin.site.register(CheckIn, CheckInAdmin)
admin.site.register(Scoreboard)
admin.site.register(Score, ScoreAdmin)
admin.site.register(Event)
admin.site.register(TimeScoreRules, TimeScoreRulesAdmin)
