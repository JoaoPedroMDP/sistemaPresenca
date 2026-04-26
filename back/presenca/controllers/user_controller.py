from django.contrib.auth.models import User

class UserController:
    @staticmethod
    def create_regular_user(name: str, password: str) -> User:
        return User.objects.create_user(username=name, password=password)
