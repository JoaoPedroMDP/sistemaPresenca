from presenca.models import Event
from presenca.repositories import Repository

class EventRepository(Repository[Event]):
    model = Event
