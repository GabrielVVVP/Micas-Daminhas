import pandas as pd
from app.utils.helpers import get_db_connection

def carregar_dados_caixa():
    with get_db_connection() as conn:
        query = "SELECT * FROM caixa"
        df = pd.read_sql_query(query, conn)
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
        return df

def salvar_dados_caixa(df):
    with get_db_connection() as conn:
        df = df.where(pd.notnull(df), None)
        df.to_sql("caixa", conn, if_exists="append", index=False)

def deletar_dados_caixa(ids):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.executemany('DELETE FROM caixa WHERE id = ?', [(id,) for id in ids])
        conn.commit()

def deletar_dados_caixa_id(id):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('DELETE FROM caixa WHERE Participante_id = ?', (id,))
        conn.commit()      

def atualizar_dados_caixa(df):
    with get_db_connection() as conn:
        c = conn.cursor()
        for index, row in df.iterrows():
            data = pd.to_datetime(row['Data']).strftime('%Y-%m-%d %H:%M:%S') if pd.notnull(row['Data']) else None
            c.execute('''UPDATE caixa SET 
                            [Data] = ?,
                            [Origem] = ?, 
                            [Observação] = ?, 
                            [Valor] = ?, 
                            [Operação] = ?
                        WHERE id = ?''', 
                        (data, row['Origem'], row['Observação'], row['Valor'], row['Operação'], row['id']))
        conn.commit()        

def atualizar_dados_caixa_id(df):
    with get_db_connection() as conn:
        c = conn.cursor()
        rows_updated = 0
        for index, row in df.iterrows():
            data = pd.to_datetime(row['Data']).strftime('%Y-%m-%d %H:%M:%S') if pd.notnull(row['Data']) else None
            c.execute('''UPDATE caixa SET 
                            [Data] = ?,
                            [Origem] = ?, 
                            [Observação] = ?, 
                            [Valor] = ?, 
                            [Operação] = ?
                        WHERE Participante_id = ?''', 
                        (data, row['Origem'], row['Observação'], row['Valor'], row['Operação'], row['Participante_id']))
            rows_updated += c.rowcount
        conn.commit()
        if rows_updated == 0:
            return "No entries were updated."
        return None