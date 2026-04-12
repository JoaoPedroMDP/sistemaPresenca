from typing import Optional
from uuid import uuid4

from ponto.models import Code, Event

class CodeRepository:
    @staticmethod
    def create(event: Event):
        new_code = Code.objects.create(code=str(uuid4()), event=event)
        return new_code

    @staticmethod
    def get_unused_code(event: Event) -> Optional[Code]:
        unused = Code.objects.filter(used=False, event=event)

        if len(unused) > 0:
            return unused[0]

        return None

    @staticmethod
    def get_by_code(code_str: str) -> Code:
        return Code.objects.get(code=code_str)

    @staticmethod
    def mark_as_used(code: Code):
        code.used = True
        code.save()

    @staticmethod
    def assign_member(code: Code, member):
        code.used_by = member
        code.save()

