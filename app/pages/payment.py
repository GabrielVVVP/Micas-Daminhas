import streamlit as st
import pandas as pd
import datetime as dt
import time
from app.utils.helpers import get_db_connection
from app.utils.orcamentos import atualizar_dados_orcamentos_pagamentos, atualizar_orcamentos_pagamentos
from app.utils.participantes import atualizar_resp_participantes
from app.utils.pagamentos import adicionar_novo_pagamento
from app.utils.eventos import get_clientes, get_clientes_tipo_evento
from app.pages import contracts

def split_payment_among_participants(pagamento, participantes_filtrados):
    """
    Verifies if the pagamento is valid and splits it among participants based on their valor_com_desconto,
    considering their current valor_pago.

    Args:
        pagamento (float): Total payment amount.
        participantes_filtrados (DataFrame): Filtered participants with their respective valor_com_desconto and valor_pago.

    Returns:
        dict: A dictionary mapping participant IDs to their respective payment amounts.
    """
    total_valor_com_desconto = participantes_filtrados["Valor com Desconto"].sum()

    if pagamento > total_valor_com_desconto:
        raise ValueError("Pagamento exceeds the total valor com desconto.")

    pagamentos = {}
    remaining_payment = pagamento

    for _, row in participantes_filtrados.iterrows():
        participante_id = row["id"]
        valor_com_desconto = row["Valor com Desconto"]
        valor_pago_atual = row["Valor Pago"]

        if valor_pago_atual >= valor_com_desconto:
            pagamentos[participante_id] = 0  # No additional payment needed
        else:
            max_payment = valor_com_desconto - valor_pago_atual
            if remaining_payment <= 0:
                pagamentos[participante_id] = 0
            elif remaining_payment >= max_payment:
                pagamentos[participante_id] = max_payment
                remaining_payment -= max_payment
            else:
                pagamentos[participante_id] = remaining_payment
                remaining_payment = 0

    return pagamentos

