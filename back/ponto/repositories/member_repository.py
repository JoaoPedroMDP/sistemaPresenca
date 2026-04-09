from django.utils import timezone

from ponto.models import Member


class MemberRepository:
    @staticmethod
    def get_all():
        return Member.objects.all()

    @staticmethod
    def get_by_id(m_id: int):
        return Member.objects.get(id=m_id)

    @staticmethod
    def didnt_checkin_today():
        today_00 = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_midnight = timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)

        return Member.objects.all().exclude(
            checkin__date__range=(today_00, today_midnight)
        )