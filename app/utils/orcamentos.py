import pandas as pd
import os
from app.utils.helpers import get_db_connection

## Orcamentos

def salvar_dados_orcamentos(df,part_tipo):
    with get_db_connection() as conn:
        if part_tipo == "Menina":
                df = df.where(pd.notnull(df), None)
                df.to_sql("orcamentos_meninas", conn, if_exists="append", index=False)
        else:
                df = df.where(pd.notnull(df), None)
                df.to_sql("orcamentos_meninos", conn, if_exists="append", index=False)

def deletar_dados_orcamentos(id, part_tipo, part_id=None):
    """
    Deletes budget data from the database and removes associated files.

    Args:
        id (int): ID of the budget to delete.
        part_tipo (str): Type of participant ("Menina" or "Menino").
        part_id (int, optional): Participant ID. If provided, deletes all budgets for the participant.
    """
    # Dynamically determine the base directory of the project
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            if part_id is None:
                table_name = "orcamentos_meninas" if part_tipo == "Menina" else "orcamentos_meninos"
                c.execute(f"SELECT [Contrato Retirada], [Contrato Devolução] FROM {table_name} WHERE id = ?", (id,))
                conn.commit()
                record = c.fetchone()
                if record:
                    contrato_retirada_path, contrato_devolucao_path = record
                    if contrato_retirada_path:
                        full_path = os.path.join(base_dir, contrato_retirada_path)
                        if os.path.exists(full_path):
                            os.remove(full_path)
                    if contrato_devolucao_path:
                        full_path = os.path.join(base_dir, contrato_devolucao_path)
                        if os.path.exists(full_path):
                            os.remove(full_path)
                c.execute(f"DELETE FROM {table_name} WHERE id = ?", (id,))

            # If part_id is provided, delete all budgets for the participant
            else:
                table_name = "orcamentos_meninas" if part_tipo == "Menina" else "orcamentos_meninos"
                c.execute(f"SELECT [Contrato Retirada], [Contrato Devolução] FROM {table_name} WHERE Participante_id = ?", (part_id,))
                conn.commit()
                records = c.fetchall()
                for contrato_retirada_path, contrato_devolucao_path in records:
                    # Delete the files if they exist
                    if contrato_retirada_path:
                        full_path = os.path.join(base_dir, contrato_retirada_path)
                        if os.path.exists(full_path):
                            os.remove(full_path)
                    if contrato_devolucao_path:
                        full_path = os.path.join(base_dir, contrato_devolucao_path)
                        if os.path.exists(full_path):
                            os.remove(full_path)
                # Delete all budget records for the participant from the database
                c.execute(f"DELETE FROM {table_name} WHERE Participante_id = ?", (part_id,))

            # Commit the changes to the database
            conn.commit()

    except Exception as e:
        #print(f"Error in deletar_dados_orcamentos: {e}")
        print("")

