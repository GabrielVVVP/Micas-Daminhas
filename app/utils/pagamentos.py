import pandas as pd
from app.utils.helpers import get_db_connection

def get_pagamentos_eventos(start_date, end_date):
    """
    Fetch payments for events within the specified date range.

    Args:
        start_date (datetime.date): Start date of the range.
        end_date (datetime.date): End date of the range.

    Returns:
        pd.DataFrame: DataFrame containing payment data.
    """
    conn = get_db_connection()
    query = f"""
        SELECT * 
        FROM pagamentos_eventos
        WHERE "Data do Pagamento" BETWEEN '{start_date}' AND '{end_date}'
    """
    pagamentos_df = pd.read_sql(query, conn)
    conn.close()
    return pagamentos_df

def adicionar_novo_pagamento(evento_id, participante_id, data_evento, data_pagamento, tipo_evento, tipo_pagamento, forma_pagamento, taxa_maquina, valor_recebido, valor_pago, observacao, status):
    """
    Adds a new payment record to the pagamentos_eventos table.

    Args:
        evento_id (str): ID of the event.
        participante_id (str): ID of the participant.
        orcamento_id (str): ID of the budget.
        data_evento (date): Date of the event.
        data_pagamento (date): Date of the payment.
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
                [Evento_id], [Participante_id], [Data do Evento], [Data do Pagamento],
                [Tipo Evento], [Tipo Pagamento], [Forma de Pagamento],
                [Taxa da Máquina], [Valor Recebido],  
                [Valor Pago], [Observação], [Status]
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            evento_id, participante_id, data_evento, data_pagamento,
            tipo_evento, tipo_pagamento, forma_pagamento,
            taxa_maquina, valor_recebido, valor_pago, observacao, status
        ))
        conn.commit()

def verificar_pagamento_evento(evento_id):
    """
    Verifies if a payment record exists for the given event and participant.

    Args:
        evento_id (str): ID of the event.
        participante_id (str): ID of the participant.

    Returns:
        bool: True if the payment record exists, False otherwise.
    """
    with get_db_connection() as conn:
        return pd.read_sql_query(f"SELECT * FROM pagamentos_eventos WHERE Evento_id = {evento_id}", conn)

def verificar_pagamento_participantes(participante_id):
    """
    Verifies if a payment record exists for the given event and participant.

    Args:
        evento_id (str): ID of the event.
        participante_id (str): ID of the participant.

    Returns:
        bool: True if the payment record exists, False otherwise.
    """
    with get_db_connection() as conn:
        return pd.read_sql_query(f"SELECT * FROM pagamentos_eventos WHERE Participante_id = {participante_id}", conn)      

def editar_pagamento(pagamento_id, data_pagamento=None, forma_pagamento=None, taxa_maquina=None, observacao=None, valor_pago=None):
    """
    Edits an existing payment record in the pagamentos_eventos table.

    Args:
        pagamento_id (int): ID of the payment record to edit.
        data_pagamento (date, optional): New payment date.
        forma_pagamento (str, optional): New payment method.
        taxa_maquina (float, optional): New machine fee (only if forma_pagamento is "Crédito" or "Débito").
        observacao (str, optional): New observation (only if forma_pagamento is "Deposito").
        valor_pago (float, optional): New paid value.
    """
    with get_db_connection() as conn:
        c = conn.cursor()

        # Fetch the current payment record
        c.execute("SELECT [Forma de Pagamento], [Taxa da Máquina] FROM pagamentos_eventos WHERE id = ?", (pagamento_id,))
        record = c.fetchone()
        if not record:
            raise ValueError("Payment record not found.")
        
        current_forma_pagamento, current_taxa_maquina = record

        # Update fields based on conditions
        updates = []
        params = []

        if data_pagamento is not None:
            updates.append("[Data do Pagamento] = ?")
            params.append(data_pagamento)

        if forma_pagamento is not None:
            updates.append("[Forma de Pagamento] = ?")
            params.append(forma_pagamento)

        if taxa_maquina is not None:
            if current_forma_pagamento in ["Crédito", "Débito"]:
                updates.append("[Taxa da Máquina] = ?")
                params.append(taxa_maquina)
            else:
                raise ValueError("Taxa da Máquina can only be updated if Forma de Pagamento is 'Crédito' or 'Débito'.")

        if observacao is not None:
            if current_forma_pagamento == "Deposito":
                updates.append("[Observação] = ?")
                params.append(observacao)
            else:
                raise ValueError("Observação can only be updated if Forma de Pagamento is 'Deposito'.")

        if valor_pago is not None:
            #updates.append("[Valor Pago] = ?")
            #params.append(valor_pago)
            # Update valor_recebido based on valor_pago and taxa_maquina
            valor_recebido = valor_pago - (taxa_maquina if taxa_maquina is not None else current_taxa_maquina)
            updates.append("[Valor Recebido] = ?")
            params.append(valor_recebido)

        if updates:
            query = f"UPDATE pagamentos_eventos SET {', '.join(updates)} WHERE id = ?"
            params.append(pagamento_id)
            c.execute(query, tuple(params))
            conn.commit()

def deletar_pagamento(pagamento_id):
    """
    Deletes a payment record from the pagamentos_eventos table.

    Args:
        pagamento_id (int): ID of the payment record to delete.
    """
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM pagamentos_eventos WHERE id = ?", (pagamento_id,))
        conn.commit()    

def mudar_status_pagamento_deletado(pagamento_id):
    """
    Changes the status of the associated event to 'Cliente Modificado' if no other payments exist for the same event.
    Also updates the status of all related orcamentos_meninas and orcamentos_meninos to 'Orçamento Atualizado'.

    Args:
        pagamento_id (int): ID of the payment record to check.
    """
    with get_db_connection() as conn:
        c = conn.cursor()

        # Get the Evento_id associated with the given pagamento_id
        c.execute("SELECT [Evento_id] FROM pagamentos_eventos WHERE id = ?", (pagamento_id,))
        record = c.fetchone()
        if not record:
            raise ValueError("Payment record not found.")
        
        evento_id = record[0]

        # Check if there are other payments for the same Evento_id
        c.execute("SELECT COUNT(*) FROM pagamentos_eventos WHERE [Evento_id] = ? AND id != ?", (evento_id, pagamento_id))
        count = c.fetchone()[0]

        if count == 0:
            # Update the status of the event to 'Cliente Modificado'
            c.execute("UPDATE eventos SET [Status] = 'Cliente Modificado' WHERE id = ?", (evento_id,))
            
            # Update the status of all related orcamentos_meninas to 'Orçamento Atualizado'
            c.execute("UPDATE orcamentos_meninas SET [Status] = 'Orçamento Atualizado' WHERE [Evento_id] = ?", (evento_id,))
            
            # Update the status of all related orcamentos_meninos to 'Orçamento Atualizado'
            c.execute("UPDATE orcamentos_meninos SET [Status] = 'Orçamento Atualizado' WHERE [Evento_id] = ?", (evento_id,))
            
            conn.commit()        
