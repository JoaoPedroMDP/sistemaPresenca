import logging

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from unidecode import unidecode

from presenca.models import Member


lgr = logging.getLogger(__name__)

def get_slug(name: str) -> str:
    return unidecode(name.split(' ')[0].lower().replace(" ", "_"))
    
def fix_passwords(UserModel):
    users_without_password = UserModel.objects.filter(password='')

    lgr.info(f"Encontrados {users_without_password.count()} usuários sem senha definida. Criando senhas padrão...")
    for user in users_without_password:
        if user.member is None:
            continue
        lgr.info(f"Criando senha para usuário: {user.username}")

        m: Member = user.member
        suffix = m.name.split()[-1].lower()
        if m.birthday:
            suffix = m.birthday.strftime("%d%m%Y")
        
        passw = get_slug(m.name) + suffix
        user.password = make_password(passw)
        user.save()

class Command(BaseCommand):
    help = "Cria senhas padrão para os usuários que não possuem senha definida"

    def handle(self, *args, **options):
        fix_passwords(User)