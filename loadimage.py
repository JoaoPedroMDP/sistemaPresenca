import os
import sys


def main(back: bool, front: bool):
    # executa docker compose build
    if back:
        os.system("docker load < /images/back.tar.gz")
        os.system("docker compose down back")
        os.system("docker compose up -d back")

    if front:
        os.system("docker load < /images/front.tar.gz")
        os.system("docker compose down front")
        os.system("docker compose up -d front")

if __name__ == "__main__":
    back = False
    front = False
    # Instruções de uso

    # Verifica os argumentos
    if len(sys.argv) < 2:
        print("Uso: python loadimage.py [back] [front]")
        print("Exemplo: python loadimage.py back front")
        print("Erro: É necessário especificar pelo menos um dos argumentos 'back' ou 'front'.")
        sys.exit(1)
    
    for arg in sys.argv[1:]:
        if arg == "back":
            back = True
        elif arg == "front":
            front = True
        else:
            print(f"Argumento desconhecido: {arg}")
            print("Uso: python loadimage.py [back] [front]")
            sys.exit(1)


    main(back, front)