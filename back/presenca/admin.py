from typing import Any
import uuid

import qrcode
import qrcode.image.svg
from django.contrib import admin
from django.db.models.fields.related import ForeignKey
from django.forms.models import ModelChoiceField
from django.http import HttpRequest
from django.utils.formats import date_format
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from presenca.models import CheckIn, Code, Config, Device, Event, TimeScoreRules, Member, Score, Scoreboard


class HasMemberList(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field: ForeignKey[Any], request: HttpRequest | None, **kwargs: Any) -> ModelChoiceField | None:
        if db_field.name == "member":
            kwargs['queryset'] = Member.objects.all().order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class CheckInAdmin(HasMemberList):
    list_display = ("name", "checkindate", "event")
    list_filter = ("date", "event")
    search_fields = ("member__name", "date", "event__name")
    ordering = ("-date",)

    @admin.display(description="Data")
    def checkindate(self, obj):
        if not obj.date:
            return ""

        dt_local = timezone.localtime(obj.date)
        return date_format(dt_local, format="d/m/Y H:i:s")

    @admin.display(description="Nome")
    def name(self, obj):
        return obj.member.name


class TimeScoreRulesAdmin(admin.ModelAdmin):
    list_display = ('event', 'start_time_s', 'end_time_s', 'points')
    list_filter = ('event',)
    search_fields = ('event__name',)

    @admin.display(description="Inicio")
    def start_time_s(self, obj):
        return obj.start_time.strftime("%H:%M:%S")

    @admin.display(description="Fim")
    def end_time_s(self, obj):
        return obj.end_time.strftime("%H:%M:%S")


class CodeAdmin(admin.ModelAdmin):
    list_display = ("code", "event", "created_at")
    list_filter = ("event",)
    date_hierarchy = "created_at"
    search_fields = ("code",)
    ordering = ("-created_at",)


class DeviceAdmin(admin.ModelAdmin):
    """
        Aparelhos liberados para marcar presença sem QR rotativo. Para liberar
        um tablet: adicione um dispositivo, salve e leia nele o QR que aparece
        na tela de edição.
    """
    list_display = ("__str__", "event", "code", "created_at", "status")
    list_filter = ("event",)
    search_fields = ("code", "label")
    readonly_fields = ("code", "activated_at", "qr_code")
    actions = ("revoke",)

    # A URL que o QR aponta. Fica na Config para poder mudar sem deploy
    # (dev, rede local, produção).
    SITE_URL_CONFIG_KEY = "SITE_URL"
    SITE_URL_DEFAULT = "http://localhost:5173"

    def get_fields(self, request, obj=None):
        if obj is None:
            # Na criação o código ainda não existe e não há QR para mostrar
            return ("event", "label")

        return ("code", "event", "label", "activated_at", "revoked_at", "qr_code")

    def save_model(self, request, obj, form, change):
        if not obj.code:
            obj.code = str(uuid.uuid4())
        super().save_model(request, obj, form, change)

    @admin.display(description="Situação")
    def status(self, obj):
        if obj.revoked_at:
            return "revogado"
        if not obj.is_valid():
            return "expirado"
        if obj.activated_at:
            return "em uso"

        return "aguardando leitura do QR"

    @admin.display(description="QR Code de ativação")
    def qr_code(self, obj):
        if obj.activated_at:
            return "Código já resgatado por um aparelho. Para liberar outro, crie um novo dispositivo."

        if obj.revoked_at or not obj.is_valid():
            return "Dispositivo revogado ou expirado. Crie um novo."

        site_url = Config.get_value(self.SITE_URL_CONFIG_KEY, self.SITE_URL_DEFAULT)
        url = f"{str(site_url).rstrip('/')}/checkin/device/{obj.code}"
        img = qrcode.make(url, image_factory=qrcode.image.svg.SvgPathImage, box_size=12)
        svg = img.to_string(encoding="unicode")

        return format_html(
            '<div style="max-width:320px">{}</div>'
            '<p style="margin-top:.5rem">Leia no aparelho. Uso único.<br>'
            '<code>{}</code></p>',
            mark_safe(svg), url
        )

    @admin.action(description="Revogar acesso dos dispositivos selecionados")
    def revoke(self, request, queryset):
        revoked = queryset.filter(revoked_at__isnull=True).update(revoked_at=timezone.now())
        self.message_user(request, f"{revoked} dispositivo(s) revogado(s).")


class ScoreAdmin(HasMemberList):
    list_display = ("member", "points")
    list_filter = ("board",)
    search_fields = ("member__name", "board__name", "points")
    ordering = ("-points",)


class MemberAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "birthday", "has_photo")
    search_fields = ("name", "user__username")
    ordering = ("name","birthday")

    @admin.display(description="Foto", boolean=True)
    def has_photo(self, obj):
        return bool(obj.photo)


class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "start", "end")
    search_fields = ("name",)
    ordering = ("name",)


class ScoreboardAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)


class ConfigAdmin(admin.ModelAdmin):
    list_display = ("key", "value", "type")
    search_fields = ("key", "value")


admin.site.site_title = "Painel - Presença Jovens"
admin.site.register(Code, CodeAdmin)
admin.site.register(Device, DeviceAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(CheckIn, CheckInAdmin)
admin.site.register(Scoreboard, ScoreboardAdmin)
admin.site.register(Score, ScoreAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(TimeScoreRules, TimeScoreRulesAdmin)
admin.site.register(Config, ConfigAdmin)
