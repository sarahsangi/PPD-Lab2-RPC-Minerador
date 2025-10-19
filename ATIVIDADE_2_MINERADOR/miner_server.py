import grpc
from concurrent import futures
import time
import hashlib
import random
import threading 

# Importa os arquivos gerados
import miner_pb2
import miner_pb2_grpc

# --- Variáveis Globais e Configurações ---
_ONE_DAY_IN_SECONDS = 60 * 60 * 24
PORT = '8080' 

# Dicionário de Transações (Tabela de Registros)
TRANSACTIONS = {}
CURRENT_TRANSACTION_ID = 0 
# Trava para acesso seguro à tabela de transações
TABLE_LOCK = threading.Lock() 

# --- Funções Auxiliares do Servidor ---

def _generate_new_challenge(transaction_id):
    """Gera um novo desafio (1-5) e TransactionID inicial."""
    global CURRENT_TRANSACTION_ID
    
    # Gera um desafio aleatório entre 1 (fácil) e 5 (difícil)
    challenge_level = random.randint(1, 5)
    
    with TABLE_LOCK:
        TRANSACTIONS[transaction_id] = {
            'challenge': challenge_level,
            'solution': "",     
            'winner': -1,       # -1 se pendente
            'solved': False
        }
        CURRENT_TRANSACTION_ID = transaction_id
        
    print(f"--- NOVO DESAFIO GERADO ---")
    print(f"TransactionID: {transaction_id}, Nível do Desafio (Zeros Iniciais): {challenge_level}")

def _check_challenge(challenge_level, solution_string):
    """Verifica se a string 'solution_string' resolve o desafio SHA-1."""
    if not solution_string:
        return False, ""
        
    # Calcula o hash SHA-1 da string submetida
    hash_object = hashlib.sha1(solution_string.encode('utf-8'))
    hex_dig = hash_object.hexdigest()
    
    # Verifica se o hash começa com a quantidade necessária de zeros
    target_prefix = '0' * challenge_level
    
    return hex_dig.startswith(target_prefix), hex_dig

# --- Implementação do Serviço RPC ---

class MinerServicer(miner_pb2_grpc.MinerServicer):
    
    def getTransactionID(self, request, context):
        """Retorna o valor atual da transação com desafio pendente."""
        with TABLE_LOCK:
            return miner_pb2.IntegerResponse(value=CURRENT_TRANSACTION_ID)

    def getChallenge(self, request, context):
        """Retorna o valor do desafio associado ao TransactionID."""
        tx_id = request.transactionID
        with TABLE_LOCK:
            if tx_id not in TRANSACTIONS:
                return miner_pb2.IntegerResponse(value=-1) # ID inválido
            
            return miner_pb2.IntegerResponse(value=TRANSACTIONS[tx_id]['challenge'])

    def getTransactionStatus(self, request, context):
        """Retorna 0 resolvido, 1 pendente, -1 inválido."""
        tx_id = request.transactionID
        
        with TABLE_LOCK:
            if tx_id not in TRANSACTIONS:
                return miner_pb2.IntegerResponse(value=-1) # ID inválido
            
            tx_data = TRANSACTIONS[tx_id]
        
        # Retorna 0 (resolvido) ou 1 (pendente)
        return miner_pb2.IntegerResponse(value=0 if tx_data['solved'] else 1)

    def getWinner(self, request, context):
        """Retorna o ClientID do vencedor (0 se não tem, -1 se ID inválido)."""
        tx_id = request.transactionID
        with TABLE_LOCK:
            if tx_id not in TRANSACTIONS:
                return miner_pb2.IntegerResponse(value=-1) # ID inválido
            
            winner_id = TRANSACTIONS[tx_id]['winner']
            # Retorna 0 se não tem vencedor (pendente)
            return miner_pb2.IntegerResponse(value=winner_id if winner_id != -1 else 0)

    def getSolution(self, request, context):
        """Retorna status, solução e desafio associado."""
        tx_id = request.transactionID
        with TABLE_LOCK:
            if tx_id not in TRANSACTIONS:
                return miner_pb2.SolutionData(status=-1, solution="", challenge=0) 

            tx_data = TRANSACTIONS[tx_id]
            status = 0 if tx_data['solved'] else 1
            
            return miner_pb2.SolutionData(
                status=status,
                solution=tx_data['solution'],
                challenge=tx_data['challenge']
            )

    def submitChallenge(self, request, context):
        """Submete uma solução. Retorna 1 válida, 0 inválida, 2 resolvido, -1 inválido ID."""
        
        tx_id = request.transactionID
        client_id = request.clientID
        solution = request.solution
        next_tx_id = tx_id + 1 # Determina o próximo ID fora do lock

        # Tenta pegar dados da transação
        with TABLE_LOCK:
            if tx_id not in TRANSACTIONS:
                return miner_pb2.IntegerResponse(value=-1) 

            tx_data = TRANSACTIONS[tx_id]

            if tx_data['solved']:
                print(f"Submissão ignorada de Cliente {client_id}: Desafio {tx_id} já resolvido.")
                return miner_pb2.IntegerResponse(value=2) 

            challenge_level = tx_data['challenge']
        
        # Verifica a solução SHA-1 (pode ser demorado, fora do lock)
        is_valid, final_hash = _check_challenge(challenge_level, solution)

        if is_valid:
            # Reentra no lock APENAS para registrar o resultado
            with TABLE_LOCK:
                # Checa novamente se alguém ganhou em concorrência
                if tx_data['solved']:
                    print(f"Corrida perdida: Cliente {client_id} chegou tarde.")
                    return miner_pb2.IntegerResponse(value=2)

                # Registra o vencedor
                tx_data['solution'] = final_hash 
                tx_data['winner'] = client_id
                tx_data['solved'] = True
                
                print(f"\n---!!! VENCEDOR !!!---")
                print(f"Transação {tx_id} resolvida pelo Cliente {client_id}")
                
                # O RETORNO RPC PODE ACONTECER AQUI, DEPOIS DO REGISTRO
                # A geração do próximo desafio (que pode demorar) será feita abaixo
                
            # Cria a próxima transação FORA DO LOCK PRINCIPAL (otimização)
            _generate_new_challenge(next_tx_id)
            
            return miner_pb2.IntegerResponse(value=1) # Solução válida
        else:
            print(f"Submissão inválida de Cliente {client_id} para Transação {tx_id}.")
            return miner_pb2.IntegerResponse(value=0) # Solução inválida


def serve():
    # Garante que o desafio TransactionID = 0 seja gerado ao iniciar
    _generate_new_challenge(0)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    miner_pb2_grpc.add_MinerServicer_to_server(MinerServicer(), server)
    
    server.add_insecure_port(f'localhost:{PORT}')
    server.start()
    print(f"Servidor Minerador gRPC iniciado em localhost:{PORT}. Aguardando clientes...")
    
    try:
        # Mantém o servidor rodando em loop
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        print("Servidor desligando...")
        server.stop(0)

if __name__ == '__main__':
    serve()