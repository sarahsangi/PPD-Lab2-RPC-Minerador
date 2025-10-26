# PPD - Laboratório II: Sistema Distribuído RPC (Calculadora e Minerador)

Este projeto implementa um sistema distribuído no modelo **Cliente/Servidor**, utilizando o conceito de **Chamada de Procedimento Remoto (RPC)** com a tecnologia **gRPC** em Python.  

O trabalho foi dividido em duas partes: uma **calculadora distribuída** e um **protótipo de minerador de criptomoedas com execução concorrente**.

**Aluna:** Sarah Candido Sangi  
**Disciplina:** Programação Paralela e Distribuída (PPD)

---

## 1. Organização do Repositório

O projeto está organizado em duas pastas principais, separando as atividades:

1. **`ATIVIDADE_1_CALCULADORA/`** – Implementação de uma calculadora RPC.  
2. **`ATIVIDADE_2_MINERADOR/`** – Protótipo de mineração de criptomoedas com uso de múltiplas *threads*.

---

## 2. Instruções para Compilação e Execução

### 2.1. Requisitos

1. Ter o **Python 3.x** instalado.  
2. Instalar as dependências necessárias:
      
    ```bash
    pip install grpcio grpcio-tools pybreaker
    ```

### 2.2. Geração dos Stubs RPC

Os *stubs* são arquivos gerados automaticamente a partir das definições dos arquivos `.proto`, e são usados para que cliente e servidor se comuniquem corretamente.

Na raiz do projeto, execute:

**Atividade 1 – Calculadora**
   
   ```bash
    python -m grpc_tools.protoc -I. --python_out=./ATIVIDADE_1_CALCULADORA --grpc_python_out=./ATIVIDADE_1_CALCULADORA ATIVIDADE_1_CALCULADORA/grpcCalc.proto
   ```
    
**Atividade 2 – Minerador**

   ```bash
    python -m grpc_tools.protoc -I. --python_out=./ATIVIDADE_2_MINERADOR --grpc_python_out=./ATIVIDADE_2_MINERADOR ATIVIDADE_2_MINERADOR/miner.proto
   ```

### 2.3. Execução das Aplicações

É importante iniciar sempre o **servidor** antes do **cliente**.

| Atividade | Servidor | Cliente |
|:-----------|:----------|:----------|
| **Atividade 1** | `python ATIVIDADE_1_CALCULADORA/server.py` | `python ATIVIDADE_1_CALCULADORA/client.py` |
| **Atividade 2** | `python ATIVIDADE_2_MINERADOR/miner_server.py` | `python ATIVIDADE_2_MINERADOR/miner_client.py` |

---

## 3. Relatório Técnico (Metodologia e Resultados Encontrados)

### 3.1. Metodologia de Implementação

A arquitetura Cliente/Servidor foi construída utilizando o **gRPC em Python**, aproveitando a geração automática de código (stubs) a partir da definição da interface (.proto).

**Concorrência e Sincronização**

 - **No Cliente (Mine)**: A função de mineração utiliza **múltiplas threads** para realizar a busca da solução SHA-1 (nonce) localmente. Este paralelismo atende à sugestão das instruções, otimizando o tempo de descoberta da Solution.

 - **No Servidor**: Foi implementado o uso de mecanismos de sincronização (locks) para garantir que o acesso e a alteração da tabela de transações (TRANSACTIONS) sejam atômicos, prevenindo race conditions quando múltiplos clientes submetem soluções simultaneamente.

### 3.2. Testes e Resultados Encontrados

#### Atividade 1: Calculadora RPC

| Requisito | Status | Descrição |
|:-----------|:--------|:-----------|
| **Operações básicas** | Cumprido | Soma, subtração, multiplicação e divisão implementadas.|
| **Menu interativo** | Cumprido | O cliente permite escolher a operação pelo terminal. |
| **Circuit Breaker** | Cumprido | Evita tentativas de reconexão infinitas. |
| **Comunicação RPC** | Cumprido | Cliente e servidor se comunicam via stubs gRPC. |

#### Atividade 2: Minerador RPC

| Requisito | Status | Descrição |
|:-----------|:--------|:-----------|
| **Estrutura de Dados** | Cumprido | O Servidor mantém a tabela de registros com TransactionID, Challenge, Solution e Winner. O desafio 0 é gerado ao iniciar. |
| **Interface RPC completa** | Cumprido | Todos os métodos solicitados foram implementados (`getTransactionID`, `getChallenge`, `submitChallenge`, etc). |
| **Geração de desafios** | Cumprido | Um novo desafio é criado automaticamente após cada solução válida. |
| **Ciclo de Mineração (Mine)** | Cumprido |O método Mine do cliente executa os 6 passos, desde a busca do desafio até a submissão da solução (passos 1 a 6). |
| **Validação da Prova de Trabalho** | Cumprido | O Servidor valida o hash SHA-1 submetido. O retorno 1 (Solução Válida) é emitido após o registro do ClientID vencedor e a criação do próximo desafio. |
| **Consultas de Estado** | Cumprido | As consultas para transações resolvidas confirmam o registro da Solution e do Winner, e o status da transação é retornado como RESOLVIDA. |


## 4. Vídeo de Demonstração

A execução completa das duas atividades e a validação das funcionalidades principais podem ser vistas no vídeo de demonstração.

**Link para o vídeo:** [adicionar link após a gravação]
