import pandas as pd
from app.utils.helpers import get_db_connection

# Função para carregar os dados para o banco
def salvar_dados_pagamentos(df):
    with get_db_connection() as conn:
        df.rename(columns={
            "F. pgto": "Forma de Pagamento",
            "Obs.": "Observação",
            "T. Desc": "Taxa de Desconto",
            "VALOR PAGO": "Valor Pago"
        }, inplace=True)
        # Replace NaN and NaT with None
        df = df.where(pd.notnull(df), None)
        df["Valor"] = df["Valor"].astype(float)
        df["Valor Pago"] = df["Valor Pago"].astype(float)
        df.to_sql("pagamentos", conn, if_exists="append", index=False)          

# Função para deletar dados no banco
def deletar_dados(ids):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.executemany('DELETE FROM pagamentos WHERE id = ?', [(id,) for id in ids])
        conn.commit()

# Função para atualizar os dados no banco
def atualizar_dados(df):
    with get_db_connection() as conn:
        c = conn.cursor()
        for index, row in df.iterrows():
            data = pd.to_datetime(row['Data']).strftime('%Y-%m-%d %H:%M:%S') if pd.notnull(row['Data']) else None
            data_casamento = pd.to_datetime(row['Data do Casamento']).strftime('%Y-%m-%d %H:%M:%S') if pd.notnull(row['Data do Casamento']) else None
            c.execute('''UPDATE pagamentos SET 
                            [Data] = ?, 
                            [Noiva] = ?, 
                            [Data do Casamento] = ?, 
                            [Valor] = ?, 
                            [Forma de Pagamento] = ?, 
                            [Observação] = ?, 
                            [Auto] = ?, 
                            [Taxa de Desconto] = ?, 
                            [Valor Pago] = ?, 
                            [Status] = ? 
                        WHERE id = ?''', 
                        (data, row['Noiva'], data_casamento, row['Valor'], row['Forma de Pagamento'], row['Observação'], row['Auto'], row['Taxa de Desconto'], row['Valor Pago'], row['Status'], row['id']))
        conn.commit()

def adicionar_novo_pagamento(evento_id, participante_id, orcamento_id, data_evento, data_pagamento, responsavel_financeiro, tipo_evento, valor_total, forma_pagamento, taxa_desconto, valor_pago, valor_restante, observacao, status):
    """
    Adds a new payment record to the pagamentos_eventos table.

    Args:
        evento_id (str): ID of the event.
        participante_id (str): ID of the participant.
        orcamento_id (str): ID of the budget.
        data_evento (date): Date of the event.
        data_pagamento (date): Date of the payment.
        responsavel_financeiro (str): Financial responsible person.
        tipo_evento (str): Type of the event.
        valor_total (float): Total value.
        forma_pagamento (str): Payment method.
        taxa_desconto (float): Discount rate.
        valor_pago (float): Paid value.
        valor_restante (float): Remaining value.
        observacao (str): Observation.
        status (str): Payment status.
    """
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO pagamentos_eventos (
                [Evento_id], [Participante_id], [Orcamento_id], [Data do Evento], [Data do Pagamento],
                [Responsável Financeiro], [Tipo_Evento], [Valor Total], [Forma de Pagamento],
                [Taxa de Desconto], [Valor Pago], [Valor Restante], [Observação], [Status]
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            evento_id, participante_id, orcamento_id, data_evento, data_pagamento,
            responsavel_financeiro, tipo_evento, valor_total, forma_pagamento,
            taxa_desconto, valor_pago, valor_restante, observacao, status
        ))
        conn.commit()