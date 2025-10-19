# PPD - Laboratório II: Sistema Distribuído RPC (Calculadora e Minerador)

Este projeto implementa um sistema distribuído no modelo **Cliente/Servidor**, utilizando o conceito de **Chamada de Procedimento Remoto (RPC)** com a tecnologia **gRPC** em Python.  
O trabalho foi dividido em duas partes: uma **calculadora distribuída** e um **minerador de criptomoedas com execução concorrente**.

**Aluna:** Sarah Candido Sangi  
**Disciplina:** Programação Paralela e Distribuída (PPD)

---

## 1. Organização do Repositório

O projeto segue o padrão Cliente/Servidor e está dividido em duas pastas principais:

1. **`ATIVIDADE_1_CALCULADORA/`** – Implementação de uma calculadora simples utilizando RPC.  
2. **`ATIVIDADE_2_MINERADOR/`** – Protótipo de mineração de criptomoedas com uso de múltiplas *threads*.

---

## 2. Instruções de Execução

### 2.1. Requisitos

1. Ter o **Python 3.x** instalado (recomendado: 3.10 ou superior).  
2. Instalar as dependências necessárias:
   **Dependências:** Instale as bibliotecas necessárias (`grpcio` e `pybreaker`).
   
    ```bash
    pip install grpcio grpcio-tools pybreaker
    ```

> Obs.: O módulo `pybreaker` é utilizado apenas na calculadora, para controlar falhas de conexão (padrão *Circuit Breaker*).

---

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
---

### 2.3. Execução das Aplicações

É importante iniciar sempre o **servidor** antes do **cliente**.

| Atividade | Servidor | Cliente |
|:-----------|:----------|:----------|
| **Atividade 1** | `python ATIVIDADE_1_CALCULADORA/server.py` | `python ATIVIDADE_1_CALCULADORA/client.py` |
| **Atividade 2** | `python ATIVIDADE_2_MINERADOR/miner_server.py` | `python ATIVIDADE_2_MINERADOR/miner_client.py` |

---

## 3. Relatório Técnico

### Atividade 1: Calculadora RPC

A aplicação da calculadora foi implementada com base no modelo Cliente/Servidor, utilizando o gRPC para comunicação remota entre as funções.

| Requisito | Status | Descrição |
|:-----------|:--------|:-----------|
| **Operações básicas** | Cumprido | Soma, subtração, multiplicação e divisão implementadas.|
| **Menu interativo** | Cumprido | O cliente permite escolher a operação pelo terminal. |
| **Circuit Breaker** | Cumprido | Evita tentativas de reconexão infinitas. |
| **Comunicação RPC** | Cumprido | Cliente e servidor se comunicam via stubs gRPC. |

---

### Atividade 2: Minerador RPC

O projeto cumpre o requisito de construir um protótipo Cliente/Servidor de minerador de criptomoedas em Python/gRPC.

| Requisito | Status | Descrição |
|:-----------|:--------|:-----------|
| **Tabela de transações** | Cumprido | O servidor armazena TransactionID, Challenge, Solution e Winner. |
| **Interface RPC completa** | Cumprido | Todos os métodos solicitados foram implementados (`getTransactionID`, `getChallenge`, `submitChallenge`, etc). |
| **Geração de desafios** | Cumprido | Um novo desafio é criado automaticamente após cada solução válida. |
| **Concorrência no cliente** | Cumprido | O cliente utiliza múltiplas *threads* para tentar encontrar a solução. |
| **Validação do hash** | Cumprido | O servidor verifica se o hash começa com a quantidade exigida de zeros. |
| **Prova de Trabalho (PoW)** | Cumprido | O ciclo completo de mineração, submissão e validação foi reproduzido com sucesso. |


## 4. Vídeo de Demonstração

A execução completa das duas atividades e a validação das funcionalidades principais podem ser vistas no vídeo de demonstração.

**Link para o vídeo:** [adicionar link após a gravação]
