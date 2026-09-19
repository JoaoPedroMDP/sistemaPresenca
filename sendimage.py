import json
import os
import shutil
import subprocess
import sys

REMOTE = "root@presenca"
REMOTE_DIR = "/images"
SERVICES = ("back", "front")


def detect_engine() -> str:
    """Retorna o engine de containers disponível: docker ou podman."""
    for engine in ("docker", "podman"):
        if shutil.which(engine):
            return engine
    print("Nenhum engine de containers encontrado (docker ou podman).")
    sys.exit(1)


def read_version() -> str:
    """Lê a versão do cz.json, a mesma que o commitizen usa na tag."""
    with open("cz.json") as f:
        return json.load(f)["commitizen"]["version"]


def remote_exists(path: str) -> bool:
    return subprocess.run(["ssh", REMOTE, "test", "-e", path]).returncode == 0


def run(cmd: str):
    print(f"$ {cmd}")
    code = os.system(cmd)
    if code != 0:
        print(f"Comando falhou (exit {code >> 8}).")
        sys.exit(1)


def build_cmd(engine: str, service: str, tag: str) -> str:
    # Constrói direto com o engine em vez de `compose build`: o podman delega
    # o compose ao docker-compose, que sem BuildKit não suporta o
    # additional_contexts (repo-root) que o front precisa. Os parâmetros
    # espelham a seção build de cada serviço em docker-compose-dev.yml.
    # O prefixo docker.io/library evita que o podman marque como localhost/,
    # nome que o compose de produção não reconheceria após o load.
    extra = "--build-context repo-root=. " if service == "front" else ""
    return (
        f"{engine} build --no-cache --platform linux/amd64 "
        f"-f docker/Dockerfile.{service} {extra}"
        f"-t docker.io/library/{tag} ./{service}"
    )


def main(services: list[str]):
    engine = detect_engine()
    version = read_version()
    print(f"Usando engine: {engine}, versão: {version}")

    # Uma imagem por versão e nunca sobrescrita no servidor: as versões
    # anteriores continuam em /images para rollback via loadimage.py.
    # A checagem vem antes de qualquer build para falhar rápido.
    for service in services:
        remote_path = f"{REMOTE_DIR}/{service}-{version}.tar.gz"
        if remote_exists(remote_path):
            print(f"{remote_path} já existe no servidor.")
            print("Faça o bump da versão (cz bump) antes de enviar uma nova imagem.")
            sys.exit(1)

    for service in services:
        tag = f"sistemapresenca-{service}:{version}"
        archive = f"{service}-{version}.tar.gz"
        run(build_cmd(engine, service, tag))
        run(f"{engine} save {tag} -o {archive}")
        run(f"scp {archive} {REMOTE}:{REMOTE_DIR}/{archive}")


if __name__ == "__main__":
    usage = "Uso: python sendimage.py [back] [front]"
    if len(sys.argv) < 2:
        print(usage)
        print("Exemplo: python sendimage.py back front")
        sys.exit(1)

    services = []
    for arg in sys.argv[1:]:
        if arg in SERVICES:
            services.append(arg)
        else:
            print(f"Argumento desconhecido: {arg}")
            print(usage)
            sys.exit(1)

    main(services)
