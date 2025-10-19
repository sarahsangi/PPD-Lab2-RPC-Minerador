import grpc
from concurrent import futures
import threading
import hashlib
import random
import miner_pb2
import miner_pb2_grpc

# Dicionário principal: guarda todas as transações e seus dados
transactions = {}
lock = threading.Lock()  # Garante acesso seguro ao dicionário entre threads

# Gera um novo desafio e o adiciona à tabela
def _generate_new_challenge(transaction_id):
    challenge_level = random.randint(1, 5)  # nível de dificuldade (nº de zeros no hash)
    transactions[transaction_id] = {
        "TransactionID": transaction_id,
        "Challenge": challenge_level,
        "Solution": "",
        "Winner": -1
    }
    print(f"Novo desafio criado -> TransactionID: {transaction_id}, Challenge: {challenge_level}")

# Implementação dos métodos RPC do servidor
class MinerService(miner_pb2_grpc.apiServicer):

    def getTransactionID(self, request, context):
        with lock:
            # Busca a transação atual (ainda sem vencedor)
            for t_id, data in transactions.items():
                if data["Winner"] == -1:
                    return miner_pb2.IntegerResponse(value=t_id)
            # Caso todas tenham vencedor, gera nova
            new_id = len(transactions)
            _generate_new_challenge(new_id)
            return miner_pb2.IntegerResponse(value=new_id)

    def getChallenge(self, request, context):
        t_id = request.transactionId
        if t_id in transactions:
            return miner_pb2.IntegerResponse(value=transactions[t_id]["Challenge"])
        return miner_pb2.IntegerResponse(value=-1)

    def getTransactionStatus(self, request, context):
        t_id = request.transactionId
        if t_id not in transactions:
            return miner_pb2.IntegerResponse(value=-1)
        # 0 = resolvido, 1 = pendente
        status = 1 if transactions[t_id]["Winner"] == -1 else 0
        return miner_pb2.IntegerResponse(value=status)

    def submitChallenge(self, request, context):
        t_id = request.transactionId
        if t_id not in transactions:
            return miner_pb2.IntegerResponse(value=-1)

        # Se já houver vencedor, retorna 2
        if transactions[t_id]["Winner"] != -1:
            return miner_pb2.IntegerResponse(value=2)

        # Verifica se o hash da solução atende o desafio
        challenge = transactions[t_id]["Challenge"]
        sha1_hash = hashlib.sha1(request.solution.encode()).hexdigest()
        if sha1_hash.startswith("0" * challenge):
            with lock:
                transactions[t_id]["Solution"] = request.solution
                transactions[t_id]["Winner"] = request.clientId
                print(f"Transação {t_id} solucionada pelo cliente {request.clientId}")
                _generate_new_challenge(len(transactions))
            return miner_pb2.IntegerResponse(value=1)
        else:
            return miner_pb2.IntegerResponse(value=0)

    def getWinner(self, request, context):
        t_id = request.transactionId
        if t_id not in transactions:
            return miner_pb2.IntegerResponse(value=-1)
        winner = transactions[t_id]["Winner"]
        return miner_pb2.IntegerResponse(value=winner)

    def getSolution(self, request, context):
        t_id = request.transactionId
        if t_id not in transactions:
            return miner_pb2.SolutionData(status=-1, solution="", challenge=-1)
        data = transactions[t_id]
        status = 1 if data["Winner"] == -1 else 0
        return miner_pb2.SolutionData(
            status=status,
            solution=data["Solution"],
            challenge=data["Challenge"]
        )

# Inicializa o servidor e mantém ele rodando até interrupção manual
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    miner_pb2_grpc.add_apiServicer_to_server(MinerService(), server)
    server.add_insecure_port('[::]:8080')
    server.start()
    print("Servidor RPC de mineração rodando na porta 8080...")

    # Gera o primeiro desafio (TransactionID = 0)
    _generate_new_challenge(0)
    server.wait_for_termination()

if __name__ == "__main__":
    serve()