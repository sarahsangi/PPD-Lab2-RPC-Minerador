import grpc
import miner_pb2
import miner_pb2_grpc
import hashlib
import threading
import random
import string
import sys

# Gera uma string aleatória que será usada como tentativa de solução
def generate_candidate():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

# Cada thread tenta encontrar uma string cuja hash SHA-1 começa com '0' * challenge
def mine_challenge(challenge, found_flag, result_holder, thread_id):
    counter = 0
    while not found_flag.is_set():
        candidate = generate_candidate()
        sha1_hash = hashlib.sha1(candidate.encode()).hexdigest()
        if sha1_hash.startswith("0" * challenge):
            result_holder["solution"] = candidate
            found_flag.set()
            print(f"\nThread {thread_id} encontrou solução: {candidate}")
            break
        counter += 1
        if counter % 100000 == 0:
            sys.stdout.write(f"\r[Thread {thread_id}] Tentativas: {counter:,}...")
            sys.stdout.flush()

# Procedimento completo de mineração: busca o desafio, minera e envia
def start_mining(stub, client_id):
    t_id = stub.getTransactionID(miner_pb2.Void()).value
    challenge = stub.getChallenge(miner_pb2.TransactionID(transactionId=t_id)).value
    print(f"\nMinerando transação {t_id} com desafio: {challenge} zeros iniciais...")

    found_flag = threading.Event()
    result_holder = {}

    # Cria múltiplas threads minerando em paralelo
    threads = []
    for i in range(4):
        t = threading.Thread(target=mine_challenge, args=(challenge, found_flag, result_holder, i))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    solution = result_holder.get("solution", "")
    if solution:
        print(f"Submetendo solução encontrada: {solution}")
        response = stub.submitChallenge(
            miner_pb2.ChallengeArgs(transactionId=t_id, clientId=client_id, solution=solution)
        )
        print(f"Resultado da submissão: {response.value}")
    else:
        print("Nenhuma solução encontrada.")

# Exibe menu e permite interação com o servidor
def menu(stub, client_id):
    while True:
        print("\n=== Menu do Cliente Minerador ===")
        print("1 - getTransactionID")
        print("2 - getChallenge")
        print("3 - getTransactionStatus")
        print("4 - getWinner")
        print("5 - getSolution")
        print("6 - Mine (minerar desafio)")
        print("0 - Sair")

        op = input("Escolha a opção: ")

        try:
            if op == '1':
                res = stub.getTransactionID(miner_pb2.Void())
                print("TransactionID atual:", res.value)
            elif op == '2':
                t_id = int(input("TransactionID: "))
                res = stub.getChallenge(miner_pb2.TransactionID(transactionId=t_id))
                print("Desafio:", res.value)
            elif op == '3':
                t_id = int(input("TransactionID: "))
                res = stub.getTransactionStatus(miner_pb2.TransactionID(transactionId=t_id))
                print("Status:", res.value)
            elif op == '4':
                t_id = int(input("TransactionID: "))
                res = stub.getWinner(miner_pb2.TransactionID(transactionId=t_id))
                print("Vencedor:", res.value)
            elif op == '5':
                t_id = int(input("TransactionID: "))
                res = stub.getSolution(miner_pb2.TransactionID(transactionId=t_id))
                print(f"Status: {res.status} | Solução: {res.solution} | Desafio: {res.challenge}")
            elif op == '6':
                start_mining(stub, client_id)
            elif op == '0':
                print("Encerrando cliente.")
                break
            else:
                print("Opção inválida.")
        except Exception as e:
            print("Erro:", e)

if __name__ == "__main__":
    # Conecta ao servidor e inicia o menu
    channel = grpc.insecure_channel('localhost:8080')
    stub = miner_pb2_grpc.apiStub(channel)
    client_id = random.randint(1000, 9999)
    print(f"Cliente minerador iniciado. ID: {client_id}")
    menu(stub, client_id)