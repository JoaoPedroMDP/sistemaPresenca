from ponto.models import Event

class EventRepository:
    @staticmethod
    def get(*args, **kwargs) -> Event:
        return Event.objects.get(*args, **kwargs)
