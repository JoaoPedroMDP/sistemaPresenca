import logging

from django.contrib.auth.models import User

from presenca.controllers.user_controller import UserController
from presenca.models import Member


lgr = logging.getLogger(__name__)


class MemberController:
    @staticmethod
    def get_or_create(name: str):
        try:
            member: Member = Member.objects.get(name=name)
        except Member.DoesNotExist:
            lgr.info(f"Membro não encontrado: {name}. Criando...")
            user: User = UserController.create_regular_user(name, password="default_password")
            member: Member = Member.objects.get_or_create(name=name, user=user)[0]

        return member