def atualizar_dados_orcamentos(df_orcamento_atualizado, tipo_edicao):
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            # Determine the table based on participant type
            table_name = "orcamentos_meninas" if "Busto" in df_orcamento_atualizado.columns else "orcamentos_meninos"
            
            # Update the database
            for _, row in df_orcamento_atualizado.iterrows():
                if tipo_edicao == "Editar Medidas":
                    if table_name == "orcamentos_meninas":
                        c.execute(f"""
                            UPDATE {table_name}
                            SET Busto = ?, Cintura = ?, 
                                `Ombro-Cintura` = ?, `Cintura-Pé` = ?, Modelo = ?, 
                                `Acessórios` = ?, Observação = ?, [Data Retirada] = ?, [Estado Retirada] = ?,
                                [Data Devolução] = ?, [Estado Devolução] = ?, Status = ?
                            WHERE Evento_id = ? AND Participante_id = ?
                        """, (
                            row.get("Busto"), row.get("Cintura"),
                            row.get("Ombro-Cintura"), row.get("Cintura-Pé"), row.get("Modelo"),
                            row.get("Acessórios"), row.get("Observação"), row.get("Data Retirada"),
                            row.get("Estado Retirada"), row.get("Estado Devolução"), row.get("Data Devolução"),
                            row.get("Status"),row.get("Evento_id"), row.get("Participante_id")
                        ))
                    else:
                        c.execute(f"""
                            UPDATE {table_name}
                            SET `Ombro-Punho` = ?, `Bainha-Calça` = ?, Modelo = ?, `Acessórios` = ?, Observação = ?, 
                            [Data Retirada] = ?, [Estado Retirada] = ?, [Data Devolução] = ?, [Estado Devolução] = ?,Status = ?
                            WHERE Evento_id = ? AND Participante_id = ?
                        """, (
                            row.get("Ombro-Punho"), row.get("Bainha-Calça"), row.get("Modelo"),
                            row.get("Acessórios"), row.get("Observação"), row.get("Data Retirada"),
                            row.get("Estado Retirada"), row.get("Estado Devolução"), row.get("Data Devolução"),
                            row.get("Status"), row.get("Evento_id"), row.get("Participante_id")
                        ))    
                elif tipo_edicao == "Editar Orçamento":
                    c.execute(f"""
                        UPDATE {table_name}
                        SET `Valor Total` = ?, `Taxa de Desconto` = ?, `Valor com Desconto` = ?, Status = ?
                        WHERE Evento_id = ? AND Participante_id = ?
                    """, (
                        row.get("Valor Total"), row.get("Taxa de Desconto"), row.get("Valor com Desconto"), row.get("Status"), row.get("Evento_id"), row.get("Participante_id")
                    ))
            conn.commit()
    except Exception as e:
        #print(f"Error updating budget: {e}")
        print("")

def atualizar_dados_orcamentos_pagamentos(meninas_ids=None, meninos_ids=None, tipo_pagamento=None, desconto=None, status=None):
    with get_db_connection() as conn:
        c = conn.cursor()

        # Update `orcamentos_meninas`
        if meninas_ids:
            if isinstance(meninas_ids, list):
                c.executemany(
                    """
                    UPDATE orcamentos_meninas
                    SET Desconto = ?, `Tipo de Pagamento` = ?, Status = ?
                    WHERE id = ?
                    """,
                    [(desconto, tipo_pagamento, status, id) for id in meninas_ids]
                )
            else:
                c.execute(
                    """
                    UPDATE orcamentos_meninas
                    SET Desconto = ?, `Tipo de Pagamento` = ?, Status = ?
                    WHERE id = ?
                    """,
                    (desconto, tipo_pagamento, status, meninas_ids)
                )

        # Update `orcamentos_meninos`
        if meninos_ids:
            if isinstance(meninos_ids, list):
                c.executemany(
                    """
                    UPDATE orcamentos_meninos
                    SET Desconto = ?, `Tipo de Pagamento` = ?, Status = ?
                    WHERE id = ?
                    """,
                    [(desconto, tipo_pagamento, status, id) for id in meninos_ids]
                )
            else:
                c.execute(
                    """
                    UPDATE orcamentos_meninos
                    SET Desconto = ?, `Tipo de Pagamento` = ?, Status = ?
                    WHERE id = ?
                    """,
                    (desconto, tipo_pagamento, status, meninos_ids)
                )

        conn.commit()

