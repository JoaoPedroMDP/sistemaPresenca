import logging

from django.core.handlers.asgi import ASGIRequest
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from ninja import Router, Schema


login_router = Router()
lgr = logging.getLogger(__name__)

class LoginSchema(Schema):
    username: str
    password: str

@login_router.post("/login")
def login(request: ASGIRequest, data: LoginSchema):
    username = data.username
    password = data.password

    if not username or not password:
        return {"error_code": 400, "error": "Username e senha são obrigatórios."}
    
    user = authenticate(request, username=username, password=password)
    if user is not None:
        auth_login(request, user)
        return {"message": "Login bem-sucedido."}
    else:
        return {"error_code": 401, "error": "Credenciais inválidas."}

@login_router.get("/logout")
def logout(request: ASGIRequest):
    if request.user.is_authenticated:
        auth_logout(request)
        return {"message": "Logout bem-sucedido."}
    else:
        return {"error_code": 400, "error": "Nenhum usuário logado."}
