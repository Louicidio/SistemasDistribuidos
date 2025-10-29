import socket
import threading

HOST = "0.0.0.0"
PORT = 5001

clientes = {}  # chave de clientes

def broadcast(mensagem, conn):
    nickname = clientes[conn]
    mensagem_formatada = f"{nickname}: {mensagem.decode('utf-8')}"
    for cliente in list(clientes.keys()):
        try:
            cliente.send(mensagem_formatada.encode("utf-8"))
        except:
            cliente.close()
            del clientes[cliente]

def handle_client(conn, addr):
    try:
        nickname = conn.recv(1024).decode("utf-8")
        clientes[conn] = nickname

        print(f"[NOVA CONEXÃO] {addr} como {nickname}")
        conn.send(f"Bem-vindo ao chat, {nickname}! Digite /sair para sair.\n".encode("utf-8"))
        broadcast(f"entrou no chat.".encode("utf-8"), conn)

        while True:
            msg = conn.recv(1024)
            if not msg:
                break

            try:
                decoded = msg.decode("utf-8").strip()
            except:
                decoded = None

            # --- Comando de envio de arquivo ---
            if decoded and decoded.startswith("/file "):
                partes = decoded.split(" ", 2)
                if len(partes) == 3:
                    _, file_name, file_size = partes
                    file_size = int(file_size)
                    # Recebe os bytes do arquivo
                    received = b""
                    while len(received) < file_size:
                        chunk = conn.recv(min(1024, file_size - len(received)))
                        if not chunk:
                            break
                        received += chunk
                    # Repassa cabeçalho e bytes para todos os clientes (exceto remetente)
                    header = f"/file {file_name} {file_size}\n".encode("utf-8")
                    for cliente in list(clientes.keys()):
                        if cliente != conn:
                            try:
                                cliente.send(header)
                                sent = 0
                                while sent < file_size:
                                    chunk = received[sent:sent+1024]
                                    cliente.send(chunk)
                                    sent += len(chunk)
                            except:
                                cliente.close()
                                del clientes[cliente]
                else:
                    conn.send("[ERRO] Cabeçalho de arquivo inválido.\n".encode("utf-8"))

            # --- Comando /sair ---
            elif decoded == "/sair":
                conn.send("Você saiu do chat.\n".encode("utf-8"))
                break

            # --- Comando /users ---
            elif decoded == "/users":
                lista = ", ".join(clientes.values())
                conn.send(f"Usuários conectados: {lista}\n".encode("utf-8"))

            # --- Comando /private <nome> <mensagem> ---
            elif decoded and decoded.startswith("/private "):
                partes = decoded.split(" ", 2)  # divide em 3 partes
                if len(partes) < 3:
                    conn.send("Uso correto: /private <nome> <mensagem>\n".encode("utf-8"))
                else:
                    destino, mensagem_privada = partes[1], partes[2]
                    encontrado = False
                    for c, n in clientes.items():
                        if n == destino:
                            c.send(f"[PRIVADO de {nickname}] {mensagem_privada}\n".encode("utf-8"))
                            conn.send(f"[PRIVADO para {destino}] {mensagem_privada}\n".encode("utf-8"))
                            encontrado = True
                            break
                    if not encontrado:
                        conn.send(f"Usuário '{destino}' não encontrado.\n".encode("utf-8"))

            # --- Mensagem normal ---
            else:
                broadcast(msg, conn)

    except:
        pass
    finally:
        nickname = clientes.get(conn, "Desconhecido")
        print(f"[DESCONECTADO] {addr} ({nickname})")

        if conn in clientes:
            del clientes[conn]

        conn.close()
        for cliente in list(clientes.keys()):
            cliente.send(f"{nickname} saiu do chat.\n".encode("utf-8"))

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
print(f"[SERVIDOR INICIADO] Aguardando conexões em {HOST}:{PORT}...")

while True:
    conn, addr = server.accept()
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.start()
    print(f"[USUÁRIOS ATIVOS] {len(clientes) + 1}")
