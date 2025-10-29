import socket

HOST = "172.31.69.179"
PORT = 5001

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    print("Conectado ao servidor!")

    while True:
        data = client.recv(1024).decode()
        if not data:
            break

        print(data, end="")

        if "Digite sua jogada" in data:
            jogada = input("> ")
            client.sendall(jogada.encode())

    client.close()
    print("Conexão encerrada")

if __name__ == "__main__":
    main()