import pandas as pd
from app.utils.helpers import get_db_connection


## Participantes

def get_participantes():
    with get_db_connection() as conn:
        query = "SELECT * FROM participantes"
        df = pd.read_sql_query(query, conn)
    return df

def get_participantes_event(evento_id):
    with get_db_connection() as conn:
        query = f"SELECT id, Nome, Tipo FROM participantes WHERE Evento_id = {evento_id}"
        df = pd.read_sql_query(query, conn)
    return df

def salvar_dados_participantes(df):
    with get_db_connection() as conn:
        if "Data" not in df.columns or df["Data"].isnull().all():
            df["Data"] = pd.to_datetime("now").date()
        df = df.where(pd.notnull(df), None)
        df.to_sql("participantes", conn, if_exists="append", index=False)

def atualizar_dados_participantes(df):
    with get_db_connection() as conn:
        c = conn.cursor()
        for index, row in df.iterrows():
            c.execute('''UPDATE participantes SET [Evento_id] = ?, [Nome] = ?, [Tipo] = ?, [Telefone] = ?, [Email] = ?, [Endereço] = ?, [CPF] = ?, [Status] = ? WHERE id = ?''', (row['Evento_id'], row['Nome'], row['Tipo'], row['Telefone'], row['Email'], row['Endereço'], row['CPF'], row['Status'], row['id']))
        conn.commit()

def atualizar_status_participante(participante_id, novo_status):
    """
    Updates the status of a participante in the database.

    Args:
        participante_id (int): The ID of the participante to update.
        novo_status (str): The new status to set.
    """
    with get_db_connection() as conn:
        query = "UPDATE participantes SET Status = ? WHERE id = ?"
        conn.execute(query, (novo_status, participante_id))
        conn.commit()

def deletar_dados_participantes(ids):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.executemany('DELETE FROM participantes WHERE id = ?', [(id,) for id in ids])
        conn.commit()

