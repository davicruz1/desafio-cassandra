# Desafio NoSQL: Case FastDelivery com Cassandra & ScyllaDB

Este repositório contém a resolução do desafio de transição do modelo relacional (SQL) para o modelo NoSQL distribuído, focado na otimização de consultas da plataforma FastDelivery.

## 🧠 Parte 1 – Análise do Cenário Atual

1. **Quais consultas exigem muitos JOINs?**
   As consultas que listam os itens de um pedido (dependem de PEDIDOS, ITENS e PRODUTOS) e o histórico de pedidos recentes por cliente.

2. **Quais tabelas podem causar gargalos?**
   As tabelas de `PEDIDOS`, `ITENS_PEDIDO` e `ENTREGAS`, devido ao altíssimo volume de escritas simultâneas e atualizações em tempo real feitas por clientes e entregadores.

3. **Quais consultas exigem baixa latência?**
   Todas as consultas que alimentam o aplicativo mobile em tempo real, como o histórico de pedidos do cliente e a busca de entregas em andamento por cidade.

4. **Quais informações poderiam ser duplicadas?**
   O nome do cliente (na tabela de pedidos) e o nome do produto (na tabela de itens do pedido), evitando a necessidade de JOINs no momento da leitura.

---

## 📐 Parte 2 – Nova Modelagem

Abaixo estão as 3 tabelas criadas no Cassandra, modeladas com foco exclusivo na performance das consultas (Query-First):

### 1. Tabela `pedidos_por_cliente`
* **Consulta atendida:** Consulta 1 (Pedidos recentes de um cliente).
* **Partition Key:** `cliente_id` (distribui os clientes entre os nós do cluster).
* **Clustering Key:** `data_pedido DESC` (garante que os pedidos mais novos apareçam primeiro).
* **Justificativa:** Agrupa todo o histórico de um cliente na mesma partição física, trazendo os dados ordenados por data instantaneamente.

### 2. Tabela `itens_por_pedido`
* **Consulta atendida:** Consulta 2 (Itens de um pedido específico).
* **Partition Key:** `pedido_id` (guarda todos os itens de um mesmo pedido juntos).
* **Clustering Key:** `item_id` (garante a unicidade e ordenação dos itens).
* **Justificativa:** Elimina o JOIN entre tabelas relacionais de itens e produtos, salvando o nome do produto diretamente na linha.

### 3. Tabela `entregas_por_cidade`
* **Consulta atendida:** Consulta 3 (Entregas em andamento por cidade).
* **Partition Key:** `cidade` (separa a carga de dados por município de operação).
* **Clustering Key:** `status_entrega` e `entrega_id`.
* **Justificativa:** Permite buscar de forma performática apenas os registros onde o status seja `em_andamento` para uma determinada região.

---

## 💻 Parte 3 – Implementação (Python)

O script `main.py` presente neste repositório executa de forma automatizada:
1. A criação do Keyspace `fastdelivery`.
2. A criação das 3 tabelas otimizadas.
3. A inserção de dados fictícios simulando a desnormalização.
4. A execução dos `SELECTs` simulando o comportamento do aplicativo.
