from presenca.errors import ExpiredCodeError
from presenca.models import Code, Event


class CodeController:
    @staticmethod
    def get_current_code(event: Event) -> Code:
        """
            Retorna o código mais recente do evento, criando um novo se o
            último já passou da idade de rotação (evita exibir um QR
            prestes a expirar).
        """
        current = Code.latest_for_event_newer_than(event, Code.rotation_seconds())
        if not current:
            current = Code.create_for_event(event)

        return current

    @staticmethod
    def rotate_code(event: Event) -> Code:
        return Code.create_for_event(event)

    @staticmethod
    def validate_code(code: Code) -> None:
        if not code.is_valid():
            raise ExpiredCodeError("Code expired")
