import streamlit as st
import pandas as pd
import datetime as dt
import time
from app.utils.helpers import get_db_connection
from app.utils.orcamentos import get_orcamentos, atualizar_orcamentos_pagamentos
from app.utils.pagamentos import adicionar_novo_pagamento, verificar_pagamento_evento, verificar_pagamento_participantes
from app.utils.eventos import get_clientes, update_client_params

def payment():

    st.header("Pagamentos")	

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
        dados_cliente = clientes[clientes["Nome"] == cliente_selecionado]
        participantes = pd.read_sql_query(f"""
            SELECT p.id, p.Data, p.Nome, p.Tipo, 
                COALESCE(om.[Valor Total], 0) + COALESCE(omn.[Valor Total], 0) AS "Valor Total",
                COALESCE(om.[Taxa de Desconto], 0) + COALESCE(omn.[Taxa de Desconto], 0) AS "Taxa de Desconto",
                COALESCE(om.[Valor com Desconto], 0) + COALESCE(omn.[Valor com Desconto], 0) AS "Valor com Desconto",
                CASE 
                    WHEN om.[Status Contrato Retirada] IS NOT NULL THEN om.[Status Contrato Retirada]
                    WHEN omn.[Status Contrato Retirada] IS NOT NULL THEN omn.[Status Contrato Retirada]
                    ELSE 'Sem Status'
                END AS "Status Contrato Retirada"
            FROM participantes p
            LEFT JOIN orcamentos_meninas om ON p.id = om.Participante_id
            LEFT JOIN orcamentos_meninos omn ON p.id = omn.Participante_id
            WHERE p.Evento_id = {evento_id} AND (om.[Valor Total] IS NOT NULL OR omn.[Valor Total] IS NOT NULL)
        """, conn)
        orcamento_meninas, orcamento_meninos = get_orcamentos(evento_id)

        if participantes.empty:
            st.warning("Nenhum orçamento encontrado para os participantes deste evento.")
        elif any(participantes["Status Contrato Retirada"]!="Contrato Assinado"):
            st.warning("O contrato de retirada de todos os participantes precisam ser assinados para que se possa realizar o pagamento.")    
        else: 
            if dados_cliente["Tipo Pagamento"].values[0] == "Cliente Integral":
                st.markdown("### Orçamentos dos Participantes do Evento")
                st.dataframe(participantes, use_container_width=True)
                participante_id = None
                old_payments = verificar_pagamento_evento(evento_id)
                total_sum = participantes["Valor Total"].sum()
                total_discount = participantes["Valor com Desconto"].sum()
                total_aggregate_discount = (1-(total_discount/total_sum))*100
                st.markdown("### Pagamentos Anteriores deste Evento")
                if old_payments.empty:
                    st.warning("Nenhum pagamento encontrado para este evento.")
                    valor_pago_total = 0
                else: 
                    cum_val_receb = old_payments["Valor Recebido"].cumsum()
                    valor_pago_total = old_payments["Valor Pago"].sum()
                    old_payments["Valor Total"] = participantes["Valor Total"].sum()
                    old_payments["Valor Total Desconto"] = participantes["Valor com Desconto"].sum()
                    old_payments["Valor Restante"] = old_payments["Valor Total Desconto"] - cum_val_receb
                    st.dataframe(old_payments, use_container_width=True)
                    
            else:        
                participante_selecionado = st.selectbox("Selecione o Participante", participantes["Nome"])
                participante_dados = participantes[participantes["Nome"] == participante_selecionado].iloc[0]
                participantes = participante_dados
                participante_id = participante_dados["id"]
                total_sum = participantes["Valor Total"].sum()
                total_discount = participantes["Valor com Desconto"].sum()
                total_aggregate_discount = (1-(total_discount/total_sum))*100
                st.markdown("### Orçamento do Participante do Evento")
                st.dataframe(participantes, use_container_width=True)
                old_payments = verificar_pagamento_participantes(participante_dados["id"])

                st.markdown("### Pagamentos Anteriores deste Participante")
                if old_payments.empty:
                    st.warning("Nenhum pagamento encontrado para este participante.")
                    valor_pago_total = 0.0
                else: 
                    cum_val_receb = old_payments["Valor Recebido"].cumsum()
                    old_payments["Valor Total"] = participantes["Valor Total"].sum()
                    valor_pago_total = old_payments["Valor Pago"].sum()
                    old_payments["Valor Total Desconto"] = participantes["Valor com Desconto"].sum()
                    old_payments["Valor Restante"] = old_payments["Valor Total Desconto"] - cum_val_receb
                    st.dataframe(old_payments, use_container_width=True)
                   
            with st.container(border=True):
                st.markdown("### Novo Pagamento")
                """if dados_cliente["Status"].loc[0] == "Pagamento Completo":
                    st.info("Este evento já foi pago completamente.")
                    return
                else:"""
                #total_sum = old_payments["Valor Total"].sum()
                #total_discount = old_payments["Valor Total Desconto"].sum()
                #if total_sum != 0:
                #    total_aggregate_discount = (1-(total_discount/total_sum))*100
                #else:
                #    total_aggregate_discount = 0.0
                forma_pagamento = st.selectbox("Forma de Pagamento:", ["Dinheiro", "Depósito", "Crédito", "Débito"])
            with st.container(border=True):   
                    valor_total_desc = total_sum - total_discount
                    valor_remanescente = total_discount - valor_pago_total
                    taxa_maquina = 0.0
                    observacao = None
                    st.markdown(f"###### Valor Total Cliente: R$ {total_sum:.2f}")
                    st.markdown(f"###### Desconto Agregado Total (%): {total_aggregate_discount:.2f}")
                    st.markdown(f"###### Desconto Agregado Total: {valor_total_desc:.2f}")
                    st.markdown(f"###### Valor Total Desconto: R$ {total_discount:.2f}")
                    st.markdown(f"###### Valor Pago Total: R$ {valor_pago_total:.2f}")
                    st.markdown(f"###### Valor Remanescente: R$ {valor_remanescente:.2f}")
                    data_do_pagamento = st.date_input("Data do Pagamento")    
                    pagamento = st.number_input("Pagamento", min_value=0.0, max_value=valor_remanescente, value=0.0)
                    valor_recebido = pagamento
                    if forma_pagamento == "Crédito":
                        taxa_maquina = st.number_input("Taxa da Máquina (R$)", min_value=0.0, value=0.0)
                        valor_recebido = pagamento - taxa_maquina
                        st.markdown(f"###### Valor Recebido (Retirando Taxa da Máquina): R$ {valor_recebido:.2f}")
                    if forma_pagamento == "Depósito":
                        observacao = st.date_input("Observação")  
                    if pagamento <= valor_remanescente:  
                        if st.button("Confirmar Pagamento", disabled=(pagamento > valor_remanescente)or(pagamento <= 0)):
                            try:  
                                status_pagamento = "Pagamento Completo" if valor_remanescente == pagamento else "Pagamento Parcial"
                                adicionar_novo_pagamento(
                                    int(evento_id),
                                    int(participante_id) if participante_id else None,
                                    dados_cliente["Data do Evento"].values[0],
                                    data_do_pagamento,
                                    dados_cliente["Tipo Evento"].values[0],
                                    dados_cliente["Tipo Pagamento"].values[0],
                                    forma_pagamento,
                                    taxa_maquina,
                                    valor_recebido,
                                    pagamento,
                                    observacao,
                                    status_pagamento
                                )
                                atualizar_orcamentos_pagamentos(
                                    orcamento_meninas["id"].tolist() if orcamento_meninas is not None else [],
                                    orcamento_meninos["id"].tolist() if orcamento_meninos is not None else [],
                                    status_pagamento
                                )
                                update_client_params(
                                    event_id=int(evento_id),
                                    params={"Status": status_pagamento}
                                )
                                st.success("Informações de Pagamento atualizadas com sucesso!")
                                time.sleep(2)
                                st.rerun()
                            except ValueError as e:
                                st.error(str(e))   
                        else:
                            st.warning("Valor do pagamento deve ser menor ou igual ao valor remanescente.")         









