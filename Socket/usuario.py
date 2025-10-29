import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox
import sys

# Configuração do cliente
HOST = "172.31.75.183"  # trocas de ip para conectar a outros servidores
PORT = 5001

root = tk.Tk()
root.withdraw()  # esconder janela principal só para perguntar o nome
nickname = simpledialog.askstring("Login", "Digite seu nome de usuário:")

if not nickname:
    print('Nickname vazio, encerrando.')
    sys.exit()

# Criar socket e conectar
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect((HOST, PORT))
    print('Conectado ao servidor!')
except Exception as e:
    print(f'Erro ao conectar: {e}')
    messagebox.showerror("Erro de conexão", f"Não foi possível conectar ao servidor: {e}")
    root.destroy()
    sys.exit()

# Enviar nickname ao servidor
try:
    client.send(nickname.encode("utf-8"))
except Exception as e:
    print(f'Erro ao enviar nickname: {e}')
    messagebox.showerror("Erro", f"Erro ao enviar nickname: {e}")
    root.destroy()
    sys.exit()

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Chat - {nickname}")

        # area do chat
        self.chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=20, state="disabled")
        self.chat_area.pack(padx=10, pady=10)

        # campo de entrada
        self.msg_entry = tk.Entry(root, width=40)
        self.msg_entry.pack(side=tk.LEFT, padx=10, pady=10)
        self.msg_entry.bind("<Return>", self.send_msg)

        # Botão enviar
        self.send_btn = tk.Button(root, text="Enviar", command=self.send_msg)
        self.send_btn.pack(side=tk.LEFT, padx=10, pady=10)

        # Thread para receber mensagens
        threading.Thread(target=self.receive, daemon=True).start()

    def send_msg(self, event=None):
        msg = self.msg_entry.get()
        self.msg_entry.delete(0, tk.END)
        if msg.strip() != "":
            client.send(msg.encode("utf-8"))
            if msg.strip() == "/sair":
                client.close()
                self.root.quit()

    def send_file(self):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename()
        if not file_path:
            return
        import os
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        try:
            header = f"/file {file_name} {file_size}\n"
            client.send(header.encode("utf-8"))
            with open(file_path, "rb") as f:
                while True:
                    chunk = f.read(1024)
                    if not chunk:
                        break
                    client.send(chunk)
            self.chat_area.config(state="normal")
            self.chat_area.insert(tk.END, f"[Você enviou o arquivo: {file_name}]\n")
            self.chat_area.config(state="disabled")
            self.chat_area.see(tk.END)
        except Exception as e:
            self.chat_area.config(state="normal")
            self.chat_area.insert(tk.END, f"[Erro ao enviar arquivo: {e}]\n")
            self.chat_area.config(state="disabled")
            self.chat_area.see(tk.END)

    def receive(self):
        import os
        while True:
            try:
                msg = client.recv(1024)
                if not msg:
                    break
                try:
                    decoded = msg.decode("utf-8")
                except:
                    decoded = None
                if decoded and decoded.startswith("/file "):
                    partes = decoded.strip().split(" ", 2)
                    if len(partes) == 3:
                        _, file_name, file_size = partes
                        file_size = int(file_size)
                        received = b""
                        while len(received) < file_size:
                            chunk = client.recv(min(1024, file_size - len(received)))
                            if not chunk:
                                break
                            received += chunk
                        save_path = os.path.join(os.getcwd(), file_name)
                        with open(save_path, "wb") as f:
                            f.write(received)
                        self.chat_area.config(state="normal")
                        self.chat_area.insert(tk.END, f"[Arquivo recebido: {file_name} salvo em {save_path}]\n")
                        self.chat_area.config(state="disabled")
                        self.chat_area.see(tk.END)
                        if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                            self.add_open_image_button(save_path, file_name)
                    else:
                        self.chat_area.config(state="normal")
                        self.chat_area.insert(tk.END, "[Erro ao receber cabeçalho de arquivo]\n")
                        self.chat_area.config(state="disabled")
                        self.chat_area.see(tk.END)
                else:
                    try:
                        msg_str = msg.decode("utf-8")
                    except:
                        msg_str = str(msg)
                    self.chat_area.config(state="normal")
                    self.chat_area.insert(tk.END, msg_str + "\n")
                    self.chat_area.config(state="disabled")
                    self.chat_area.see(tk.END)
            except Exception as e:
                print(f'Erro na thread de recebimento: {e}')
                self.chat_area.config(state="normal")
                self.chat_area.insert(tk.END, f"[Erro ao receber: {e}]\n")
                self.chat_area.config(state="disabled")
                self.chat_area.see(tk.END)
                break

    def add_open_image_button(self, path, file_name):
        def open_image():
            import tkinter as tk
            from PIL import Image, ImageTk
            win = tk.Toplevel(self.root)
            win.title(file_name)
            img = Image.open(path)
            img.thumbnail((400, 400))
            photo = ImageTk.PhotoImage(img)
            label = tk.Label(win, image=photo)
            label.image = photo
            win.photo = photo
            label.pack()
        btn = tk.Button(self.root, text=f"Abrir {file_name}", command=open_image)
        btn.pack(padx=10, pady=2)

if __name__ == "__main__":
    try:
        root.deiconify()
        app = ChatApp(root)
        root.mainloop()
    except Exception as e:
        print(f'Erro ao iniciar interface: {e}')
