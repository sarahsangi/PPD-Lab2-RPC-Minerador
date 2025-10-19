import grpc
from concurrent import futures
import grpcCalc_pb2
import grpcCalc_pb2_grpc

class apiServicer(grpcCalc_pb2_grpc.apiServicer):
    def add(self, request, context):
        return grpcCalc_pb2.result(num=request.numOne + request.numTwo)

    def sub(self, request, context):
        return grpcCalc_pb2.result(num=request.numOne - request.numTwo)

    def mult(self, request, context):
        return grpcCalc_pb2.result(num=request.numOne * request.numTwo)

    def div(self, request, context):
        if request.numTwo == 0:
            return grpcCalc_pb2.result(num=0)
        return grpcCalc_pb2.result(num=int(request.numOne / request.numTwo))

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grpcCalc_pb2_grpc.add_apiServicer_to_server(apiServicer(), server)
    server.add_insecure_port('[::]:8080')
    server.start()
    print("Servidor gRPC da calculadora rodando na porta 8080...")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()

import grpc
from concurrent import futures
import grpcCalc_pb2
import grpcCalc_pb2_grpc

class apiServicer(grpcCalc_pb2_grpc.apiServicer):
    def add(self, request, context):
        return grpcCalc_pb2.result(num=request.numOne + request.numTwo)

    def sub(self, request, context):
        return grpcCalc_pb2.result(num=request.numOne - request.numTwo)

    def mult(self, request, context):
        return grpcCalc_pb2.result(num=request.numOne * request.numTwo)

    def div(self, request, context):
        if request.numTwo == 0:
            return grpcCalc_pb2.result(num=0)
        return grpcCalc_pb2.result(num=int(request.numOne / request.numTwo))

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grpcCalc_pb2_grpc.add_apiServicer_to_server(apiServicer(), server)
    server.add_insecure_port('localhost:8080')    

    server.start()
    print("Servidor gRPC da calculadora rodando na porta 8080...")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
