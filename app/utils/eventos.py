import pandas as pd
from app.utils.helpers import get_db_connection

## Eventos        

def get_clientes(conn):
    return pd.read_sql_query("SELECT * FROM eventos", conn) 

def get_clientes_tipo_evento(id_evento):
    with get_db_connection() as conn:
        return pd.read_sql_query(f"SELECT Tipo_Evento FROM eventos WHERE id = {id_evento}", conn) 

def check_duplicate_event(conn, tipo_evento, nome, data):
    query = """
    SELECT COUNT(*) FROM eventos 
    WHERE Tipo_Evento = ? AND Nome = ? AND Data = ?
    """
    duplicate_count = conn.execute(query, (tipo_evento, nome, data)).fetchone()[0]
    return duplicate_count > 0       

def save_cliente(df):
    with get_db_connection() as conn:
        if "Data" not in df.columns or df["Data"].isnull().all():
            df["Data"] = pd.to_datetime("now").date()
        df = df.where(pd.notnull(df), None)
        df.to_sql("eventos", conn, if_exists="append", index=False) 

def update_cliente(conn, cliente_id, data, nome, telefone, endereco, cpf, tipo_evento):
    query = """
    UPDATE eventos
    SET Data = ?, Nome = ?, Telefone = ?, Endereço = ?, CPF = ?, Tipo_Evento = ?, Status = ?
    WHERE id = ?
    """
    conn.execute(query, (data, nome, telefone, endereco, cpf, tipo_evento, "Cadastro Modificado", cliente_id))
    conn.commit()

def delete_cliente_and_associated_data(cliente_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Check if the table `orcamento_meninos` exists and contains data
        cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='orcamentos_meninos'
        """)
        if cursor.fetchone():
            cursor.execute("DELETE FROM orcamentos_meninos WHERE Evento_id = ?", (cliente_id,))
            print(f"Deleted rows in orcamentos_meninos: {cursor.rowcount}")

        # Check if the table `orcamento_meninas` exists and contains data
        cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='orcamentos_meninas'
        """)
        if cursor.fetchone():
            cursor.execute("DELETE FROM orcamentos_meninas WHERE Evento_id = ?", (cliente_id,))
            print(f"Deleted rows in orcamentos_meninas: {cursor.rowcount}")

        # Check if the table `participantes` exists and contains data
        cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='participantes'
        """)
        if cursor.fetchone():
            cursor.execute("DELETE FROM participantes WHERE Evento_id = ?", (cliente_id,))
            print(f"Deleted rows in participantes: {cursor.rowcount}")

        # Check if the table `eventos` exists and contains data
        cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='eventos'
        """)
        if cursor.fetchone():
            cursor.execute("DELETE FROM eventos WHERE id = ?", (cliente_id,))
            print(f"Deleted rows in eventos: {cursor.rowcount}")

        # Commit the transaction
        conn.commit()
        print(f"Deletion committed for id: {cliente_id}")
        cursor.close()