import grpc
from concurrent import futures
import grpcCalc_pb2
import grpcCalc_pb2_grpc

# Implementa o serviço da calculadora
class apiServicer(grpcCalc_pb2_grpc.apiServicer):
    # Soma dois números
    def add(self, request, context):
        return grpcCalc_pb2.result(num=request.numOne + request.numTwo)

    # Subtrai dois números
    def sub(self, request, context):
        return grpcCalc_pb2.result(num=request.numOne - request.numTwo)

    # Multiplica dois números
    def mult(self, request, context):
        return grpcCalc_pb2.result(num=request.numOne * request.numTwo)

    # Divide dois números (tratando divisão por zero)
    def div(self, request, context):
        if request.numTwo == 0:
            return grpcCalc_pb2.result(num=0)
        return grpcCalc_pb2.result(num=int(request.numOne / request.numTwo))

# Função que cria e executa o servidor
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grpcCalc_pb2_grpc.add_apiServicer_to_server(apiServicer(), server)
    server.add_insecure_port('[::]:8080')
    server.start()
    print("Servidor gRPC da calculadora rodando na porta 8080...")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
