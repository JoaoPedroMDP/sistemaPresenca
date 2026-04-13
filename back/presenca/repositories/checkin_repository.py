from presenca.models import CheckIn, Code, Member


class CheckinRepository:
    
    @staticmethod
    def create(member: Member) -> CheckIn:
        checkin = CheckIn.objects.create(
            member=member
        )

        return checkin