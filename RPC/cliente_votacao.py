"""
Sistema de Votação Distribuído - Cliente RPC
Interface simples para votar
"""

import xmlrpc.client
import sys

HOST = "localhost"
PORT = 8000

def main():
    # Conectar ao servidor
    servidor_url = f"http://{HOST}:{PORT}"
    
    if len(sys.argv) > 1:
        servidor_url = f"http://{sys.argv[1]}:{PORT}"
    
    print("=" * 50)
    print("SISTEMA DE VOTAÇÃO - CLIENTE")
    print("=" * 50)
    print(f"Servidor: {servidor_url}\n")
    
    try:
        proxy = xmlrpc.client.ServerProxy(servidor_url, allow_none=True)
    except:
        print("Erro ao conectar!")
        return
    
    nome = input("Seu nome: ").strip()
    if not nome:
        print("Nome inválido!")
        return
    
    while True:
        print("\n" + "=" * 50)
        print("MENU")
        print("=" * 50)
        print("1. Votar")
        print("2. Ver resultados")
        print("3. Sair")
        print("4. Resetar votação (administrador)")
        
        opcao = input("\nOpção: ").strip()
        
        if opcao == "1":
            print("\nQual a melhor linguagem de programação?")
            print("1. Python")
            print("2. Java")
            print("3. JavaScript")
            print("4. C++")
            
            voto = input("\nEscolha (1-4): ").strip()
            linguagens = {"1": "Python", "2": "Java", "3": "JavaScript", "4": "C++"}
            
            if voto in linguagens:
                resultado = proxy.votar(linguagens[voto], nome)
                print(f"\n{resultado['mensagem']}")
            else:
                print("\nOpção inválida!")
        
        elif opcao == "2":
            resultado = proxy.ver_resultados()
            print("\n" + "=" * 50)
            print("RESULTADOS DA VOTAÇÃO")
            print("=" * 50)
            
            for linguagem, votos in resultado['votos'].items():
                porcentagem = (votos / resultado['total'] * 100) if resultado['total'] > 0 else 0
                barra = "█" * int(porcentagem / 5)
                print(f"{linguagem:<12} {votos:>3} votos  {barra} {porcentagem:.1f}%")
            
            print("-" * 50)
            print(f"Total: {resultado['total']} votos de {resultado['votantes']} votantes")
        
        elif opcao == "3":
            print("\nAté logo!")
            break

        elif opcao == "4":
            senha = input("\nDigite a senha de administrador para resetar a votação: ").strip()
            resultado = proxy.resetar(senha)
            print(f"\n{resultado['mensagem']}")
        
        else:
            print("\nOpção inválida!")

if __name__ == "__main__":
    main()