def atualizar_orcamentos_pagamentos(orcamento_meninas_ids, orcamento_meninos_ids, status_pagamento):
    """
    Updates the payment information for the given orcamentos.

    Args:
        orcamento_meninas_ids (list): List of IDs for orcamentos_meninas.
        orcamento_meninos_ids (list): List of IDs for orcamentos_meninos.
        status_pagamento (str): Payment status (e.g., "Pagamento Completo" or "Pagamento Parcial").
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    for orcamento_id in orcamento_meninas_ids:
        cursor.execute(f"""
            UPDATE orcamentos_meninas
            SET [Status] = ?
            WHERE id = ?
        """, (status_pagamento, orcamento_id))

    for orcamento_id in orcamento_meninos_ids:
        cursor.execute(f"""
            UPDATE orcamentos_meninos
            SET [Status] = ?
            WHERE id = ?
        """, (status_pagamento, orcamento_id))

    conn.commit()
    conn.close()

def get_eventos(conn):
    """Fetch all events from the database."""
    return pd.read_sql_query("SELECT * FROM eventos", conn)

def get_participantes(conn, evento_id):
    """Fetch all participants for a given event."""
    return pd.read_sql_query(f"SELECT * FROM participantes WHERE Evento_id = {evento_id}", conn)

def get_orcamento(conn, evento_id, participante_id, tipo_participante):
    """Fetch the budget for a given participant and event."""
    table = "orcamentos_meninos" if tipo_participante == "Menino" else "orcamentos_meninas"
    return pd.read_sql_query(f"SELECT * FROM {table} WHERE Evento_id = {evento_id} AND Participante_id = {participante_id}", conn)

def get_orcamentos(evento_id):
    """Fetch the budgets for all participants in a given event."""
    with get_db_connection() as conn:
        return pd.read_sql_query(f"SELECT * FROM orcamentos_meninas WHERE Evento_id = {evento_id}", conn), pd.read_sql_query(f"SELECT * FROM orcamentos_meninos WHERE Evento_id = {evento_id}", conn)

def update_status_multiple_orcamento(evento_id, status, status_value):
    """
    Update the status of all orcamentos for a given evento_id.

    Args:
        evento_id (int): The ID of the event.
        status (str): The column to update.
        status_value (str): The new value to set for the status.
    """
    with get_db_connection() as conn:
        c = conn.cursor()
        # Use parameterized queries to safely update the database
        query_meninas = f"UPDATE orcamentos_meninas SET [{status}] = ? WHERE Evento_id = ?"
        query_meninos = f"UPDATE orcamentos_meninos SET [{status}] = ? WHERE Evento_id = ?"
        c.execute(query_meninas, (status_value, evento_id))
        c.execute(query_meninos, (status_value, evento_id))
        conn.commit()

def get_status_retirada_orcamentos(evento_id):
    """
    Get the status of all orcamentos for a given evento_id.

    Args:
        evento_id (int): The ID of the event.

    Returns:
        list: A list of dictionaries containing the status of each orcamento.
    """
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute(f"SELECT [Status Contrato Retirada] FROM orcamentos_meninas WHERE Evento_id = ?", (evento_id,))
        meninas_status = c.fetchall()
        c.execute(f"SELECT [Status Contrato Retirada] FROM orcamentos_meninos WHERE Evento_id = ?", (evento_id,))
        meninos_status = c.fetchall()

        if meninas_status == "Contrato Assinado" and meninos_status == "Contrato Assinado":
            return 1
        else:
            return 0   
        
def get_orcamentos_param_by_ids(event_ids):
    """
    Retrieves a list of a given parameter (e.g., 'Nome') for a list of event IDs.

    Args:
        event_ids (list): List of event IDs to filter.
        param (str): The column name to retrieve (e.g., 'Nome').

    Returns:
        list: A list of values for the given parameter.
    """
    conn = get_db_connection()
    query = f"SELECT id, Evento_id, Participante_id, [Valor Total], [Valor com Desconto] FROM orcamentos_meninos WHERE Evento_id IN ({','.join(map(str, event_ids))})"
    query2 = f"SELECT id, Evento_id, Participante_id, [Valor Total], [Valor com Desconto] FROM orcamentos_meninas WHERE Evento_id IN ({','.join(map(str, event_ids))})"
    eventos_df = pd.read_sql(query, conn)
    eventos_df2 = pd.read_sql(query2, conn)
    conn.close()

    if "Valor Total" not in eventos_df.columns:
        raise ValueError(f"Parameter 'Valor Total' not found in the 'orcamentos_meninos' table.")
    
    if "Valor com Desconto" not in eventos_df.columns:
        raise ValueError(f"Parameter 'Valor com Desconto' not found in the 'orcamentos_meninos' table.")

    if "Valor Total" not in eventos_df2.columns:
        raise ValueError(f"Parameter 'Valor Total' not found in the 'orcamentos_meninas' table.")
    
    if "Valor com Desconto" not in eventos_df2.columns:
        raise ValueError(f"Parameter 'Valor com Desconto' not found in the 'orcamentos_meninas' table.")
    return eventos_df, eventos_df2          