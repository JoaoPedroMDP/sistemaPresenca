from presenca.models import CheckIn, Member
from presenca.repositories import Repository


class CheckinRepository(Repository[CheckIn]):
    model = CheckIn

    @staticmethod
    def create(member: Member) -> CheckIn:
        checkin = CheckIn.objects.create(
            member=member
        )

        return checkin
