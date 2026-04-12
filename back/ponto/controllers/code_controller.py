from ponto.errors import UsedCodeError
from ponto.models import Code, Event
from ponto.repositories.code_repository import CodeRepository
from ponto.repositories.event_repository import EventRepository


class CodeController:
    @staticmethod
    def get_unused_code(event: Event) -> Code:
        unused = CodeRepository.get_unused_code(event)
        if not unused:
            unused = CodeRepository.create(event)

        return unused

    @classmethod
    def get_unused_code_event_name(cls, event_name: str) -> Code:
        event: Event = EventRepository.get(name=event_name)
        return cls.get_unused_code(event)

    @staticmethod
    def use_code(code: Code) -> None:
        if code.used:
            raise UsedCodeError("Code already used")

        CodeRepository.mark_as_used(code)
