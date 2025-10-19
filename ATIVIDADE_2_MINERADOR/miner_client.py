import grpc
import miner_pb2
import miner_pb2_grpc
import hashlib
import threading
import time
import sys
import random 

# --- Variáveis Globais de Controle ---

FOUND_SOLUTION = None                   # Armazena a string de entrada que resolve o desafio
MINING_STOP_EVENT = threading.Event()   # Sinalizador para interromper as threads de mineração
CLIENT_ID = random.randint(1000, 9999)  # ID exclusivo para este cliente

# --- Funções de Mineração Concorrente ---

def mine_challenge(challenge_level, thread_id):
    """
    Função executada por cada thread. Busca um hash SHA-1 que comece com 'challenge_level' zeros.
    """
    global FOUND_SOLUTION
    
    # Define o prefixo de zeros que o hash precisa ter
    target_prefix = '0' * challenge_level
    counter = 0

    # Continua a busca até que uma solução seja encontrada ou sinalizada
    while not MINING_STOP_EVENT.is_set():
        # Gera uma string de entrada única (ex: ClientID-ThreadID-Contador)
        input_string = f"{CLIENT_ID}-{thread_id}-{counter}" 
        
        # Calcula o hash SHA-1 da string
        hash_object = hashlib.sha1(input_string.encode('utf-8'))
        hex_dig = hash_object.hexdigest()
        
        # Verifica se o hash atende ao desafio
        if hex_dig.startswith(target_prefix):
            # Solução encontrada: armazena e sinaliza o fim para outras threads
            FOUND_SOLUTION = input_string
            MINING_STOP_EVENT.set()
            print(f"\n[Thread {thread_id}] Solução encontrada! Input: {input_string}")
            print(f"Hash: {hex_dig}")
            return
        
        counter += 1
        # Feedback visual simples (opcional)
        if counter % 100000 == 0:
            sys.stdout.write(f"\r[Thread {thread_id}] Tentativas: {counter/1000000:.1f}M...")
            sys.stdout.flush()

def start_mining(stub, num_threads=4):
    """
    Coordena as etapas da mineração (Passos 1 a 6 do item 'Mine' do menu).
    """
    global FOUND_SOLUTION
    global MINING_STOP_EVENT
    
    try:
        # 1. Buscar transactionID atual
        response_id = stub.getTransactionID(miner_pb2.Empty())
        current_tx_id = response_id.value
        print(f"\n[Mine] Buscando Transação ID: {current_tx_id}")

        # 2. Buscar a challenge (desafio)
        request_challenge = miner_pb2.TransactionIDRequest(transactionID=current_tx_id)
        response_challenge = stub.getChallenge(request_challenge)
        challenge_level = response_challenge.value

        if challenge_level == -1:
            print("Erro: Transação ID inválida ou não existente no servidor.")
            return

        print(f"[Mine] Desafio atual: Encontrar um SHA-1 com {challenge_level} zeros iniciais.")
        
        # Reinicia o estado para a nova mineração
        FOUND_SOLUTION = None
        MINING_STOP_EVENT.clear()
        
        # 3. Buscar, localmente, uma solução (usando múltiplas threads)
        threads = []
        print(f"[Mine] Iniciando busca em {num_threads} threads...")
        for i in range(num_threads):
            t = threading.Thread(target=mine_challenge, args=(challenge_level, i+1))
            threads.append(t)
            t.start()

        # Aguarda que uma solução seja encontrada
        while not FOUND_SOLUTION and not MINING_STOP_EVENT.is_set():
            time.sleep(0.1)

        # 4. Interrompe todas as threads após encontrar a solução
        MINING_STOP_EVENT.set()
        for t in threads:
            t.join() 
            
        if not FOUND_SOLUTION:
            print("[Mine] Mineração interrompida ou falhou antes de encontrar uma solução.")
            return

        # 5. Submeter a solução ao servidor e aguardar resultado
        print(f"\n[Mine] Submetendo solução: '{FOUND_SOLUTION}'")
        request_submit = miner_pb2.SubmitChallengeRequest(
            transactionID=current_tx_id, 
            clientID=CLIENT_ID, 
            solution=FOUND_SOLUTION
        )
        response_submit = stub.submitChallenge(request_submit)
        submit_status = response_submit.value

        # 6. Imprimir/Decodificar resposta do servidor
        print("\n--- Resultado da Submissão ---")
        if submit_status == 1:
            print(f"Sucesso! Solução validada. Você ({CLIENT_ID}) é o vencedor da Transação {current_tx_id}!")
        elif submit_status == 0:
            print("Inválido. A solução submetida não atende ao desafio.")
        elif submit_status == 2:
            print("Atrasado. O desafio já havia sido solucionado por outro minerador.")
        elif submit_status == -1:
            print("Erro: Transação ID inválida.")
        else:
            print(f"Resposta desconhecida do servidor: {submit_status}")
            
    except grpc.RpcError as e:
        print(f"Erro de comunicação RPC: {e.details()}")
    except KeyboardInterrupt:
        MINING_STOP_EVENT.set()
        print("\nMineração interrompida pelo usuário.")


