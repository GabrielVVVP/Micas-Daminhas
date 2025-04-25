import pandas as pd
from app.utils.helpers import get_db_connection

## Eventos        

def get_clientes(conn):
    return pd.read_sql_query("SELECT * FROM eventos", conn) 

def get_clientes_tipo_evento(id_evento):
    with get_db_connection() as conn:
        return pd.read_sql_query(f"SELECT [Tipo Evento] FROM eventos WHERE id = {id_evento}", conn) 

def check_duplicate_event(conn, tipo_evento, nome, data):
    query = """
    SELECT COUNT(*) FROM eventos 
    WHERE [Tipo Evento] = ? AND Nome = ? AND Data = ?
    """
    duplicate_count = conn.execute(query, (tipo_evento, nome, data)).fetchone()[0]
    return duplicate_count > 0       

def save_cliente(df):
    with get_db_connection() as conn:
        if "Data" not in df.columns or df["Data"].isnull().all():
            df["Data"] = pd.to_datetime("now").date()
        df = df.where(pd.notnull(df), None)
        df.to_sql("eventos", conn, if_exists="append", index=False) 

def update_cliente(conn, cliente_id, data, nome, telefone, email, endereco, cpf, tipo_evento, tipo_pagamento):
    query = """
    UPDATE eventos
    SET Data = ?, Nome = ?, Telefone = ?, Email = ?, Endereço = ?, CPF = ?, [Tipo Evento] = ?, [Tipo Pagamento] = ?, Status = ?
    WHERE id = ?
    """
    conn.execute(query, (data, nome, telefone, email, endereco, cpf, tipo_evento, tipo_pagamento, "Cadastro Modificado", cliente_id))
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
            #print(f"Deleted rows in orcamentos_meninos: {cursor.rowcount}")

        # Check if the table `orcamento_meninas` exists and contains data
        cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='orcamentos_meninas'
        """)
        if cursor.fetchone():
            cursor.execute("DELETE FROM orcamentos_meninas WHERE Evento_id = ?", (cliente_id,))
            #print(f"Deleted rows in orcamentos_meninas: {cursor.rowcount}")

        # Check if the table `participantes` exists and contains data
        cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='participantes'
        """)
        if cursor.fetchone():
            cursor.execute("DELETE FROM participantes WHERE Evento_id = ?", (cliente_id,))
            #print(f"Deleted rows in participantes: {cursor.rowcount}")

        # Check if the table `participantes` exists and contains data
        cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='pagamentos_eventos'
        """)
        if cursor.fetchone():
            cursor.execute("DELETE FROM pagamentos_eventos WHERE Evento_id = ?", (cliente_id,))
            #print(f"Deleted rows in pagamentos_eventos: {cursor.rowcount}")    

        # Check if the table `eventos` exists and contains data
        cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='eventos'
        """)
        if cursor.fetchone():
            cursor.execute("DELETE FROM eventos WHERE id = ?", (cliente_id,))
            #print(f"Deleted rows in eventos: {cursor.rowcount}")

        # Commit the transaction
        conn.commit()
        #print(f"Deletion committed for id: {cliente_id}")
        cursor.close()

def get_eventos_param_by_ids(event_ids, param):
    """
    Retrieves a list of a given parameter (e.g., 'Nome') for a list of event IDs.

    Args:
        event_ids (list): List of event IDs to filter.
        param (str): The column name to retrieve (e.g., 'Nome').

    Returns:
        list: A list of values for the given parameter.
    """
    conn = get_db_connection()
    query = f"SELECT id, {param} FROM eventos WHERE id IN ({','.join(map(str, event_ids))})"
    eventos_df = pd.read_sql(query, conn)
    conn.close()

    if param not in eventos_df.columns:
        raise ValueError(f"Parameter '{param}' not found in the 'eventos' table.")

    return eventos_df[param].tolist()    

def update_client_params(event_id, params):
    """
    Updates specific parameters for a given event ID.

    Args:
        event_id (int): The ID of the event to update.
        params (dict): Dictionary of parameters to update with their new values.

    Returns:
        None
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Dynamically build the SET clause based on the keys in the params dictionary
        set_clause = ", ".join([f"{key} = ?" for key in params.keys()])
        values = list(params.values())

        # Add the event_id to the values list for the WHERE clause
        values.append(event_id)

        query = f"""
        UPDATE eventos
        SET {set_clause}
        WHERE id = ?
        """
        cursor.execute(query, values)

        conn.commit()
        cursor.close()  