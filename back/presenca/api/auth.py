import logging

from django.core.handlers.asgi import ASGIRequest
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.http import JsonResponse
from ninja import Router, Schema
from ninja.security import SessionAuth


login_router = Router()
lgr = logging.getLogger(__name__)

class LoginSchema(Schema):
    username: str
    password: str

@login_router.post("/login")
def login(request: ASGIRequest, data: LoginSchema):
    lgr.debug(f"/auth/login - INICIO")
    username = data.username.lower()
    password = data.password

    if not username or not password:
        return JsonResponse({"error_code": 400, "error": "Username e senha são obrigatórios."}, status=400)

    user = authenticate(request, username=username, password=password)
    if user is None:
        lgr.info(f"Falha de login para usuário '{username}'. Credenciais inválidas.")
        return JsonResponse({"error_code": 401, "error": "Credenciais inválidas."}, status=401)

    auth_login(request, user)
    lgr.info(f"Usuário '{username}' logado com sucesso.")
    lgr.debug(f"/auth/login - FIM")
    return {"message": "Login bem-sucedido."}

@login_router.get("/logout", auth=SessionAuth())
def logout(request: ASGIRequest):
    lgr.debug(f"/auth/logout - INICIO")
    lgr.info(f"Usuário '{request.user.username}' solicitou logout.")

    auth_logout(request)

    lgr.info(f"Usuário '{request.user.username}' deslogado com sucesso.")
    lgr.debug(f"/auth/logout - FIM")

    return {"message": "Logout bem-sucedido."}

@login_router.get("/logged", auth=SessionAuth())
def logged(request: ASGIRequest):
    lgr.debug(f"/auth/logged - INICIO")
    lgr.info(f"Verificando status de login do usuário '{request.user.username}'.")
    lgr.debug(f"/auth/logged - FIM")
    return 200, {"logged": True, "username": request.user.username}
