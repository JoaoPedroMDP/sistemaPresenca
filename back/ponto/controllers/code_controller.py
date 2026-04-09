from ponto.errors import InactiveCodeError
from ponto.controllers.ws_controller import WsController
from ponto.models import Code
from ponto.repositories.code_repository import CodeRepository


class CodeController:
    @staticmethod
    def get_unused_code() -> Code:
        unused = CodeRepository.get_active_code()
        if not unused:
            unused = CodeRepository.create()

        return unused

    @staticmethod
    def use_code(code_str: str) -> None:
        code = CodeRepository.get_by_code(code_str)

        if code.used:
            raise InactiveCodeError("Code already used")

        CodeRepository.mark_as_used(code)

        new_code = CodeController.get_unused_code()
        WsController.sync_emit_new_code(new_code)
