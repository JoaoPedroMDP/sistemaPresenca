import os
import sys


def main(back: bool, front: bool):
    # executa docker compose build
    if back:
        os.system("docker compose -f docker-compose-dev.yml build --no-cache back")
        os.system("docker save sistemapresenca-back:latest -o back.tar.gz")
        os.system("scp back.tar.gz root@checkin:/images/back.tar.gz")

    if front:
        os.system("docker compose -f docker-compose-dev.yml build --no-cache front")
        os.system("docker save sistemapresenca-front:latest -o front.tar.gz")
        os.system("scp front.tar.gz root@checkin:/images/front.tar.gz")

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