# --- Função Principal do Cliente ---

def run():
    # Conexão RPC com o servidor (ajuste a porta se necessário)
    with grpc.insecure_channel('localhost:8080') as channel:
        stub = miner_pb2_grpc.MinerStub(channel)

        print(f"Cliente Minerador ID: {CLIENT_ID} iniciado.")
        
        while True:
            print("\n--- Menu do Cliente RPC ---")
            print("1. get Transaction ID")
            print("2. get Challenge")
            print("3. get Transaction Status")
            print("4. get Winner")
            print("5. get Solution")
            print("6. Mine (Inicia a mineração)")
            print("0. Sair")
            
            choice = input("Escolha a opção: ")
            
            try:
                if choice == '0':
                    print("Encerrando cliente.")
                    break

                if choice == '6':
                    # Chama o coordenador de mineração
                    start_mining(stub, num_threads=4)
                    continue

                # Prepara o Request para chamadas que exigem TransactionID
                if choice in ('2', '3', '4', '5'):
                    tx_id = int(input("Digite o TransactionID: "))
                    request = miner_pb2.TransactionIDRequest(transactionID=tx_id)
                else:
                    request = miner_pb2.Empty() # Para getTransactionID

                # Lógica de chamadas RPC
                if choice == '1':
                    response = stub.getTransactionID(request)
                    print(f"ID da Transação Corrente: {response.value}")
                
                elif choice == '2':
                    response = stub.getChallenge(request)
                    if response.value == -1:
                        print("Erro: ID de transação inválido.")
                    else:
                        print(f"Desafio da Transação {tx_id}: {response.value} zeros iniciais.")

                elif choice == '3':
                    response = stub.getTransactionStatus(request)
                    if response.value == 0:
                        print(f"Status: Transação {tx_id} RESOLVIDA.")
                    elif response.value == 1:
                        print(f"Status: Transação {tx_id} PENDENTE.")
                    else:
                        print(f"Erro: ID de transação inválido.")
                        
                elif choice == '4':
                    response = stub.getWinner(request)
                    if response.value == -1:
                        print("Erro: ID de transação inválido.")
                    elif response.value == 0:
                        print(f"Transação {tx_id} não possui vencedor (pendente).")
                    else:
                        print(f"Vencedor da Transação {tx_id}: Cliente ID {response.value}")

                elif choice == '5':
                    response = stub.getSolution(request)
                    if response.status == -1:
                        print("Erro: ID de transação inválido.")
                    else:
                        status_str = "RESOLVIDA" if response.status == 0 else "PENDENTE"
                        print(f"--- Dados da Transação {tx_id} ---")
                        print(f"Status: {status_str}")
                        print(f"Desafio (Nível): {response.challenge}")
                        if response.status == 0:
                            print(f"Solução (Hash Vencedor): {response.solution}")
                        else:
                            print("Solução: Ainda não encontrada.")
                
                else:
                    print("Opção inválida.")
                    
            except ValueError:
                print("Erro de entrada: Digite um número inteiro válido para o ID.")
            except grpc.RpcError as e:
                print(f"Erro de comunicação RPC: {e.details()}")
            except Exception as e:
                print(f"Ocorreu um erro: {e}")

if __name__ == '__main__':
    run()
