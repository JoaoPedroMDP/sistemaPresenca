import os
import shutil
import sys


def detect_engine() -> str:
    """Retorna o engine de containers disponível: docker ou podman."""
    for engine in ("docker", "podman"):
        if shutil.which(engine):
            return engine
    print("Nenhum engine de containers encontrado (docker ou podman).")
    sys.exit(1)


def main(back: bool, front: bool):
    engine = detect_engine()
    print(f"Usando engine: {engine}")

    # executa compose build
    if back:
        os.system(f"{engine} compose -f docker-compose-dev.yml build --no-cache back")
        os.system(f"{engine} save sistemapresenca-back:latest -o back.tar.gz")
        os.system("scp back.tar.gz root@presenca:/images/back.tar.gz")

    if front:
        os.system(f"{engine} compose -f docker-compose-dev.yml build --no-cache front")
        os.system(f"{engine} save sistemapresenca-front:latest -o front.tar.gz")
        os.system("scp front.tar.gz root@presenca:/images/front.tar.gz")

if __name__ == "__main__":
    back = False
    front = False
    # Instruções de uso

    # Verifica os argumentos
    if len(sys.argv) < 2:
        print("Uso: python sendimage.py [back] [front]")
        print("Exemplo: python sendimage.py back front")
        sys.exit(1)
    
    for arg in sys.argv[1:]:
        if arg == "back":
            back = True
        elif arg == "front":
            front = True
        else:
            print(f"Argumento desconhecido: {arg}")
            print("Uso: python sendimage.py [back] [front]")
            sys.exit(1)


    main(back, front)