def payment():

    st.header("Pagamentos")	

    options = st.selectbox("Selecione a Ação", ["Nenhum","Selecionar Responsável Financeiro", "Contratos de Retirada e Devolução", "Realizar Pagamento"])

    if options == "Selecionar Responsável Financeiro":

        # Load data from the database
        conn = get_db_connection()
        clientes = get_clientes(conn) 

        # Update start_date and end_date to use "Data" from eventos
        fallback_date = dt.date.today()
        min_date = pd.to_datetime(clientes["Data"], errors="coerce").min()
        max_date = pd.to_datetime(clientes["Data"], errors="coerce").max()

        # Replace buttons with a select box for date range selection
        date_option = st.selectbox("Selecione o período", ["Dia", "Mês", "Ano", "Seletor de Datas"], index=1)

        if date_option == "Dia":
            start_date = dt.date.today()
            end_date = dt.date.today()
        elif date_option == "Mês":
            start_date = dt.date.today().replace(day=1)
            end_date = (dt.date.today().replace(day=1) + dt.timedelta(days=31)).replace(day=1) - dt.timedelta(days=1)
        elif date_option == "Ano":
            start_date = dt.date.today().replace(month=1, day=1)
            end_date = dt.date.today().replace(month=12, day=31)
        elif date_option == "Seletor de Datas":
            start_date = st.date_input("Data Inicial", value=min_date if pd.notna(min_date) else fallback_date)
            end_date = st.date_input("Data Final", value=max_date if pd.notna(max_date) else fallback_date)

        filtered_clientes = clientes[
            (pd.to_datetime(clientes["Data"], errors="coerce") >= pd.to_datetime(start_date)) &
            (pd.to_datetime(clientes["Data"], errors="coerce") <= pd.to_datetime(end_date))
        ]
        cliente_selecionado = st.selectbox("Selecione o Cliente", filtered_clientes["Nome"] if not filtered_clientes.empty else [])

        if clientes.empty:
            st.warning("Nenhum cliente encontrado.")
        elif filtered_clientes.empty:
            st.warning("Nenhum cliente encontrado para o intervalo de datas selecionado.")

        if cliente_selecionado:
            evento_id = clientes[clientes["Nome"] == cliente_selecionado]["id"].values[0]
            participantes = pd.read_sql_query(f"""
                SELECT p.id, p.Data, p.[Responsável Financeiro], p.Nome, p.Tipo, 
                    COALESCE(om.[Valor Total], 0) + COALESCE(omn.[Valor Total], 0) AS "Valor Total",
                    COALESCE(om.[Desconto], omn.[Desconto]) AS "Desconto (%)",
                    COALESCE(om.[Valor Pago], omn.[Valor Pago]) AS "Valor Pago"                          
                FROM participantes p
                LEFT JOIN orcamentos_meninas om ON p.id = om.Participante_id
                LEFT JOIN orcamentos_meninos omn ON p.id = omn.Participante_id
                WHERE p.Evento_id = {evento_id} AND (om.[Valor Total] IS NOT NULL OR omn.[Valor Total] IS NOT NULL)
            """, conn)

            if not participantes.empty:
                participantes = participantes.convert_dtypes()  # Ensure consistent data types for all columns
                participantes = participantes.fillna('')  # Replace NaN values with empty strings for compatibility

                # Ensure 'Valor Total' and 'Desconto (%)' are numeric before performing calculations
                participantes["Valor Total"] = pd.to_numeric(participantes["Valor Total"], errors="coerce")
                participantes["Desconto (%)"] = pd.to_numeric(participantes["Desconto (%)"], errors="coerce")

                # Drop rows with invalid numeric values to avoid calculation errors
                participantes = participantes.dropna(subset=["Valor Total", "Desconto (%)"])

                # Perform element-wise calculation for 'Valor com Desconto'
                participantes["Valor com Desconto"] = participantes["Valor Total"] * (1 - participantes["Desconto (%)"] / 100)

            if participantes.empty:
                st.warning("Nenhum orçamento encontrado para os participantes deste evento.")

            else: 
                participantes["Selecionar"] = False
                participantes_editor = st.data_editor(participantes, use_container_width=True)

                selected_rows = participantes_editor[participantes_editor["Selecionar"]]

                if not selected_rows.empty:
                    total_sum = selected_rows["Valor Total"].sum()
                    with st.container(border=True):
                        st.markdown(f"###### Total Selecionado: R$ {total_sum:.2f}")
                        desconto = st.number_input("Desconto (%)", min_value=0.0, max_value=100.0, value=0.0)
                        valor_com_desconto = total_sum * (1 - desconto / 100)
                        st.markdown(f"###### Valor com Desconto: R$ {valor_com_desconto:.2f}")
                        tipo_pagamento = st.selectbox("Forma de Pagamento", ["Dinheiro", "Depósito", "Crédito", "Débito"])
                        option_resp = st.selectbox("Selecione o Responsável Financeiro", ["Cliente", "Mãe", "Outro"])
                        if option_resp == "Cliente":    
                            resp_fin = st.text_input("Nome do Responsável Financeiro", value=cliente_selecionado)
                        elif option_resp == "Mãe":
                            resp_fin = st.text_input("Nome da Mãe", value=cliente_selecionado)    
                        else:
                            resp_fin = st.text_input("Nome do Responsável Financeiro")    
                        if st.button("Confirmar Informações de Pagamento"):
                            participantes_ids = selected_rows["id"].tolist()
                            query_meninas = f"""
                                SELECT id FROM orcamentos_meninas WHERE Participante_id IN ({','.join(map(str, participantes_ids))})
                            """
                            query_meninos = f"""
                                SELECT id FROM orcamentos_meninos WHERE Participante_id IN ({','.join(map(str, participantes_ids))})
                            """
                            orcamento_meninas_ids = pd.read_sql_query(query_meninas, conn)["id"].tolist()
                            orcamento_meninos_ids = pd.read_sql_query(query_meninos, conn)["id"].tolist()

                            atualizar_dados_orcamentos_pagamentos(
                                orcamento_meninas_ids,
                                orcamento_meninos_ids,
                                tipo_pagamento,
                                desconto,
                                "Informações de Pagamento Atualizadas"
                            )
                            atualizar_resp_participantes(selected_rows["id"].tolist(), resp_fin)
                            st.success("Informações de Pagamento atualizados com sucesso!")
                            time.sleep(2)
                            st.rerun()

    elif options == "Contratos de Retirada e Devolução":
        contracts.contracts() 
    elif options == "Realizar Pagamento":
        conn = get_db_connection()
        clientes = get_clientes(conn) 
        
        # Update start_date and end_date to use "Data" from eventos
        fallback_date = dt.date.today()
        min_date = pd.to_datetime(clientes["Data"], errors="coerce").min()
        max_date = pd.to_datetime(clientes["Data"], errors="coerce").max()

        # Replace buttons with a select box for date range selection
        date_option = st.selectbox("Selecione o período", ["Dia", "Mês", "Ano", "Seletor de Datas"], index=1)

        if date_option == "Dia":
            start_date = dt.date.today()
            end_date = dt.date.today()
        elif date_option == "Mês":
            start_date = dt.date.today().replace(day=1)
            end_date = (dt.date.today().replace(day=1) + dt.timedelta(days=31)).replace(day=1) - dt.timedelta(days=1)
        elif date_option == "Ano":
            start_date = dt.date.today().replace(month=1, day=1)
            end_date = dt.date.today().replace(month=12, day=31)
        elif date_option == "Seletor de Datas":
            start_date = st.date_input("Data Inicial", value=min_date if pd.notna(min_date) else fallback_date)
            end_date = st.date_input("Data Final", value=max_date if pd.notna(max_date) else fallback_date)


        filtered_clientes = clientes[
            (pd.to_datetime(clientes["Data"], errors="coerce") >= pd.to_datetime(start_date)) &
            (pd.to_datetime(clientes["Data"], errors="coerce") <= pd.to_datetime(end_date))
        ]
        cliente_selecionado = st.selectbox("Selecione o Cliente", filtered_clientes["Nome"] if not filtered_clientes.empty else [])

        if clientes.empty:
            st.warning("Nenhum cliente encontrado.")
        elif filtered_clientes.empty:
            st.warning("Nenhum cliente encontrado para o intervalo de datas selecionado.")

        if cliente_selecionado:
            evento_id = clientes[clientes["Nome"] == cliente_selecionado]["id"].values[0]
            participantes = pd.read_sql_query(f"""
                SELECT p.id, p.Data, p.[Responsável Financeiro], p.Nome, p.Tipo, 
                    COALESCE(om.[Tipo de Pagamento], omn.[Tipo de Pagamento]) AS "Tipo de Pagamento",
                    COALESCE(om.[Valor Total], 0) + COALESCE(omn.[Valor Total], 0) AS "Valor Total",
                    COALESCE(om.[Desconto], omn.[Desconto]) AS "Desconto (%)",
                    COALESCE(om.[Valor Pago], omn.[Valor Pago]) AS "Valor Pago"                          
                FROM participantes p
                LEFT JOIN orcamentos_meninas om ON p.id = om.Participante_id
                LEFT JOIN orcamentos_meninos omn ON p.id = omn.Participante_id
                WHERE p.Evento_id = {evento_id} AND (om.[Valor Total] IS NOT NULL OR omn.[Valor Total] IS NOT NULL)
            """, conn)

            if not participantes.empty:
                participantes = participantes.convert_dtypes()  # Ensure consistent data types for all columns
                participantes = participantes.fillna('')  # Replace NaN values with empty strings for compatibility

                # Ensure 'Valor Total' and 'Desconto (%)' are numeric before performing calculations
                participantes["Valor Total"] = pd.to_numeric(participantes["Valor Total"], errors="coerce")
                participantes["Desconto (%)"] = pd.to_numeric(participantes["Desconto (%)"], errors="coerce")

                # Drop rows with invalid numeric values to avoid calculation errors
                participantes = participantes.dropna(subset=["Valor Total", "Desconto (%)"])

                # Perform element-wise calculation for 'Valor com Desconto'
                participantes["Valor com Desconto"] = participantes["Valor Total"] * (1 - participantes["Desconto (%)"] / 100)

            if participantes.empty:
                st.warning("Nenhum orçamento encontrado para os participantes deste evento.")

            else: 
                # Selectbox for Responsável Financeiro
                responsaveis = participantes["Responsável Financeiro"].dropna().unique()
                responsavel_selecionado = st.selectbox("Selecione o Responsável Financeiro", responsaveis)

                # Filter participantes by selected Responsável Financeiro
                participantes_filtrados = participantes[participantes["Responsável Financeiro"] == responsavel_selecionado]

                # Display filtered participantes in a dataframe
                st.dataframe(participantes_filtrados, use_container_width=True)

                if not participantes_filtrados.empty:
                    total_sum = participantes_filtrados["Valor Total"].sum()
                    discount = participantes_filtrados["Desconto (%)"].iloc[0] if not participantes_filtrados["Desconto (%)"].isnull().all() else 0
                    forma_de_pagamento = participantes_filtrados["Tipo de Pagamento"].iloc[0] if not participantes_filtrados["Tipo de Pagamento"].isnull().all() else "Não Definido"
                    valor_com_desconto = participantes_filtrados["Valor com Desconto"].sum()
                    valor_pago_total = participantes_filtrados["Valor Pago"].sum()
                    valor_remanescente = valor_com_desconto - valor_pago_total
                    with st.container(border=True):
                        st.markdown(f"###### Total Selecionado: R$ {total_sum:.2f}")
                        st.markdown(f"###### Desconto (%): {discount:.2f}")
                        st.markdown(f"###### Valor com Desconto: R$ {valor_com_desconto:.2f}")
                        st.markdown(f"###### Valor Pago Total: R$ {valor_pago_total:.2f}")
                        st.markdown(f"###### Valor Remanescente: R$ {valor_remanescente:.2f}")
                        st.markdown(f"###### Forma de Pagamento: {forma_de_pagamento}")
                        pagamento = st.number_input("Pagamento", min_value=0.0, max_value=valor_remanescente, value=0.0) 
                        if pagamento <= valor_remanescente:  
                            if st.button("Confirmar Pagamento", disabled=(pagamento > valor_remanescente)or(pagamento <= 0)):
                                try:
                                    pagamentos = split_payment_among_participants(pagamento, participantes_filtrados)
                                    for participante_id, valor_pago in pagamentos.items():
                                        query_meninas = f"""
                                            SELECT id FROM orcamentos_meninas WHERE Participante_id = {participante_id}
                                        """
                                        query_meninos = f"""
                                            SELECT id FROM orcamentos_meninos WHERE Participante_id = {participante_id}
                                        """
                                        orcamento_meninas_ids = pd.read_sql_query(query_meninas, conn)["id"].tolist()
                                        orcamento_meninos_ids = pd.read_sql_query(query_meninos, conn)["id"].tolist()

                                        valor_com_desconto = participantes_filtrados.loc[participantes_filtrados["id"] == participante_id, "Valor com Desconto"].iloc[0]
                                        valor_pago_atual = participantes_filtrados.loc[participantes_filtrados["id"] == participante_id, "Valor Pago"].iloc[0]
                                        total_valor_pago = valor_pago + valor_pago_atual

                                        status_pagamento = "Pagamento Completo" if total_valor_pago == valor_com_desconto else "Pagamento Parcial"

                                        atualizar_orcamentos_pagamentos(
                                            orcamento_meninas_ids,
                                            orcamento_meninos_ids,
                                            valor_pago,
                                            status_pagamento
                                        )

                                        # Add payment record to pagamentos_eventos
                                        # Ensure proper indexing and data types before accessing values
                                        participantes_filtrados = participantes_filtrados.reset_index(drop=True)

                                        # Retrieve values using .loc for precise access
                                        orcamento_id = orcamento_meninas_ids[0] if orcamento_meninas_ids else orcamento_meninos_ids[0]
                                        data_evento = participantes_filtrados.loc[participantes_filtrados["id"] == participante_id, "Data"].values[0]
                                        data_pagamento = dt.date.today()
                                        responsavel_financeiro = participantes_filtrados.loc[participantes_filtrados["id"] == participante_id, "Responsável Financeiro"].values[0]
                                        tipo_evento = get_clientes_tipo_evento(evento_id).values[0]
                                        valor_total = participantes_filtrados.loc[participantes_filtrados["id"] == participante_id, "Valor Total"].values[0]
                                        forma_pagamento = forma_de_pagamento
                                        taxa_desconto = participantes_filtrados.loc[participantes_filtrados["id"] == participante_id, "Desconto (%)"].values[0]
                                        valor_restante = valor_com_desconto - total_valor_pago
                                        observacao = ""

                                        adicionar_novo_pagamento(
                                            evento_id,
                                            participante_id,
                                            orcamento_id,
                                            data_evento,
                                            data_pagamento,
                                            responsavel_financeiro,
                                            tipo_evento,
                                            valor_total,
                                            forma_pagamento,
                                            taxa_desconto,
                                            valor_pago,
                                            valor_restante,
                                            observacao,
                                            status_pagamento
                                        )

                                    st.success("Informações de Pagamento atualizadas com sucesso!")
                                    time.sleep(2)
                                    st.rerun()
                                except ValueError as e:
                                    st.error(str(e))   
                            else:
                                st.warning("Valor do pagamento deve ser menor ou igual ao valor remanescente.")         

    else:
        st.info("Selecione uma ação válida.")







