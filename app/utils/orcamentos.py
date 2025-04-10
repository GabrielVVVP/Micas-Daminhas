import pandas as pd
from app.utils.helpers import get_db_connection

## Orcamentos

def get_orcamentos():
    with get_db_connection() as conn:
        query_1 = "SELECT * FROM orcamentos_meninas"
        df_1 = pd.read_sql_query(query_1, conn)
        query_2 = "SELECT * FROM orcamentos_meninos"
        df_2 = pd.read_sql_query(query_2, conn)
    return df_2

def salvar_dados_orcamentos(df,part_tipo):
    with get_db_connection() as conn:
        if part_tipo == "Menina":
                df = df.where(pd.notnull(df), None)
                df.to_sql("orcamentos_meninas", conn, if_exists="append", index=False)
        else:
                df = df.where(pd.notnull(df), None)
                df.to_sql("orcamentos_meninos", conn, if_exists="append", index=False)

def deletar_dados_orcamentos(id,part_tipo,part_id=None):
    with get_db_connection() as conn:
        if part_id is None:
            if part_tipo == "Menina":
                conn.execute(f"DELETE FROM orcamentos_meninas WHERE id = {id}")
            else:
                conn.execute(f"DELETE FROM orcamentos_meninos WHERE id = {id}")
        else:
            if part_tipo == "Menina":
                conn.execute(f"DELETE FROM orcamentos_meninas WHERE Participante_id = {part_id}")
            else:   
                conn.execute(f"DELETE FROM orcamentos_meninos WHERE Participante_id = {part_id}") 
                   
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
                                `Acessórios` = ?, Observação = ?, Status = ?
                            WHERE Evento_id = ? AND Participante_id = ?
                        """, (
                            row.get("Busto"), row.get("Cintura"),
                            row.get("Ombro-Cintura"), row.get("Cintura-Pé"), row.get("Modelo"),
                            row.get("Acessórios"), row.get("Observação"), row.get("Status"),
                            row.get("Evento_id"), row.get("Participante_id")
                        ))
                    else:
                        c.execute(f"""
                            UPDATE {table_name}
                            SET `Ombro-Punho` = ?, `Bainha-Calça` = ?, Modelo = ?, `Acessórios` = ?, Observação = ?, Status = ?
                            WHERE Evento_id = ? AND Participante_id = ?
                        """, (
                            row.get("Ombro-Punho"), row.get("Bainha-Calça"), row.get("Modelo"),
                            row.get("Acessórios"), row.get("Observação"), row.get("Status"),
                            row.get("Evento_id"), row.get("Participante_id")
                        ))    
                elif tipo_edicao == "Editar Orçamento":
                    c.execute(f"""
                        UPDATE {table_name}
                        SET `Valor Total` = ?, `Valor Pago` = ?, `Tipo de Pagamento` = ?, Status = ?
                        WHERE Evento_id = ? AND Participante_id = ?
                    """, (
                        row.get("Valor Total"), row.get("Valor Pago"), row.get("Tipo de Pagamento"),
                        row.get("Status"), row.get("Evento_id"), row.get("Participante_id")
                    ))
            conn.commit()
    except Exception as e:
        print(f"Error updating budget: {e}")

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

def atualizar_orcamentos_pagamentos(orcamento_meninas_ids, orcamento_meninos_ids, valor_pago, status_pagamento):
    """
    Updates the payment information for the given orcamentos.

    Args:
        orcamento_meninas_ids (list): List of IDs for orcamentos_meninas.
        orcamento_meninos_ids (list): List of IDs for orcamentos_meninos.
        valor_pago (float): Payment amount to add.
        status_pagamento (str): Payment status (e.g., "Pagamento Completo" or "Pagamento Parcial").
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    for orcamento_id in orcamento_meninas_ids:
        cursor.execute(f"""
            UPDATE orcamentos_meninas
            SET [Valor Pago] = [Valor Pago] + ?, [Status] = ?
            WHERE id = ?
        """, (valor_pago, status_pagamento, orcamento_id))

    for orcamento_id in orcamento_meninos_ids:
        cursor.execute(f"""
            UPDATE orcamentos_meninos
            SET [Valor Pago] = [Valor Pago] + ?, [Status] = ?
            WHERE id = ?
        """, (valor_pago, status_pagamento, orcamento_id))

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
