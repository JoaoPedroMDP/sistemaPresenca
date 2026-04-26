from typing import Any

from django.contrib import admin
from django.db.models.fields.related import ForeignKey
from django.forms.models import ModelChoiceField
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from django.utils.formats import localize
from django.utils import timezone

from presenca.utils import is_today
from presenca.models import CheckIn, Code, Event, TimeScoreRules, Member, Score, Scoreboard


class HasMemberList(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field: ForeignKey[Any], request: HttpRequest | None, **kwargs: Any) -> ModelChoiceField | None:
        if db_field.name == "member":
            kwargs['queryset'] = Member.objects.all().order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class CheckInAdmin(HasMemberList):
    list_display = ("name", "date", "event")
    list_filter = ("date", "event")
    search_fields = ("member__name", "date", "event__name")
    ordering = ("-date",)

    @admin.display(description="Data")
    def date(self, obj):
        if not obj.date:
            return ""
        
        dt_local = timezone.localtime(obj.date)
        return localize(dt_local, use_l10n=True)

    @admin.display(description="Nome")
    def name(self, obj):
        return obj.member.name


class TimeScoreRulesAdmin(admin.ModelAdmin):
    list_display = ('event', 'start_time', 'end_time', 'points')
    list_filter = ('event',)
    search_fields = ('event__name',)

    @admin.display(description="Inicio")
    def start_time(self, obj):
        return obj.start_time.strftime("%H:%M:%S")

    @admin.display(description="Fim")
    def end_time(self, obj):
        return obj.end_time.strftime("%H:%M:%S")


class CodeAdmin(admin.ModelAdmin):
    list_display = ("code", "used", "created_at")
    search_fields = ("code",)


class ScoreAdmin(HasMemberList):
    list_display = ("member", "points")
    list_filter = ("board",)
    search_fields = ("member__name", "board__name", "points")
    ordering = ("-points",)


class MemberAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "created_at")
    search_fields = ("name", "user__username")
    ordering = ("name",)

admin.site.site_title = _("Painel - Presença Jovens")
admin.site.register(Code, CodeAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(CheckIn, CheckInAdmin)
admin.site.register(Scoreboard)
admin.site.register(Score, ScoreAdmin)
admin.site.register(Event)
admin.site.register(TimeScoreRules, TimeScoreRulesAdmin)
