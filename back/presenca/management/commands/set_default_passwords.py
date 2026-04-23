import logging

from django.core.management.base import BaseCommand, CommandParser
from django.contrib.auth.models import User

from presenca.models import Member


lgr = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Cria senhas padrão para os usuários que não possuem senha definida"

    def handle(self, *args, **options):
        users_without_password = User.objects.filter(password='')

        lgr.info(f"Encontrados {users_without_password.count()} usuários sem senha definida. Criando senhas padrão...")
        for user in users_without_password:
            if user.member is None:
                continue

            m: Member = user.member
            suffix = m.name.split()[-1].lower()
            if m.birthday:
                suffix = m.birthday.strftime("%d%m%Y")
            
            passw = m.slug() + suffix
            print(f"Definindo senha para usuário {user.username} (senha: {passw})")
            user.set_password(passw)
            user.save()
