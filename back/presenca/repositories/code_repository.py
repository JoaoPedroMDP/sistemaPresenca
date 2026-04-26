from typing import Optional
from uuid import uuid4

from django.utils import timezone

from presenca.models import Code, Event
from presenca.repositories import Repository

class CodeRepository(Repository[Code]):
    model = Code

    @staticmethod
    def create(event: Event):
        new_code = Code.objects.create(code=str(uuid4()), event=event)
        return new_code

    @staticmethod
    def get_unused_code(event: Event) -> Optional[Code]:
        unused = Code.objects.filter(used__isnull=True, event=event)

        if len(unused) > 0:
            return unused[0]

        return None

    @staticmethod
    def mark_as_used(code: Code):
        code.used = timezone.now()
        code.save()

    @staticmethod
    def assign_member(code: Code, member):
        code.used_by = member
        code.save()

