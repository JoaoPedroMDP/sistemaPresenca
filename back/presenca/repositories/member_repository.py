from django.contrib.auth.models import User
from django.utils import timezone

from presenca.models import Member
from presenca.repositories import Repository


class MemberRepository(Repository[Member]):
    model = Member

    @staticmethod
    def didnt_checkin_today():
        today_00 = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_midnight = timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)

        return Member.objects.all().exclude(
            checkins__date__range=(today_00, today_midnight)
        )
