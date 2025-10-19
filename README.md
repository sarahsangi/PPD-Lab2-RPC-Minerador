# PPD - Laboratório II: Sistema Distribuído RPC (Calculadora e Minerador)

Este projeto implementa um sistema distribuído Cliente/Servidor usando o conceito de Chamada de Procedimento Remoto (RPC), utilizando a tecnologia **gRPC do Google**.

**ALUNA:** Sarah Candido Sangi

---

## 1. Organização do Repositório

O projeto segue a arquitetura Cliente/Servidor e está organizado em duas pastas principais, uma para cada atividade:

1. **`ATIVIDADE_1_CALCULADORA/`**: Implementação da calculadora RPC.
2. **`ATIVIDADE_2_MINERADOR/`**: Protótipo Cliente/Servidor de mineração de criptomoedas com concorrência.

## 2. Instruções de Compilação e Execução

### 2.1. Configuração do Ambiente

1.  **Python:** Certifique-se de que o Python 3.x está instalado.
2.  **Dependências:** Instale as bibliotecas necessárias (`grpcio` para RPC e `pybreaker` para a calculadora).
   
    ```bash
    pip install grpcio grpcio-tools pybreaker
    ```

### 2.2. Geração dos Stubs RPC (Compilação da Interface)

Os *stubs* gerados são as interfaces que o programador usa para abstrair a comunicação de rede. Execute os comandos na raiz do projeto:

1.  **Calculadora (Atividade 1):**
   
    ```bash
    python -m grpc_tools.protoc -I. --python_out=./ATIVIDADE_1_CALCULADORA --grpc_python_out=./ATIVIDADE_1_CALCULADORA ATIVIDADE_1_CALCULADORA/grpcCalc.proto
    ```
    
2.  **Minerador (Atividade 2):**
   
    ```bash
    python -m grpc_tools.protoc -I. --python_out=./ATIVIDADE_2_MINERADOR --grpc_python_out=./ATIVIDADE_2_MINERADOR ATIVIDADE_2_MINERADOR/miner.proto
    ```

### 2.3. Execução das Aplicações

É fundamental que o processo servidor seja iniciado **antes** do processo cliente.

| Atividade | Terminal 1 (Servidor) | Terminal 2 (Cliente) |
| :--- | :--- | :--- |
| **Atividade 1** | `python ATIVIDADE_1_CALCULADORA/server.py` | `python ATIVIDADE_1_CALCULADORA/client.py` |
| **Atividade 2** | `python ATIVIDADE_2_MINERADOR/miner_server.py` | `python ATIVIDADE_2_MINERADOR/miner_client.py` |

---

## 3. Relatório Técnico (Análise de Conformidade)

Abaixo está um resumo da metodologia de implementação e os resultados-chave.

### I. Atividade 1: Calculadora RPC

| Item | Conformidade | Detalhe |
| :--- | :--- | :--- |
| **Requisitos** | **ATENDIDO** | Implementa as quatro operações básicas (Soma, Subtração, Multiplicação e Divisão). |
| **Interatividade**| **ATENDIDO** | O cliente é um serviço interativo, utilizando um menu para a escolha das operações. |

### II. Atividade 2: Minerador de Criptomoedas

O projeto cumpre o requisito de construir um protótipo Cliente/Servidor de minerador de criptomoedas em Python/gRPC.

| Item | Conformidade | Detalhe |
| :--- | :--- | :--- |
| **Tabela de Registros** | **ATENDIDO** | O servidor mantém os registros de **TransactionID**, **Challenge**, **Solution**, e **Winner**. O servidor gera um novo desafio com TransactionID $=0$ ao ser carregado. |
| **Interface RPC** | **ATENDIDO** | Todas as chamadas RPC (`get TransactionID`, `submit Challenge`, `get Winner`, etc.) são disponibilizadas e possuem as estruturas de dados e retornos especificados. |
| **Método `Mine` (Concorrência)** | **ATENDIDO** | A função `Mine` do cliente executa a busca da solução SHA-1 de forma concorrente, conforme sugerido, usando **múltiplas *threads***. |
| **Prova de Trabalho** | **ATENDIDO** | O sistema executa o ciclo completo: o cliente submete a solução; o servidor a valida com SHA-1; o servidor registra o `ClientID` vencedor e gera um novo desafio, retornando `Sucesso!`. |

## 4. Vídeo de Demonstração (Obrigatório)

A execução completa e a validação de todos os requisitos do minerador (Mineração, Submissão, Status, Vencedor, Solução) podem ser verificadas no vídeo.

**LINK PARA O VÍDEO:** [Link para o Vídeo de 5 minutos]
