"""
Sistema de Votação Distribuído - Servidor RPC
Simples e direto: permite que múltiplos clientes votem em tempo real
"""

from xmlrpc.server import SimpleXMLRPCServer
import threading

HOST = "0.0.0.0"
PORT = 8000

class SistemaVotacao:
    """Gerencia votos de múltiplos clientes"""
    
    def __init__(self):
        self.votos = {"Python": 0, "Java": 0, "JavaScript": 0, "C++": 0}
        self.votantes = set()  # Evita voto duplicado
        self.lock = threading.Lock()
    
    def votar(self, linguagem, nome_votante):
        """Registra um voto"""
        with self.lock:
            if nome_votante in self.votantes:
                return {"sucesso": False, "mensagem": "Você já votou!"}
            
            if linguagem not in self.votos:
                return {"sucesso": False, "mensagem": "Linguagem inválida!"}
            
            self.votos[linguagem] += 1
            self.votantes.add(nome_votante)
            
            print(f"[VOTO] {nome_votante} votou em {linguagem}")
            return {"sucesso": True, "mensagem": f"Voto em {linguagem} registrado!"}
    
    def ver_resultados(self):
        """Retorna os resultados atuais"""
        with self.lock:
            total = sum(self.votos.values())
            return {
                "votos": self.votos,
                "total": total,
                "votantes": len(self.votantes)
            }
    
    def resetar(self, senha):
        """Reseta a votação (requer senha)"""
        if senha != "admin123":
            return {"sucesso": False, "mensagem": "Senha incorreta!"}
        
        with self.lock:
            self.votos = {"Python": 0, "Java": 0, "JavaScript": 0, "C++": 0}
            self.votantes.clear()
            print("[RESETADO] Votação resetada!")
            return {"sucesso": True, "mensagem": "Votação resetada!"}

def main():
    print("=" * 50)
    print("SISTEMA DE VOTAÇÃO DISTRIBUÍDO - SERVIDOR RPC")
    print("=" * 50)
    print(f"Porta: {PORT}")
    print("Aguardando clientes...\n")
    
    votacao = SistemaVotacao()
    server = SimpleXMLRPCServer((HOST, PORT), allow_none=True)
    server.register_instance(votacao)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServidor encerrado.")

if __name__ == "__main__":
    main()
