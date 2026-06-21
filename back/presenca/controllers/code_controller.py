from presenca.errors import UsedCodeError
from presenca.models import Code, Event


class CodeController:
    @staticmethod
    def get_unused_code(event: Event) -> Code:
        unused = Code.get_unused_for_event(event)
        if not unused:
            unused = Code.create_for_event(event)

        return unused

    @classmethod
    def get_unused_code_event_name(cls, event_name: str) -> Code:
        event: Event = Event.objects.get(name=event_name)
        return cls.get_unused_code(event)

    @staticmethod
    def use_code(code: Code) -> None:
        if code.used:
            raise UsedCodeError("Code already used")

        code.mark_as_used()
