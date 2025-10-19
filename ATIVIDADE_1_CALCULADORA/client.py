import grpc
import grpcCalc_pb2
import grpcCalc_pb2_grpc
import pybreaker

breaker = pybreaker.CircuitBreaker(fail_max=2, reset_timeout=2)

@breaker
def connect():
    channel = grpc.insecure_channel('localhost:8080')
    client = grpcCalc_pb2_grpc.apiStub(channel)

    while True:
        try:
            print('\nOperações disponíveis:')
            print('1 - Adição')
            print('2 - Subtração')
            print('3 - Multiplicação')
            print('4 - Divisão')
            print('0 - Sair')

            op = input('Escolha a operação: ')

            if op == '0':
                print("Finalizando a aplicação cliente.")
                break

            if op not in ('1', '2', '3', '4'):
                print("Opção inválida.")
                continue

            x = int(input('Entre com o primeiro número: '))
            y = int(input('Entre com o segundo número: '))

            if op == '1':
                res = client.add(grpcCalc_pb2.args(numOne=x, numTwo=y))
            elif op == '2':
                res = client.sub(grpcCalc_pb2.args(numOne=x, numTwo=y))
            elif op == '3':
                res = client.mult(grpcCalc_pb2.args(numOne=x, numTwo=y))
            elif op == '4':
                res = client.div(grpcCalc_pb2.args(numOne=x, numTwo=y))

            print(f"Resultado: {res.num}")

        except pybreaker.CircuitBreakerError:
            print("Erro de circuito (muitas falhas consecutivas).")
        
        except ValueError:
            print("Erro de entrada: Por favor, digite apenas números inteiros.")

        except grpc.RpcError as e:
            print(f"Erro de Conexão/RPC: {e.details()}")

        except Exception as e:
            print("Erro inesperado:", e)

if __name__ == '__main__':
    connect()
