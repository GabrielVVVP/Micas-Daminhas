import pandas as pd
import logging
from app.utils.helpers import get_db_connection

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

## Participantes

def get_participantes():
    with get_db_connection() as conn:
        query = "SELECT * FROM participantes"
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
            c.execute('''UPDATE participantes SET [Evento_id] = ?, [Responsável Financeiro] = ?, [Nome] = ?, [Tipo] = ?, [Telefone] = ?, [Email] = ?, [Endereço] = ?, [CPF] = ?, [Status] = ? WHERE id = ?''', (row['Evento_id'], row['Responsável Financeiro'], row['Nome'], row['Tipo'], row['Telefone'], row['Email'], row['Endereço'], row['CPF'], row['Status'], row['id']))
        conn.commit()

def atualizar_resp_participantes(ids, novo_resp):
    try:
        with get_db_connection() as conn:
            c = conn.cursor()

            # Ensure `ids` is always a list
            if not isinstance(ids, (list, tuple)):
                ids = [ids]

            logging.debug(f"Updating participantes with IDs: {ids} to new responsible: {novo_resp}")
            bindings = [(novo_resp, id) for id in ids]
            c.executemany(
                """
                UPDATE participantes
                SET `Responsável Financeiro` = ?
                WHERE id = ?
                """,
                bindings
            )
            conn.commit()
            logging.info("Participants' financial responsible updated successfully.")
    except Exception as e:
        logging.error(f"Error updating financial responsible: {e}")

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

