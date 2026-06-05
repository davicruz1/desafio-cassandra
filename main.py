from cassandra.cluster import Cluster

# conectando no cluster local (mudar o IP se for rodar em outro lugar)
cluster = Cluster(['127.0.0.1']) 
session = cluster.connect()

# criando o keyspace da fastdelivery (funciona tipo o database/schema do SQL)
session.execute("""
    CREATE KEYSPACE IF NOT EXISTS fastdelivery
    WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
""")
session.set_keyspace('fastdelivery')

# Tabela para a Consulta 1: puxar o histórico de pedidos de um cliente
# a data do pedido entra como clustering key pra ordenar automático do mais novo pro mais antigo
session.execute("""
    CREATE TABLE IF NOT EXISTS pedidos_por_cliente (
        cliente_id int,
        data_pedido timestamp,
        pedido_id int,
        nome_cliente text,
        valor_total decimal,
        status text,
        PRIMARY KEY (cliente_id, data_pedido)
    ) WITH CLUSTERING ORDER BY (data_pedido DESC);
""")

# Tabela para a Consulta 2: listar os itens de um pedido de forma direta
# salvando o nome do produto aqui dentro pra não precisar fazer JOIN depois
session.execute("""
    CREATE TABLE IF NOT EXISTS itens_por_pedido (
        pedido_id int,
        item_id int,
        produto_id int,
        nome_produto text,
        quantidade int,
        valor_unitario decimal,
        PRIMARY KEY (pedido_id, item_id)
    );
""")

# Tabela para a Consulta 3: buscar entregas em andamento filtrando por cidade
session.execute("""
    CREATE TABLE IF NOT EXISTS entregas_por_cidade (
        cidade text,
        status_entrega text,
        entrega_id int,
        pedido_id int,
        entregador text,
        data_saida timestamp,
        PRIMARY KEY (cidade, status_entrega, entrega_id)
    );
""")

# simulando a gravação de um pedido pro cliente 10
session.execute("""
    INSERT INTO pedidos_por_cliente (cliente_id, data_pedido, pedido_id, nome_cliente, valor_total, status)
    VALUES (10, '2026-06-05 12:00:00', 5001, 'João Silva', 150.00, 'ENTREGUE');
""")

# colocando dois itens nesse mesmo pedido (com os nomes dos produtos já duplicados aqui)
session.execute("""
    INSERT INTO itens_por_pedido (pedido_id, item_id, produto_id, nome_produto, quantidade, valor_unitario)
    VALUES (5001, 1, 99, 'Hambúrguer Artesanal', 2, 60.00);
""")
session.execute("""
    INSERT INTO itens_por_pedido (pedido_id, item_id, produto_id, nome_produto, quantidade, valor_unitario)
    VALUES (5001, 2, 88, 'Batata Frita Large', 1, 30.00);
""")

# cadastrando a entrega simulando que ela tá em andamento em SP
session.execute("""
    INSERT INTO entregas_por_cidade (cidade, status_entrega, entrega_id, pedido_id, entregador, data_saida)
    VALUES ('Sao Paulo', 'em_andamento', 7001, 5001, 'Carlos Motoboy', '2026-06-05 12:05:00');
""")

print("--- Consulta 1: Pedidos do Cliente 10 ---")
rows = session.execute("SELECT * FROM pedidos_por_cliente WHERE cliente_id = 10;")
for row in rows:
    print(f"Pedido: {row.pedido_id} - Total: R$ {row.valor_total} - Status: {row.status}")

print("\n--- Consulta 2: Itens do Pedido 5001 ---")
rows = session.execute("SELECT * FROM itens_por_pedido WHERE pedido_id = 5001;")
for row in rows:
    print(f"Item {row.item_id}: {row.nome_produto} x{row.quantidade}")

print("\n--- Consulta 3: Entregas em Andamento em São Paulo ---")
rows = session.execute("SELECT * FROM entregas_por_cidade WHERE cidade = 'Sao Paulo' AND status_entrega = 'em_andamento';")
for row in rows:
    print(f"Entrega {row.entrega_id} com o entregador {row.entregador}")

# fechando as conexões para limpar o processo
session.shutdown()
cluster.shutdown()
