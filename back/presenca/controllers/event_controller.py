from presenca.models import Event, Member

class EventController:
    @staticmethod
    def get_or_create(name: str):
        event: Event = Event.objects.get_or_create(name=name)[0]
        return event

    @staticmethod
    def get_events_member_participated(member: Member):
        return Event.objects.filter(checkin__member=member).distinct()
