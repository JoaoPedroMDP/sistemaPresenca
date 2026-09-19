import json
import os
import sys

IMAGES_DIR = "/images"
SERVICES = ("back", "front")

# Sempre o compose de produção: sem -f o docker procura um compose.yml
# solto no servidor, que pode estar defasado em relação ao repositório
COMPOSE = "docker compose -f docker-compose-prod.yml"


def read_version() -> str:
    """Versão do cz.json do repositório no servidor (a última enviada)."""
    with open("cz.json") as f:
        return json.load(f)["commitizen"]["version"]


def run(cmd: str):
    print(f"$ {cmd}")
    code = os.system(cmd)
    if code != 0:
        print(f"Comando falhou (exit {code >> 8}).")
        sys.exit(1)


def main(services: list[str], version: str):
    # Só carrega imagens e recria containers; o servidor não constrói nada.
    # A imagem carregada fica como sistemapresenca-X:<versão> e a tag latest,
    # que o docker-compose-prod.yml usa, é movida para ela. Rollback é rodar
    # com --version apontando para uma imagem anterior ainda em /images.
    for service in services:
        archive = f"{IMAGES_DIR}/{service}-{version}.tar.gz"
        if not os.path.exists(archive):
            print(f"Imagem não encontrada: {archive}")
            print("Versões disponíveis:")
            os.system(f"ls {IMAGES_DIR}")
            sys.exit(1)

    for service in services:
        image = f"sistemapresenca-{service}"
        run(f"docker load < {IMAGES_DIR}/{service}-{version}.tar.gz")
        run(f"docker tag {image}:{version} {image}:latest")
        # APP_VERSION acompanha a imagem carregada, não o .env do servidor
        run(f"APP_VERSION={version} {COMPOSE} up -d --no-deps --force-recreate {service}")


if __name__ == "__main__":
    usage = "Uso: python loadimage.py [back] [front] [--version X.Y.Z]"
    if len(sys.argv) < 2:
        print(usage)
        print("Exemplo: python loadimage.py back front")
        print("Rollback: python loadimage.py back --version 1.1.1")
        print("Erro: É necessário especificar pelo menos um dos argumentos 'back' ou 'front'.")
        sys.exit(1)

    services = []
    version = None
    args = sys.argv[1:]
    while args:
        arg = args.pop(0)
        if arg in SERVICES:
            services.append(arg)
        elif arg == "--version":
            if not args:
                print("--version exige um valor.")
                sys.exit(1)
            version = args.pop(0)
        else:
            print(f"Argumento desconhecido: {arg}")
            print(usage)
            sys.exit(1)

    if not services:
        print("Erro: É necessário especificar pelo menos um dos argumentos 'back' ou 'front'.")
        sys.exit(1)

    main(services, version or read_version())
