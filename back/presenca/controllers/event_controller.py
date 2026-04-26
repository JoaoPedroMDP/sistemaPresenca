from presenca.models import Event

class EventController:
    @staticmethod
    def get_or_create(name: str):
        event: Event = Event.objects.get_or_create(name=name)[0]
        return event
